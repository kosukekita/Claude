#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
probe_backend.py — MODEL-AWARE backend probe (the "mandated authority").

gen_video.py shells out to this script as a subprocess and parses the LAST
line of stdout as the backend decision. This script is the single place where
"given THIS model and the CURRENT free VRAM, where should the job run?" is
decided. It is intentionally small, auditable, and stdlib-only (PEP723), so it
can be invoked with `uv run` without installing anything.

WHAT IT KNOWS (model awareness)
-------------------------------
It imports the sibling scripts/models.py to look up the model's VRAM profile:
  - vram_bf16_gb           full-precision single-card peak (incl. text encoder)
  - vram_fp8_gb            fp8 single-card peak (optional; only big models)
  - vram_offload_floor_gb  minimum VRAM with CPU/sequential offload enabled
  - wan_big / moe          flags marking the big Wan A14B MoE checkpoints
  - defer_to_ltx2          LTX-2.3 is not in diffusers; gen_video_ltx2.py runs it
If models.py cannot be imported, a small built-in copy of the canonical matrix
(mirrored from gen_video.py's FALLBACK_MODELS) is used instead — so the probe
NEVER hard-fails just because models.py is missing.

WHAT IT MEASURES (current state)
--------------------------------
Free VRAM per GPU. It first tries the sibling scripts/probe_vram.py (so the two
tools agree on how VRAM is read); if that is unavailable it calls nvidia-smi
directly; if THAT is unavailable it degrades to a cloud/grok decision.

PRIORITY LADDER (decided in EXACTLY this order)
-----------------------------------------------
  1. local-single  — model fits on ONE card at bf16 * margin.
                     precision=bf16, device=cuda:<freest>, offload=False.
                     If it does NOT fit at bf16 but DOES fit at fp8 * margin
                     (model has vram_fp8_gb), still local-single but precision=fp8.
  2. local-offload — freest card (or aggregate free) >= offload_floor * margin.
                     offload=True, precision bf16 (or fp8 if that's all that fits).
  3. local-multi   — ONLY for wan_big models, ONLY when want_quality==quality,
                     AND both GPUs are sufficiently free. multigpu=True.
                     (This tier is a QUALITY upsell, hence it sits below the
                     single-card tiers in the ladder but is checked before cloud.)
  4. cloud-modal   — if MODAL_TOKEN_ID / MODAL_TOKEN_SECRET present.
  5. cloud-fal     — else if FAL_KEY present.
  6. grok          — terminal fallback (delegates to the grok-media skill).

--force <backend> short-circuits to that backend with why="user-forced".
gen_video.py forwards a forced FAMILY (wan|ltx) as --force; those mean "run it
locally", so they resolve through the local ladder (single/offload) just like
auto, but pinned local. --force grok / cloud-modal / cloud-fal / local-* jump
straight to the named tier.

OUTPUT CONTRACT (must match gen_video.py exactly)
-------------------------------------------------
The LAST line of stdout is a single compact JSON object with keys:
  backend   one of: local-single | local-offload | local-multi |
                    cloud-modal | cloud-fal | grok
  device    "cuda:<idx>" for local tiers, null otherwise
  precision "bf16" | "fp8" | null
  offload   bool
  multigpu  bool
  model     repo id (string) | null
  why       human-readable explanation string

Everything else (the human reasoning log) goes to stderr. Exit code is 0 on all
normal paths so the caller can rely on parsing stdout; argument errors exit 2.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROBE_VRAM_PY = SCRIPT_DIR / "probe_vram.py"

# Backends the --force flag accepts. wan/ltx are FAMILY forces meaning "local".
FORCE_CHOICES = [
    "wan", "ltx", "grok",
    "local-single", "local-offload", "local-multi",
    "cloud-modal", "cloud-fal",
]
LOCAL_BACKENDS = {"local-single", "local-offload", "local-multi"}


# --------------------------------------------------------------------------- #
# Conda-pollution guard. Anaconda's libtinfo on this rig breaks spawned
# subprocesses. Scrub conda paths from LD_LIBRARY_PATH before we shell out to
# probe_vram.py / nvidia-smi. (stdlib only; cheap; idempotent.)
# --------------------------------------------------------------------------- #
def _clean_env() -> dict:
    env = os.environ.copy()
    ld = env.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p for p in ld.split(os.pathsep)
            if p and "conda" not in p.lower() and "anaconda" not in p.lower()
        ]
        if kept:
            env["LD_LIBRARY_PATH"] = os.pathsep.join(kept)
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env


def _eprint(*args: object) -> None:
    """Human reasoning log -> stderr; stdout stays pure for the JSON contract."""
    print(*args, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Built-in model matrix (mirror of gen_video.py FALLBACK_MODELS). Used ONLY if
# importing the sibling models.py fails. Keep in sync with that file.
# --------------------------------------------------------------------------- #
_BUILTIN_MODELS: dict[str, dict] = {
    "wan2.1-t2v-1.3b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        "vram_bf16_gb": 13, "vram_offload_floor_gb": 8,
    },
    "wan2.2-ti2v-5b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        "vram_bf16_gb": 28, "vram_offload_floor_gb": 24,
    },
    "wan2.2-t2v-a14b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        "vram_bf16_gb": 80, "vram_fp8_gb": 46, "vram_offload_floor_gb": 40,
        "moe": True, "wan_big": True,
    },
    "wan2.2-i2v-a14b": {
        "task": "i2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-I2V-A14B-Diffusers",
        "vram_bf16_gb": 80, "vram_fp8_gb": 46, "vram_offload_floor_gb": 40,
        "moe": True, "wan_big": True,
    },
    "ltx-video-0.9.8": {
        "task": "t2v", "pipeline": "ltx",
        "repo": "Lightricks/LTX-Video",
        "vram_bf16_gb": 24, "vram_offload_floor_gb": 10,
    },
    "ltx-video-0.9.8-i2v": {
        "task": "i2v", "pipeline": "ltx",
        "repo": "Lightricks/LTX-Video",
        "vram_bf16_gb": 24, "vram_offload_floor_gb": 10,
    },
    "ltx-2.3": {
        "task": "t2v", "pipeline": "ltx2",
        "repo": "Lightricks/LTX-2.3",
        "vram_bf16_gb": 42, "vram_fp8_gb": 20, "vram_offload_floor_gb": 18,
        "defer_to_ltx2": True,
    },
}

# t2i is not a video task; for image generation we don't have a video model
# matrix here. We still answer the probe (so gen_image.py / callers can reuse
# the same authority) using a conservative generic profile.
_GENERIC_T2I = {
    "task": "t2i", "pipeline": "image", "repo": None,
    "vram_bf16_gb": 24, "vram_offload_floor_gb": 8,
}


def load_spec(model_id: str, task: str) -> dict:
    """Resolve a model spec. Prefer sibling models.py; fall back to built-in.

    Returns a dict that always has at least vram_bf16_gb. For t2i with an
    unknown/None model, returns a generic image profile so the probe can still
    pick a tier.
    """
    spec: dict | None = None

    if (SCRIPT_DIR / "models.py").exists():
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            import importlib

            models = importlib.import_module("models")
            importlib.reload(models)
            got = models.get(model_id)  # type: ignore[attr-defined]
            if got:
                spec = dict(got)
                spec.setdefault("pipeline", spec.get("family"))
        except Exception as exc:  # pragma: no cover - defensive
            _eprint(f"[probe_backend] models.py present but unusable ({exc}); "
                    f"using built-in matrix")

    if spec is None and model_id in _BUILTIN_MODELS:
        spec = dict(_BUILTIN_MODELS[model_id])

    if spec is None:
        if task == "t2i":
            _eprint(f"[probe_backend] unknown t2i model '{model_id}'; "
                    f"using generic image VRAM profile")
            spec = dict(_GENERIC_T2I)
            spec["repo"] = model_id if model_id else None
        else:
            known = ", ".join(sorted(_BUILTIN_MODELS))
            _eprint(f"[probe_backend] ERROR: unknown model '{model_id}' "
                    f"(known: {known})")
            raise SystemExit(
                f"Unknown model '{model_id}'. Known: {known}"
            )

    # Normalize the few numeric keys we depend on.
    spec.setdefault("vram_bf16_gb", 9999)
    return spec


# --------------------------------------------------------------------------- #
# VRAM measurement. Prefer the sibling probe_vram.py (single source of truth for
# how VRAM is read); fall back to nvidia-smi directly; fall back to "no GPU".
# Returns a list of per-GPU free GB, freest-first is NOT guaranteed — caller
# keeps indices.
# --------------------------------------------------------------------------- #
def _free_via_probe_vram() -> list[tuple[int, float]] | None:
    """Return [(index, free_gb), ...] using probe_vram.py, or None on failure."""
    if not PROBE_VRAM_PY.exists():
        return None
    uv = shutil.which("uv") or "/home/kita/.local/bin/uv"
    cmd = [uv, "run", str(PROBE_VRAM_PY)]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, env=_clean_env()
        )
    except Exception as exc:
        _eprint(f"[probe_backend] probe_vram.py call failed ({exc})")
        return None
    if res.returncode != 0 or not res.stdout.strip():
        return None
    try:
        data = json.loads(res.stdout.strip().splitlines()[-1])
    except Exception as exc:
        _eprint(f"[probe_backend] could not parse probe_vram.py output ({exc})")
        return None
    if not data.get("nvidia_smi_available"):
        return []  # tool ran but found no usable GPU
    out = []
    for g in data.get("gpus", []):
        try:
            out.append((int(g["index"]), float(g["free_mb"]) / 1024.0))
        except (KeyError, ValueError, TypeError):
            continue
    return out


def _free_via_nvidia_smi() -> list[tuple[int, float]] | None:
    """Direct nvidia-smi fallback. Returns [(index, free_gb)] or None."""
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return None
    cmd = [exe, "--query-gpu=index,memory.free",
           "--format=csv,noheader,nounits"]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15, env=_clean_env()
        )
    except Exception as exc:
        _eprint(f"[probe_backend] nvidia-smi call failed ({exc})")
        return None
    if res.returncode != 0:
        return None
    out = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        try:
            out.append((int(parts[0]), float(parts[1]) / 1024.0))
        except ValueError:
            continue
    return out


def measure_free_vram() -> tuple[list[tuple[int, float]], str]:
    """Return (gpus, source). gpus = [(index, free_gb)] possibly empty."""
    via = _free_via_probe_vram()
    if via is not None:
        return via, "probe_vram.py"
    via = _free_via_nvidia_smi()
    if via is not None:
        return via, "nvidia-smi"
    return [], "none"


# --------------------------------------------------------------------------- #
# Decision builder — emits the EXACT JSON contract.
# --------------------------------------------------------------------------- #
def make_decision(backend: str, *, device: str | None, precision: str | None,
                  offload: bool, multigpu: bool, repo: str | None,
                  why: str) -> dict:
    return {
        "backend": backend,
        "device": device,
        "precision": precision,
        "offload": offload,
        "multigpu": multigpu,
        "model": repo,
        "why": why,
    }


def resolve_cloud_or_grok(repo: str | None, why: list[str]) -> dict:
    if os.environ.get("MODAL_TOKEN_ID") or os.environ.get("MODAL_TOKEN_SECRET"):
        why.append("MODAL creds present -> cloud-modal")
        return make_decision("cloud-modal", device=None, precision=None,
                             offload=False, multigpu=False, repo=repo,
                             why="; ".join(why))
    if os.environ.get("FAL_KEY"):
        why.append("FAL_KEY present -> cloud-fal")
        return make_decision("cloud-fal", device=None, precision=None,
                             offload=False, multigpu=False, repo=repo,
                             why="; ".join(why))
    why.append("no cloud creds -> delegate to grok-media (terminal)")
    return make_decision("grok", device=None, precision=None,
                         offload=False, multigpu=False, repo=repo,
                         why="; ".join(why))


def forced_decision(force: str, spec: dict, gpus: list[tuple[int, float]]) -> dict:
    """--force short-circuit. why is always 'user-forced' (+ context)."""
    repo = spec.get("repo")
    freest_idx = max(gpus, key=lambda g: g[1])[0] if gpus else 0
    device = f"cuda:{freest_idx}" if gpus else "cuda:0"
    has_fp8 = "vram_fp8_gb" in spec
    note = _ltx2_note(spec)

    # Family forces (wan/ltx) mean "run locally" -> resolve through local ladder.
    if force in {"wan", "ltx"}:
        why = [f"user-forced family={force} (local)"]
        return local_ladder(spec, gpus, want_quality="quality",
                            margin=1.1, pin_local=True, why=why) \
            or resolve_cloud_or_grok(repo, why)

    if force == "grok":
        return make_decision("grok", device=None, precision=None, offload=False,
                             multigpu=False, repo=repo,
                             why="user-forced" + note)
    if force == "cloud-modal":
        return make_decision("cloud-modal", device=None, precision=None,
                             offload=False, multigpu=False, repo=repo,
                             why="user-forced" + note)
    if force == "cloud-fal":
        return make_decision("cloud-fal", device=None, precision=None,
                             offload=False, multigpu=False, repo=repo,
                             why="user-forced" + note)
    if force == "local-single":
        prec = "fp8" if has_fp8 else "bf16"
        return make_decision("local-single", device=device, precision=prec,
                             offload=False, multigpu=False, repo=repo,
                             why="user-forced" + note)
    if force == "local-offload":
        prec = "fp8" if has_fp8 else "bf16"
        return make_decision("local-offload", device=device, precision=prec,
                             offload=True, multigpu=False, repo=repo,
                             why="user-forced" + note)
    if force == "local-multi":
        return make_decision("local-multi", device=device, precision="bf16",
                             offload=False, multigpu=True, repo=repo,
                             why="user-forced" + note)
    # Should be unreachable (argparse restricts choices).
    raise SystemExit(f"unknown --force value: {force}")


def _ltx2_note(spec: dict) -> str:
    if spec.get("defer_to_ltx2") or spec.get("pipeline") == "ltx2":
        return " (note: gen_video_ltx2.py handles execution for ltx-2.3)"
    return ""


# --------------------------------------------------------------------------- #
# The local ladder, in evaluation order:
#   local-single (bf16) > local-single (fp8) > local-multi (wan_big+quality+2 GPUs)
#   > local-offload. Returns a decision dict, or None if nothing local fits.
# --------------------------------------------------------------------------- #
def local_ladder(spec: dict, gpus: list[tuple[int, float]], *,
                 want_quality: str, margin: float, pin_local: bool,
                 why: list[str]) -> dict | None:
    if not gpus:
        why.append("no GPU detected")
        return None

    repo = spec.get("repo")
    note = _ltx2_note(spec)

    # Sort freest-first; freest is the primary device for single/offload.
    gpus_sorted = sorted(gpus, key=lambda g: g[1], reverse=True)
    freest_idx, freest_free = gpus_sorted[0]
    device = f"cuda:{freest_idx}"
    total_free = sum(f for _, f in gpus_sorted)

    bf16 = spec.get("vram_bf16_gb", 9999)
    fp8 = spec.get("vram_fp8_gb")  # may be None
    floor = spec.get("vram_offload_floor_gb", bf16)
    is_wan_big = bool(spec.get("wan_big"))
    is_wan_pipe = spec.get("pipeline") == "wan"

    why.append(
        f"freest GPU{freest_idx}={freest_free:.1f}GB free, total={total_free:.1f}GB; "
        f"need bf16~{bf16}GB"
        + (f" / fp8~{fp8}GB" if fp8 else "")
        + f" / offload_floor~{floor}GB; margin x{margin}"
    )

    # 1a. local-single at bf16.
    if freest_free >= bf16 * margin:
        why.append(f"fits one card at bf16 ({bf16}x{margin}<= {freest_free:.1f})")
        return make_decision("local-single", device=device, precision="bf16",
                             offload=False, multigpu=False, repo=repo,
                             why="; ".join(why) + note)

    # 1b. local-single at fp8 (only if model exposes an fp8 profile).
    if fp8 is not None and freest_free >= fp8 * margin:
        why.append(f"does not fit bf16, but fits one card at fp8 "
                   f"({fp8}x{margin}<= {freest_free:.1f})")
        return make_decision("local-single", device=device, precision="fp8",
                             offload=False, multigpu=False, repo=repo,
                             why="; ".join(why) + note)

    # 2. local-multi: deliberate QUALITY upsell. ONLY big Wan + want-quality +
    #    both GPUs sufficiently free ("sufficiently free" = at least two cards
    #    each clearing the offload floor, so the model can actually be sharded
    #    across them). Checked BEFORE local-offload: on a 2x48GB rig a big-Wan
    #    job always clears the single-card offload floor at fp8, so if we tested
    #    offload first the multi tier would be unreachable. This mirrors
    #    gen_video.py's builtin_select, which checks multi before single/offload
    #    inside its "fits natively" branch. (If the model fit cleanly on ONE
    #    whole card it would already have returned local-single above, so multi
    #    only fires when one card is NOT enough but two together are.)
    if is_wan_big and is_wan_pipe and want_quality == "quality":
        sufficiently_free = [f for _, f in gpus_sorted if f >= floor * margin]
        if len(sufficiently_free) >= 2:
            why.append(
                f"wan_big + want-quality + {len(sufficiently_free)} GPUs each "
                f">= {floor}x{margin}GB -> multi-GPU"
            )
            return make_decision("local-multi", device=device, precision="bf16",
                                 offload=False, multigpu=True, repo=repo,
                                 why="; ".join(why) + note)

    # 3. local-offload: freest card OR aggregate free clears the offload floor.
    fits_offload = (freest_free >= floor * margin) or (total_free >= floor * margin)
    if fits_offload:
        # Precision under offload: keep fp8 if the model only has an fp8 profile
        # at this size, else bf16 (offload trades RAM/CPU for VRAM headroom).
        prec = "fp8" if (fp8 is not None and freest_free < bf16 * margin
                         and freest_free < fp8 * margin) else "bf16"
        why.append(f"fits with offload (floor {floor}GB) on {device}, "
                   f"precision={prec}")
        return make_decision("local-offload", device=device, precision=prec,
                             offload=True, multigpu=False, repo=repo,
                             why="; ".join(why) + note)

    if pin_local:
        # Family was forced local but nothing fits cleanly: best-effort offload
        # on the freest card rather than bailing to cloud.
        why.append("forced local but VRAM tight -> best-effort offload")
        return make_decision("local-offload", device=device, precision="bf16",
                             offload=True, multigpu=False, repo=repo,
                             why="; ".join(why) + note)

    why.append("no local tier fits")
    return None


def select(spec: dict, gpus: list[tuple[int, float]], *, want_quality: str,
           margin: float, source: str) -> dict:
    why = [f"vram source={source}"]
    if not gpus:
        why.append("no usable local GPU")
        return resolve_cloud_or_grok(spec.get("repo"), why)

    local = local_ladder(spec, gpus, want_quality=want_quality, margin=margin,
                         pin_local=False, why=why)
    if local is not None:
        return local
    return resolve_cloud_or_grok(spec.get("repo"), why)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="probe_backend.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "MODEL-AWARE backend probe — the mandated authority gen_video.py "
            "calls to decide WHERE a generation job runs.\n\n"
            "It looks up the model's VRAM profile (sibling models.py, or a "
            "built-in copy), measures free VRAM (sibling probe_vram.py, or "
            "nvidia-smi), and picks a backend by this priority:\n"
            "  local-single (bf16, freest card)            best\n"
            "  local-single (fp8, if bf16 won't fit)\n"
            "  local-offload (>= offload_floor, offload=on)\n"
            "  local-multi (wan_big + --want-quality quality + both GPUs free)\n"
            "  cloud-modal (MODAL_TOKEN_ID/SECRET set)\n"
            "  cloud-fal   (FAL_KEY set)\n"
            "  grok        (terminal fallback -> grok-media skill)\n\n"
            "The decision JSON is printed as the LAST line of stdout; a human "
            "reasoning log goes to stderr. Robust to missing nvidia-smi. "
            "stdlib-only (PEP723)."
        ),
        epilog=(
            "JSON contract (last stdout line):\n"
            "  {backend, device, precision, offload, multigpu, model, why}\n\n"
            "Examples:\n"
            "  probe_backend.py --task t2v --model wan2.1-t2v-1.3b --json\n"
            "  probe_backend.py --task i2v --model wan2.2-i2v-a14b "
            "--want-quality quality --json\n"
            "  probe_backend.py --task t2v --model ltx-2.3 --json\n"
            "  probe_backend.py --task t2v --model wan2.2-t2v-a14b "
            "--force cloud-fal --json\n"
        ),
    )
    p.add_argument("--task", required=True, choices=["t2v", "i2v", "t2i"],
                   help="Generation task: text->video, image->video, text->image.")
    p.add_argument("--model", required=True,
                   help="Model id (e.g. wan2.1-t2v-1.3b) or, for t2i, a repo id.")
    p.add_argument("--want-quality", default="fast", choices=["fast", "quality"],
                   help="'quality' unlocks the local-multi tier for big Wan "
                        "models (default: fast).")
    p.add_argument("--margin", type=float, default=1.1, metavar="F",
                   help="Safety multiplier on the model's VRAM needs to guard "
                        "against activation/text-encoder spikes (default: 1.1).")
    p.add_argument("--json", action="store_true",
                   help="Emit the decision JSON (the LAST stdout line). This is "
                        "what gen_video.py reads; included for an explicit "
                        "contract even though JSON is always printed.")
    p.add_argument("--force", choices=FORCE_CHOICES, default=None,
                   help="Short-circuit to a specific backend with "
                        "why='user-forced'. wan/ltx force LOCAL execution "
                        "(resolved through the local ladder).")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.margin <= 0:
        build_parser().error("--margin must be > 0")

    spec = load_spec(args.model, args.task)
    repo = spec.get("repo")

    _eprint(f"[probe_backend] task={args.task} model={args.model} "
            f"repo={repo} want_quality={args.want_quality} "
            f"margin={args.margin}"
            + (f" force={args.force}" if args.force else ""))
    _eprint(f"[probe_backend] VRAM profile: bf16={spec.get('vram_bf16_gb')}GB "
            f"fp8={spec.get('vram_fp8_gb')} "
            f"offload_floor={spec.get('vram_offload_floor_gb')}GB "
            f"wan_big={bool(spec.get('wan_big'))} "
            f"defer_to_ltx2={bool(spec.get('defer_to_ltx2'))}")

    gpus, source = measure_free_vram()
    if gpus:
        for idx, free in sorted(gpus):
            _eprint(f"  GPU {idx}: {free:.1f} GB free  (via {source})")
    else:
        _eprint(f"[probe_backend] no usable local GPU (vram source={source})")

    if args.force:
        decision = forced_decision(args.force, spec, gpus)
    else:
        decision = select(spec, gpus, want_quality=args.want_quality,
                          margin=args.margin, source=source)

    _eprint(f"[probe_backend] DECISION: backend={decision['backend']} "
            f"device={decision['device']} precision={decision['precision']} "
            f"offload={decision['offload']} multigpu={decision['multigpu']}")
    _eprint(f"[probe_backend] why: {decision['why']}")

    # The decision JSON MUST be the LAST line of stdout (gen_video.py reads it).
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
