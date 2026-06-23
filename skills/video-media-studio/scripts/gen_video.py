#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers.git",
#   "transformers>=4.51.3",
#   "accelerate",
#   "ftfy",
#   "imageio",
#   "imageio-ffmpeg",
#   "sentencepiece",
#   "protobuf",
#   "numpy",
#   "pillow",
# ]
#
# # Pin torch to the CUDA 12.1 build: this rig's NVIDIA driver is CUDA 12.2
# # (12020); default PyPI torch wheels target a newer CUDA runtime and fail with
# # "driver is too old". cu121 wheels run fine on 12.2. See reference/setup.md.
# [tool.uv.sources]
# torch = { index = "pytorch-cu121" }
#
# [[tool.uv.index]]
# name = "pytorch-cu121"
# url = "https://download.pytorch.org/whl/cu121"
# explicit = true
# ///
"""
generate_video.py — unified video-generation entrypoint for the
`video-media-studio` skill.

CLI: --backend [auto|wan|ltx|grok], --task [t2v|i2v], --prompt, --image (i2v),
--out, plus --model / --width / --height / --num-frames / --fps / --steps /
--guidance / --negative-prompt / --seed / --offload / --want-quality / --margin.

Local-GPU-FIRST. When --backend auto, it runs the VRAM-probe logic (delegating
to the sibling scripts/probe_backend.py + scripts/models.py when present, else a
built-in fallback) and picks:

    local-single  -> run the diffusers pipeline on one GPU (fastest default)
    local-offload -> same, with enable_model_cpu_offload() / fp8 cast
    local-multi   -> print the OFFICIAL Wan torchrun command (diffusers can't
                     shard one clip; we don't fake it)
    cloud-modal / cloud-fal -> point at scripts/cloud_modal.py / cloud_fal.py
    grok          -> print EXACT instructions to use the grok-media skill
                     (we never re-implement Grok here)

Local Wan runs via Wan{,ImageToVideo}Pipeline, LTX-Video runs via
LTX{,ImageToVideo}Pipeline, both inside a CLEAN environment (anaconda's
libtinfo.so.6 pollutes LD_LIBRARY_PATH and has broken subprocesses before — we
strip it / re-exec through scripts/env.sh) with device placement / offload for
the chosen tier, VAE forced to fp32, and the mp4 written to --out.

Run with --help for the full option list. PEP723 inline deps are resolved by uv.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

# --------------------------------------------------------------------------- #
# Locations / sibling scripts
# --------------------------------------------------------------------------- #
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ENV_SH = SCRIPT_DIR / "env.sh"
PROBE_PY = SCRIPT_DIR / "probe_backend.py"
MODELS_PY = SCRIPT_DIR / "models.py"
GEN_LTX2_PY = SCRIPT_DIR / "gen_video_ltx2.py"
CLOUD_MODAL_PY = SCRIPT_DIR / "cloud_modal.py"
CLOUD_FAL_PY = SCRIPT_DIR / "cloud_fal.py"
UV = os.environ.get("UV") or shutil.which("uv") or "/home/kita/.local/bin/uv"


def log(msg: str) -> None:
    print(f"[generate_video] {msg}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Clean environment (strip the anaconda libtinfo LD_LIBRARY_PATH pollution)
# --------------------------------------------------------------------------- #
def clean_ld_environment() -> None:
    """Remove anaconda-polluted entries from LD_LIBRARY_PATH in THIS process.

    anaconda ships a libtinfo.so.6 that emits 'no version information available'
    and has broken soffice / subprocesses before. We are about to import torch,
    so scrub the in-process env. The skill's scripts/env.sh does the same for
    shelled-out ffmpeg/torchrun calls; we mirror it here for the python path.
    """
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p
            for p in ld.split(os.pathsep)
            if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p
        ]
        new = os.pathsep.join(kept)
        if new:
            os.environ["LD_LIBRARY_PATH"] = new
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
        if new != ld:
            log(f"scrubbed conda paths from LD_LIBRARY_PATH (was {len(ld)} chars)")
    # Reduce CUDA fragmentation for the big two-expert / 22B loads.
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    # Keep the HF cache on the big disk if env.sh hasn't already.
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")


# --------------------------------------------------------------------------- #
# Model matrix — built-in fallback mirror of scripts/models.py
# (probe_backend.py / models.py are the single source of truth when present)
# --------------------------------------------------------------------------- #
# task: t2v | i2v ; pipeline: wan | ltx (which diffusers family) ; ltx2 => defer
# vram_*_gb are per-clip single-card peaks INCLUDING text encoder spikes.
FALLBACK_MODELS: dict[str, dict] = {
    # --- Wan (diffusers) ---
    "wan2.1-t2v-1.3b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        "vram_bf16_gb": 13, "vram_offload_floor_gb": 8,
        "frame_rule": (4, 1), "dim_multiple": 16,
        "default_steps": 40, "default_guidance": 5.0, "default_fps": 16,
        "default_w": 832, "default_h": 480, "vae_fp32": True,
        "fal_id": "fal-ai/wan/v2.2-5b/text-to-video",
    },
    "wan2.2-ti2v-5b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        "vram_bf16_gb": 28, "vram_offload_floor_gb": 24,
        "frame_rule": (4, 1), "dim_multiple": 16,
        "default_steps": 40, "default_guidance": 5.0, "default_fps": 24,
        "default_w": 1280, "default_h": 704, "vae_fp32": True,
        "fal_id": "fal-ai/wan/v2.2-5b/text-to-video",
    },
    "wan2.2-t2v-a14b": {
        "task": "t2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        "vram_bf16_gb": 80, "vram_fp8_gb": 46, "vram_offload_floor_gb": 40,
        "frame_rule": (4, 1), "dim_multiple": 16,
        "default_steps": 40, "default_guidance": 3.5, "default_fps": 16,
        "default_w": 1280, "default_h": 720, "vae_fp32": True,
        "moe": True, "wan_big": True,
        "fal_id": "fal-ai/wan/v2.2-a14b/text-to-video",
    },
    "wan2.2-i2v-a14b": {
        "task": "i2v", "pipeline": "wan",
        "repo": "Wan-AI/Wan2.2-I2V-A14B-Diffusers",
        "vram_bf16_gb": 80, "vram_fp8_gb": 46, "vram_offload_floor_gb": 40,
        "frame_rule": (4, 1), "dim_multiple": 16,
        "default_steps": 40, "default_guidance": 3.5, "default_fps": 16,
        "default_w": 1280, "default_h": 720, "vae_fp32": True,
        "moe": True, "wan_big": True,
        "fal_id": "fal-ai/wan/v2.2-a14b/image-to-video",
    },
    # --- LTX-Video 0.9.x (diffusers) ---
    "ltx-video-0.9.8": {
        "task": "t2v", "pipeline": "ltx",
        "repo": "Lightricks/LTX-Video",
        "vram_bf16_gb": 24, "vram_offload_floor_gb": 10,
        "frame_rule": (8, 1), "dim_multiple": 32,
        "default_steps": 50, "default_guidance": 3.0, "default_fps": 24,
        "default_w": 768, "default_h": 512, "vae_fp32": True,
        "decode_timestep": 0.03, "decode_noise_scale": 0.025,
        "fal_id": "fal-ai/ltx-2.3/text-to-video",
    },
    "ltx-video-0.9.8-i2v": {
        "task": "i2v", "pipeline": "ltx",
        "repo": "Lightricks/LTX-Video",
        "vram_bf16_gb": 24, "vram_offload_floor_gb": 10,
        "frame_rule": (8, 1), "dim_multiple": 32,
        "default_steps": 50, "default_guidance": 3.0, "default_fps": 24,
        "default_w": 768, "default_h": 512, "vae_fp32": True,
        "decode_timestep": 0.03, "decode_noise_scale": 0.025,
        "fal_id": "fal-ai/ltx-2.3/image-to-video",
    },
    # --- LTX-2.3 (NOT in diffusers; defer to gen_video_ltx2.py) ---
    "ltx-2.3": {
        "task": "t2v", "pipeline": "ltx2",
        "repo": "Lightricks/LTX-2.3",
        "vram_bf16_gb": 42, "vram_fp8_gb": 20, "vram_offload_floor_gb": 18,
        "frame_rule": (8, 1), "dim_multiple": 32,
        "default_steps": 40, "default_guidance": 3.0, "default_fps": 25,
        "default_w": 768, "default_h": 512, "vae_fp32": True,
        "defer_to_ltx2": True,
        "fal_id": "fal-ai/ltx-2.3/text-to-video",
    },
}

DEFAULT_MODEL_FOR_TASK = {
    "t2v": "wan2.1-t2v-1.3b",     # fast, fits trivially, good iteration default
    "i2v": "wan2.2-i2v-a14b",     # quality default; on 48GB use fp8/offload
}


def load_model_spec(model_id: str) -> dict:
    """Prefer the authoritative scripts/models.py; fall back to the built-in."""
    if MODELS_PY.exists():
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            import importlib

            models = importlib.import_module("models")
            importlib.reload(models)
            spec = models.get(model_id)  # type: ignore[attr-defined]
            if spec:
                # Normalize a couple of keys we rely on, tolerating naming drift.
                spec = dict(spec)
                spec.setdefault("pipeline", spec.get("family"))
                return spec
        except Exception as exc:  # pragma: no cover - defensive
            log(f"models.py present but unusable ({exc}); using built-in matrix")
    if model_id in FALLBACK_MODELS:
        return dict(FALLBACK_MODELS[model_id])
    raise SystemExit(
        f"Unknown model '{model_id}'. Known: {', '.join(sorted(FALLBACK_MODELS))}\n"
        f"(or add it to {MODELS_PY})"
    )


# --------------------------------------------------------------------------- #
# VRAM probe / backend selection
# --------------------------------------------------------------------------- #
def free_vram_per_gpu_gb() -> list[float]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL,
        )
        return [float(x.strip()) / 1024.0 for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def run_external_probe(task: str, model: str, want_quality: str,
                       margin: float, force: str | None) -> dict | None:
    """Use scripts/probe_backend.py if it exists (it is the mandated authority)."""
    if not PROBE_PY.exists():
        return None
    cmd = [UV, "run", str(PROBE_PY), "--task", task, "--model", model,
           "--want-quality", want_quality, "--margin", str(margin), "--json"]
    if force:
        cmd += ["--force", force]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        if res.stderr:
            sys.stderr.write(res.stderr)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout.strip().splitlines()[-1])
    except Exception as exc:
        log(f"probe_backend.py failed ({exc}); using built-in selection")
    return None


def builtin_select(task: str, model: str, spec: dict, want_quality: str,
                   margin: float, force: str | None,
                   force_offload: bool) -> dict:
    """Fallback flowchart, mirroring scripts/probe_backend.py priority ladder."""
    why: list[str] = []

    if force in {"wan", "ltx", "local"}:
        why.append("user forced local")
        return _decision("local-single", spec, why, offload=force_offload)
    if force == "grok":
        return _decision("grok", spec, ["user forced grok"])
    if force in {"cloud-modal", "cloud", "cloud-fal"}:
        b = "cloud-fal" if force == "cloud-fal" else "cloud-modal"
        return _decision(b, spec, [f"user forced {b}"])

    free = free_vram_per_gpu_gb()
    if not free:
        why.append("no nvidia-smi / no GPU detected")
        return _resolve_cloud_or_grok(spec, why)

    free0 = free[0]
    both_idle = len(free) >= 2 and all(f >= 40 for f in free[:2])
    need_native = spec.get("vram_fp8_gb", spec.get("vram_bf16_gb", 9999))
    floor = spec.get("vram_offload_floor_gb", need_native)
    why.append(f"free GPU0={free0:.1f}GB ; need~{need_native}GB x{margin}")

    if free0 >= need_native * margin:
        if (spec.get("wan_big") and want_quality == "quality"
                and both_idle and spec.get("pipeline") == "wan"):
            why.append("big Wan + want-quality + both GPUs idle -> multi-GPU")
            return _decision("local-multi", spec, why)
        why.append("fits one card natively")
        return _decision("local-single", spec, why,
                         offload=force_offload,
                         precision="fp8" if "vram_fp8_gb" in spec else "bf16")
    if free0 >= floor * margin:
        why.append(f"fits with offload (floor {floor}GB)")
        return _decision("local-offload", spec, why, offload=True)

    why.append("VRAM insufficient even with offload")
    return _resolve_cloud_or_grok(spec, why)


def _resolve_cloud_or_grok(spec: dict, why: list[str]) -> dict:
    if os.environ.get("MODAL_TOKEN_ID") or os.environ.get("MODAL_TOKEN_SECRET"):
        why.append("MODAL creds present -> cloud-modal")
        return _decision("cloud-modal", spec, why)
    if os.environ.get("FAL_KEY"):
        why.append("FAL_KEY present -> cloud-fal")
        return _decision("cloud-fal", spec, why)
    why.append("no cloud creds -> delegate to grok-media")
    return _decision("grok", spec, why)


def _decision(backend: str, spec: dict, why: list[str], *,
              offload: bool = False, precision: str = "bf16") -> dict:
    return {
        "backend": backend,
        "device": "cuda:0",
        "precision": precision,
        "offload": offload,
        "multigpu": backend == "local-multi",
        "model": spec.get("repo"),
        "why": "; ".join(why),
    }


def _force_single_offload(ext: dict, spec: dict) -> dict:
    """When the user passes --offload, never route to local-multi (which only
    prints torchrun instructions and does NOT generate). Collapse any local
    decision to single-GPU diffusers offload so the clip actually renders."""
    ext = dict(ext)
    ext["backend"] = "local-offload"
    ext["multigpu"] = False
    ext["offload"] = True
    ext.setdefault("device", "cuda:0")
    if spec.get("vram_fp8_gb"):
        ext["precision"] = "fp8"
    ext["why"] = "user --offload -> forced single-GPU diffusers offload " \
                 "(skip local-multi torchrun); " + ext.get("why", "")
    return ext


def select_backend(args, spec: dict) -> dict:
    if args.backend in {"wan", "ltx"}:
        # Explicit local family request still honours probe for offload sizing,
        # but a forced family means "run it locally".
        ext = run_external_probe(args.task, args.model, args.want_quality,
                                 args.margin, args.backend)
        if ext and ext.get("backend", "").startswith("local"):
            if args.offload and ext.get("backend") == "local-multi":
                return _force_single_offload(ext, spec)
            return ext
        return builtin_select(args.task, args.model, spec, args.want_quality,
                              args.margin, args.backend, args.offload)
    if args.backend == "grok":
        return {"backend": "grok", "device": None, "precision": None,
                "offload": False, "multigpu": False,
                "model": spec.get("repo"), "why": "user forced grok"}
    # backend == auto
    ext = run_external_probe(args.task, args.model, args.want_quality,
                             args.margin, None)
    if ext:
        ext.setdefault("model", spec.get("repo"))
        if args.offload and ext.get("backend") == "local-multi":
            return _force_single_offload(ext, spec)
        return ext
    return builtin_select(args.task, args.model, spec, args.want_quality,
                          args.margin, None, args.offload)


# --------------------------------------------------------------------------- #
# Validation helpers
# --------------------------------------------------------------------------- #
def validate_frames(n: int, spec: dict) -> int:
    k, r = spec.get("frame_rule", (4, 1))
    if (n - r) % k != 0 or n < r:
        fixed = max(r, ((n - r) // k) * k + r)
        log(f"num_frames {n} violates {k}*k+{r} rule -> using {fixed}")
        return fixed
    return n


def validate_dim(v: int, spec: dict, name: str) -> int:
    m = spec.get("dim_multiple", 16)
    if v % m != 0:
        fixed = max(m, (v // m) * m)
        log(f"{name} {v} not divisible by {m} -> using {fixed}")
        return fixed
    return v


# --------------------------------------------------------------------------- #
# Local diffusers runners
# --------------------------------------------------------------------------- #
def run_wan(args, spec: dict, decision: dict) -> None:
    import numpy as np
    import torch
    from diffusers.utils import export_to_video

    repo = spec["repo"]
    offload = decision.get("offload", False)
    log(f"loading Wan pipeline {repo} (task={args.task}, offload={offload})")

    from diffusers import AutoencoderKLWan

    # VAE forced fp32 — bf16 VAE visibly degrades Wan decode.
    vae = AutoencoderKLWan.from_pretrained(repo, subfolder="vae",
                                           torch_dtype=torch.float32)

    if args.task == "i2v":
        from diffusers import WanImageToVideoPipeline
        from diffusers.utils import load_image
        pipe = WanImageToVideoPipeline.from_pretrained(
            repo, vae=vae, torch_dtype=torch.bfloat16)
    else:
        from diffusers import WanPipeline
        pipe = WanPipeline.from_pretrained(
            repo, vae=vae, torch_dtype=torch.bfloat16)

    if offload:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    width = validate_dim(args.width or spec.get("default_w", 832), spec, "width")
    height = validate_dim(args.height or spec.get("default_h", 480), spec, "height")
    frames = validate_frames(args.num_frames, spec)
    steps = args.steps or spec.get("default_steps", 40)
    guidance = args.guidance if args.guidance is not None else spec.get("default_guidance", 5.0)
    fps = args.fps or spec.get("default_fps", 16)
    negative = args.negative_prompt or (
        "Bright tones, overexposed, static, blurred details, subtitles, "
        "worst quality, low quality, deformed, disfigured, extra fingers, "
        "messy background")

    gen_kwargs = dict(
        prompt=args.prompt, negative_prompt=negative,
        height=height, width=width, num_frames=frames,
        num_inference_steps=steps, guidance_scale=guidance,
    )
    if spec.get("moe"):  # A14B two-stage denoise needs guidance_scale_2
        gen_kwargs["guidance_scale_2"] = guidance

    if args.task == "i2v":
        image = load_image(args.image)
        # Fit to max area while honouring the patch/vae alignment.
        max_area = width * height
        ar = image.height / image.width
        try:
            mod = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
        except Exception:
            mod = spec.get("dim_multiple", 16)
        h = max(mod, round(np.sqrt(max_area * ar)) // mod * mod)
        w = max(mod, round(np.sqrt(max_area / ar)) // mod * mod)
        image = image.resize((w, h))
        gen_kwargs.update(image=image, height=h, width=w)

    if args.seed is not None:
        gen_kwargs["generator"] = torch.Generator("cpu").manual_seed(args.seed)

    log(f"generating: {width}x{height} {frames}f {steps}steps cfg={guidance}")
    result = pipe(**gen_kwargs).frames[0]
    export_to_video(result, args.out, fps=fps)
    log(f"WROTE {args.out} (fps={fps})")


def run_ltx(args, spec: dict, decision: dict) -> None:
    import torch
    from diffusers.utils import export_to_video

    repo = spec["repo"]
    offload = decision.get("offload", False)
    log(f"loading LTX-Video pipeline {repo} (task={args.task}, offload={offload})")

    if args.task == "i2v":
        from diffusers import LTXImageToVideoPipeline
        from diffusers.utils import load_image
        pipe = LTXImageToVideoPipeline.from_pretrained(repo, torch_dtype=torch.bfloat16)
    else:
        from diffusers import LTXPipeline
        pipe = LTXPipeline.from_pretrained(repo, torch_dtype=torch.bfloat16)

    # NOTE: do NOT force the LTX VAE to fp32. Unlike Wan, the LTX pipeline does
    # not upcast latents before the VAE, so a fp32 VAE with bf16 latents raises
    # "Input type (BFloat16) and bias type (float) should be the same". LTX-Video
    # decodes fine in bf16; keep the whole pipeline bf16.
    try:
        pipe.vae.enable_tiling()  # memory-friendly decode for tall/long clips
    except Exception:
        pass

    if offload:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    width = validate_dim(args.width or spec.get("default_w", 768), spec, "width")
    height = validate_dim(args.height or spec.get("default_h", 512), spec, "height")
    frames = validate_frames(args.num_frames, spec)
    steps = args.steps or spec.get("default_steps", 50)
    guidance = args.guidance if args.guidance is not None else spec.get("default_guidance", 3.0)
    fps = args.fps or spec.get("default_fps", 24)
    negative = args.negative_prompt or (
        "worst quality, inconsistent motion, blurry, jittery, distorted")

    gen_kwargs = dict(
        prompt=args.prompt, negative_prompt=negative,
        width=width, height=height, num_frames=frames,
        num_inference_steps=steps, guidance_scale=guidance,
        decode_timestep=spec.get("decode_timestep", 0.03),
        decode_noise_scale=spec.get("decode_noise_scale", 0.025),
    )
    if args.task == "i2v":
        gen_kwargs["image"] = load_image(args.image)
    if args.seed is not None:
        gen_kwargs["generator"] = torch.Generator("cpu").manual_seed(args.seed)

    log(f"generating: {width}x{height} {frames}f {steps}steps cfg={guidance}")
    result = pipe(**gen_kwargs).frames[0]
    export_to_video(result, args.out, fps=fps)
    log(f"WROTE {args.out} (fps={fps})")


# --------------------------------------------------------------------------- #
# Non-local backends: print exact handoff instructions (no re-implementation)
# --------------------------------------------------------------------------- #
def emit_ltx2_defer(args, spec: dict, decision: dict) -> None:
    print(textwrap.dedent(f"""
    ============================================================
    LTX-2.3 is NOT supported by diffusers — use gen_video_ltx2.py
    ============================================================
    The chosen model ({args.model}) runs via the official ltx_pipelines
    package, not diffusers. Re-run with the dedicated script:

      source {ENV_SH}
      "$UV" run {GEN_LTX2_PY} \\
        --task {args.task} --prompt {sh(args.prompt)} \\
        {('--image ' + sh(args.image)) if args.image else ''} \\
        --out {sh(args.out)} \\
        --quantization fp8-cast        # backend chose: {decision['backend']}

    First-run setup (HF token + gated google/gemma-3 license, ~100GB disk)
    is documented in {SKILL_DIR / 'reference' / 'setup.md'}.
    ============================================================
    """).strip(), file=sys.stderr)


def emit_multigpu(args, spec: dict, decision: dict) -> None:
    size = f"{args.width or spec.get('default_w')}*{args.height or spec.get('default_h')}"
    task = "i2v-A14B" if args.task == "i2v" else "t2v-A14B"
    print(textwrap.dedent(f"""
    ============================================================
    BACKEND = local-multi-GPU (Wan, official torchrun)
    ============================================================
    diffusers cannot shard ONE clip across both A6000s. For full-quality
    720p sequence-parallel on 2x GPU, use the OFFICIAL Wan repo:

      git clone https://github.com/Wan-Video/Wan2.2.git && cd Wan2.2
      pip install -r requirements.txt
      huggingface-cli download Wan-AI/Wan2.2-{task.upper()} --local-dir ./ckpt

      source {ENV_SH}     # clean LD_LIBRARY_PATH first
      torchrun --nproc_per_node=2 generate.py --task {task} --size {size} \\
        --ckpt_dir ./ckpt --dit_fsdp --t5_fsdp --ulysses_size 2 \\
        --prompt {sh(args.prompt)}

    To run on ONE card instead (slower, no clone needed), re-run me with
    --backend wan (forces local-single/offload via diffusers).
    why: {decision['why']}
    ============================================================
    """).strip(), file=sys.stderr)


def emit_cloud(args, spec: dict, decision: dict) -> None:
    backend = decision["backend"]
    script = CLOUD_MODAL_PY if backend == "cloud-modal" else CLOUD_FAL_PY
    cred = "MODAL_TOKEN_ID/SECRET (modal setup)" if backend == "cloud-modal" else "FAL_KEY"
    fal_hint = ""
    if backend == "cloud-fal":
        fal_hint = f"     # fal_id: {spec.get('fal_id', '<see models.py>')}"
    print(textwrap.dedent(f"""
    ============================================================
    BACKEND = {backend}  (local VRAM insufficient)
    ============================================================
    Requires: {cred}
    why: {decision['why']}

      source {ENV_SH}
      "$UV" run {script} \\
        --model {args.model} --task {args.task} \\
        --prompt {sh(args.prompt)} \\
        {('--image ' + sh(args.image)) if args.image else ''} \\
        --out {sh(args.out)}{fal_hint}
    ============================================================
    """).strip(), file=sys.stderr)


def emit_grok(args, spec: dict, decision: dict) -> None:
    """Print EXACT instructions to delegate to the grok-media skill.

    We DO NOT re-implement Grok here. grok-media owns the binary path, auth
    gate, clean-dir rule, NL tool-naming, and session-dir output recovery.
    For Grok, text-to-video is a 2-STAGE flow (image_gen -> image_to_video).
    """
    stage = (
        "image_to_video (animate the supplied --image directly)"
        if args.task == "i2v" else
        "image_gen (make a still from the prompt) THEN image_to_video (animate it)"
    )
    grok_skill = SKILL_DIR.parent / "grok-media" / "SKILL.md"
    print(textwrap.dedent(f"""
    ============================================================
    BACKEND = grok  (LAST resort — delegate to the grok-media skill)
    ============================================================
    why: {decision['why']}

    This script intentionally does NOT call Grok. Hand off to the
    grok-media skill ({grok_skill}) and follow its contract verbatim:

      1. AUTH GATE (run first, every time):
           "$HOME/.grok/bin/grok.exe" models 2>&1 | head -3
         If 'not authenticated', STOP and ask the user to run, in THEIR
         own terminal:  grok login --device-auth   (OAuth, cannot be automated)

      2. CLEAN DIR (mandatory — running inside a project dir => Auth error):
           WORK="$(mktemp -d)"; cd "$WORK"
         {f'cp {sh(args.image)} "$WORK/input.jpg"' if args.image else ''}

      3. INVOKE via natural language naming the built-in tool:
           For this {args.task} request, use:
             {stage}
         e.g.:
           grok -p 'Use your image_gen tool to create an image: {args.prompt}'
           grok -p 'Use your image_to_video tool to animate ./input.jpg into a
                    short 3-second video: {args.prompt}. Save the video file.'
         (video is async ~50s — run with run_in_background)

      4. OUTPUT RECOVERY (output is NOT in cwd; empty reply != failure):
           ls -t "$HOME/.grok/sessions/"*"/"*"/videos/"*.mp4 2>/dev/null | head -3
         or:  grok -r -p 'What is the absolute path of the media you just
                          generated? Reply with ONLY the path.'
         Then copy/deliver it to: {args.out}

    Do not duplicate grok-media's CLI mechanics — defer to that skill.
    ============================================================
    """).strip(), file=sys.stderr)


def sh(s: str | None) -> str:
    """Single-quote a string for safe copy-paste into a shell."""
    if s is None:
        return "''"
    return "'" + str(s).replace("'", "'\\''") + "'"


# --------------------------------------------------------------------------- #
# Re-exec through a clean shell so torch loads without conda libtinfo
# --------------------------------------------------------------------------- #
def reexec_clean() -> None:
    """If env.sh exists and we haven't cleaned yet, re-exec through it once.

    Guarded by _GEV_CLEANED so we never loop. This guarantees the heavy torch
    import below sees a scrubbed LD_LIBRARY_PATH even when invoked from a conda
    shell. If env.sh is absent we just scrub in-process (clean_ld_environment).
    """
    if os.environ.get("_GEV_CLEANED") == "1" or not ENV_SH.exists():
        clean_ld_environment()
        return
    os.environ["_GEV_CLEANED"] = "1"
    cmd = (f'source {sh(str(ENV_SH))}; exec "$UV" run {sh(str(Path(__file__).resolve()))} '
           + " ".join(sh(a) for a in sys.argv[1:]))
    log("re-exec through env.sh for a clean LD_LIBRARY_PATH")
    os.execvp("bash", ["bash", "-lc", cmd])


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_video.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Unified video-generation entrypoint (LOCAL-GPU-FIRST).

            --backend auto runs the VRAM probe and picks local-single /
            local-offload / local-multi / cloud-modal / cloud-fal / grok,
            logging the WHY. Local Wan/LTX-Video run via diffusers in a clean
            env (conda LD_LIBRARY_PATH stripped). grok defers to grok-media."""),
        epilog=textwrap.dedent("""\
            examples:
              # auto-pick backend, text-to-video (fast 1.3B default)
              generate_video.py --task t2v --prompt "a fox in snow, cinematic" --out fox.mp4

              # image-to-video, force local Wan, 720p with offload
              generate_video.py --backend wan --task i2v --model wan2.2-i2v-a14b \\
                --image still.jpg --width 1280 --height 720 --offload --out anim.mp4

              # LTX-Video t2v
              generate_video.py --backend ltx --task t2v --model ltx-video-0.9.8 \\
                --prompt "ocean waves at sunset" --num-frames 121 --out waves.mp4

              # print Grok delegation instructions (no local GPU / last resort)
              generate_video.py --backend grok --task t2v --prompt "neon city" --out city.mp4
            """),
    )
    p.add_argument("--backend", choices=["auto", "wan", "ltx", "grok"],
                   default="auto",
                   help="auto = VRAM-probe pick; wan/ltx force a local family; "
                        "grok prints grok-media delegation (default: auto)")
    p.add_argument("--task", choices=["t2v", "i2v"], default="t2v",
                   help="text-to-video or image-to-video (default: t2v)")
    p.add_argument("--prompt", default="", help="text prompt")
    p.add_argument("--image", help="input still image (required for i2v)")
    p.add_argument("--out", default="out.mp4", help="output mp4 path (default: out.mp4)")
    p.add_argument("--model",
                   help="model id (default: per-task; see scripts/models.py). "
                        f"built-in: {', '.join(sorted(FALLBACK_MODELS))}")
    p.add_argument("--width", type=int, help="output width (snapped to model multiple)")
    p.add_argument("--height", type=int, help="output height (snapped to model multiple)")
    p.add_argument("--num-frames", type=int, default=81,
                   help="frame count (snapped to family rule: Wan 4k+1, LTX 8k+1; "
                        "default: 81)")
    p.add_argument("--fps", type=int, help="export fps (default: model default)")
    p.add_argument("--steps", type=int, help="inference steps (default: model default)")
    p.add_argument("--guidance", type=float,
                   help="guidance scale / CFG (default: model default; "
                        "turbo/distilled want ~0)")
    p.add_argument("--negative-prompt", help="negative prompt")
    p.add_argument("--seed", type=int, help="random seed")
    p.add_argument("--offload", action="store_true",
                   help="force enable_model_cpu_offload() (probe may set this anyway)")
    p.add_argument("--want-quality", choices=["fast", "quality"], default="fast",
                   help="quality on a big Wan with 2 idle GPUs routes to multi-GPU "
                        "(default: fast)")
    p.add_argument("--margin", type=float, default=1.1,
                   help="VRAM safety margin for the fits check (default: 1.1)")
    p.add_argument("--print-decision", action="store_true",
                   help="probe + print the backend decision JSON, then exit")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Resolve default model per task if not given.
    if not args.model:
        args.model = DEFAULT_MODEL_FOR_TASK[args.task]
        # i2v on the LTX family needs the i2v variant id.
        if args.task == "i2v" and args.model.startswith("ltx-video") \
                and not args.model.endswith("-i2v"):
            args.model = "ltx-video-0.9.8-i2v"

    spec = load_model_spec(args.model)

    # Validate task/model coherence.
    if args.task == "i2v" and not args.image:
        parser.error("--task i2v requires --image")
    if spec.get("task") and spec["task"] != args.task:
        log(f"warning: model '{args.model}' is a {spec['task']} model but "
            f"--task is {args.task}")

    decision = select_backend(args, spec)
    log(f"BACKEND={decision['backend']} :: {decision.get('why', '')}")

    if args.print_decision:
        print(json.dumps(decision))
        return 0

    backend = decision["backend"]

    # ---- non-local handoffs (print exact instructions, do not run) ----
    if backend == "grok":
        emit_grok(args, spec, decision)
        return 0
    if backend == "local-multi":
        emit_multigpu(args, spec, decision)
        return 0
    if backend in {"cloud-modal", "cloud-fal"}:
        emit_cloud(args, spec, decision)
        return 0
    if spec.get("defer_to_ltx2") or spec.get("pipeline") == "ltx2":
        emit_ltx2_defer(args, spec, decision)
        return 0

    # ---- local diffusers run ----
    Path(args.out).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    pipeline = spec.get("pipeline")
    if pipeline == "wan":
        run_wan(args, spec, decision)
    elif pipeline == "ltx":
        run_ltx(args, spec, decision)
    else:
        raise SystemExit(f"no local runner for pipeline '{pipeline}' (model {args.model})")

    print(args.out)  # stdout = the artifact path, for callers/chaining
    return 0


if __name__ == "__main__":
    # Clean the env BEFORE importing torch (done lazily inside runners). For the
    # local path we additionally re-exec through env.sh once when available.
    if "--print-decision" not in sys.argv and "--help" not in sys.argv \
            and "-h" not in sys.argv:
        reexec_clean()
    else:
        clean_ld_environment()
    sys.exit(main())
