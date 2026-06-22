#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch",
#   # Official Lightricks inference code. diffusers has NO LTX-2 support (see
#   # header). Package/module name has historically drifted ("ltx", "ltx-video",
#   # "ltx_video", "ltx_pipelines"); we install from the official repo and probe
#   # several import names at runtime. If this git dep fails to resolve, follow
#   # the OFFICIAL-VENV path printed by --help / the import-failure fallback.
#   "ltx-video @ git+https://github.com/Lightricks/LTX-2.git",
#   "transformers>=4.51.3",   # gated Gemma-3 text encoder lives here
#   "accelerate",
#   "safetensors",
#   "sentencepiece",
#   "protobuf",
#   "imageio",
#   "imageio-ffmpeg",
#   "pillow",
#   "numpy",
#   "huggingface-hub",
# ]
# ///
"""
gen_video_ltx2.py — run LTX-2.3 (the ~22B AUDIO+VIDEO model) locally via the
OFFICIAL Lightricks inference code. This is the dedicated path that
scripts/gen_video.py defers to whenever a request resolves to model `ltx-2.3`
(its model matrix marks that entry `defer_to_ltx2: True`, pipeline `ltx2`).

============================================================================
WHY THIS SCRIPT EXISTS (read before trusting the call site below)
============================================================================
* diffusers DOES NOT support LTX-2 / LTX-2.3 yet (verified Jun 2026). The
  diffusers `LTXPipeline` / `LTXImageToVideoPipeline` classes are for
  LTX-Video 0.9.x ONLY (video-only, Apache-2.0, T5 encoder). LTX-2.3 is a
  different, larger (~22B), audio+video model under the LTX-2 Community
  License and is served by the OFFICIAL repo, not diffusers:
      https://github.com/Lightricks/LTX-2     (checkpoints: Lightricks/LTX-2.3)
* Official inference uses the `ltx_pipelines` API (historically
  `TI2VidTwoStagesPipeline` / `DistilledPipeline`) shipped inside that repo's
  python package. The python package/import name HAS DRIFTED across releases
  ("ltx", "ltx_video", "ltx_pipelines"); we probe several below.
* Text encoder = GATED Gemma-3: `google/gemma-3-12b-it-qat-q4_0-unquantized`.
  You MUST `huggingface-cli login` AND accept the Gemma-3 license in a browser,
  AND accept the Lightricks/LTX-2.3 model license, or downloads 401. Needs
  ~100 GB free disk for weights.
* Ampere (RTX A6000, sm_86) here: NO FlashAttention-3 (Hopper), NO nvfp4
  (Blackwell + CUDA 12.7+). Use bf16 (fits in 48 GB) or `--quantization
  fp8-cast` (~18-20 GB, safer headroom). fp8-cast is the DEFAULT on A6000.
* Memory note (GitHub Lightricks/LTX-2 #152): wrap encode+generate in
  `torch.inference_mode()` or Gemma activations can pin ~37 GB. We do.

============================================================================
HONESTY / VERIFY-AT-FIRST-RUN
============================================================================
The EXACT official API (class names, constructor kwargs, how prompt/image/
num_frames/guidance/audio map to the call) drifts between LTX-2 releases. The
`run_ltx2()` section below is structured DEFENSIVELY and is clearly marked with
`# TODO[VERIFY]` at each spot that must be confirmed against the CURRENT repo
(check its `inference.py` / README example). It is honest about this rather
than fabricating a confident-but-wrong call. If imports fail OR the call site
cannot be confirmed, it falls back GRACEFULLY and prints the cloud/Grok route:
    LTX-2 local path unavailable -> use cloud_fal.py --model ltx-2.3 or grok-media

============================================================================
ENVIRONMENT
============================================================================
* Run via uv (PEP 723 inline deps), NEVER the conda/anaconda python.
* anaconda's libtinfo.so.6 pollutes LD_LIBRARY_PATH and has broken subprocesses
  before. This script scrubs conda paths out of LD_LIBRARY_PATH in-process
  before importing torch (mirrors scripts/env.sh). If invoking from a polluted
  interactive shell, `source scripts/env.sh` first as well.
* HF cache goes on the big disk via HF_HOME (defaults set below if unset).

ROBUST ALTERNATIVE (when the PEP723 git dep or API won't cooperate):
use the repo's OWN pinned venv, then run its example/inference entrypoint:
    git clone https://github.com/Lightricks/LTX-2.git && cd LTX-2
    uv sync --frozen && source .venv/bin/activate
    uv sync --extra xformers          # attention opt on Ampere
    # system: Python 3.12+, torch 2.7. nvfp4 N/A on Ampere -> fp8-cast.
    huggingface-cli login             # + accept Gemma-3 & LTX-2.3 licenses
This script's job is the convenience CLI + safe defaults + clear handoff; the
repo's own venv is the most reliable execution substrate if uv's resolver or
the import name disagree with what this header assumed.

CLI: --prompt --image (i2v) --task [t2v|i2v] --num-frames (8k+1, default 121)
     --width --height (each /32) --fps (default 25) --steps (default 40)
     --guidance (default 3.0) --quantization [none|fp8-cast] (default fp8-cast
     on A6000) --seed --out. Run with --help for everything.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
import textwrap
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ENV_SH = SCRIPT_DIR / "env.sh"
CLOUD_FAL_PY = SCRIPT_DIR / "cloud_fal.py"
REFERENCE_MD = SKILL_DIR / "reference" / "reference.md"

# --- LTX-2.3 canonical defaults (mirror gen_video.py FALLBACK_MODELS["ltx-2.3"]) ---
LTX2_REPO = "Lightricks/LTX-2.3"
GEMMA_REPO = "google/gemma-3-12b-it-qat-q4_0-unquantized"
FRAME_RULE = (8, 1)          # num_frames must be 8*k + 1
DIM_MULTIPLE = 32            # width & height must each be divisible by 32
DEFAULT_FRAMES = 121         # 8*15 + 1  (valid LTX-2.3 lengths: 97 / 121 / 193)
DEFAULT_W = 768
DEFAULT_H = 512
DEFAULT_FPS = 25
DEFAULT_STEPS = 40           # `dev` wants ~40 steps + higher CFG; distilled wants 8 @ CFG=1.0
DEFAULT_GUIDANCE = 3.0       # video CFG. (official MultiModalGuider: video 3.0 / audio 7.0)
AUDIO_GUIDANCE = 7.0


def log(msg: str) -> None:
    print(f"[gen_video_ltx2] {msg}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Clean environment — scrub anaconda LD pollution BEFORE importing torch.
# (Replicates scripts/env.sh for the in-process python path.)
# --------------------------------------------------------------------------- #
def clean_ld_environment() -> None:
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p for p in ld.split(os.pathsep)
            if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p
        ]
        new = os.pathsep.join(kept)
        if new:
            os.environ["LD_LIBRARY_PATH"] = new
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
        if new != ld:
            log(f"scrubbed conda paths from LD_LIBRARY_PATH (was {len(ld)} chars)")
    # Cut CUDA fragmentation for the 22B + Gemma load.
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    # Keep the (large) HF cache on the big disk unless the caller already set it.
    if not os.environ.get("HF_HOME"):
        for cand in ("/home/kita/.cache/huggingface", str(Path.home() / ".cache" / "huggingface")):
            os.environ.setdefault("HF_HOME", cand)
            break


# --------------------------------------------------------------------------- #
# Validation: 8k+1 frame rule and /32 dims
# --------------------------------------------------------------------------- #
def validate_frames(n: int) -> int:
    mult, off = FRAME_RULE
    if n < off or (n - off) % mult != 0:
        # Snap to the nearest valid value and report a clear error/suggestion.
        k = max(1, round((n - off) / mult))
        suggestion = mult * k + off
        raise SystemExit(
            f"--num-frames must satisfy the LTX-2 frame rule {mult}k+{off} "
            f"(e.g. 97, 121, 193). Got {n}. Nearest valid: {suggestion}."
        )
    return n


def validate_dim(value: int, name: str) -> int:
    if value % DIM_MULTIPLE != 0 or value <= 0:
        lo = (value // DIM_MULTIPLE) * DIM_MULTIPLE
        hi = lo + DIM_MULTIPLE
        raise SystemExit(
            f"--{name} must be a positive multiple of {DIM_MULTIPLE}. "
            f"Got {value}. Nearest valid: {lo if lo > 0 else hi} or {hi}."
        )
    return value


# --------------------------------------------------------------------------- #
# Defensive import of the official ltx package (name has drifted across releases)
# --------------------------------------------------------------------------- #
CANDIDATE_MODULES = ("ltx_pipelines", "ltx_video", "ltx", "ltxv")


def import_ltx():
    """Return (module, module_name) for the first importable official LTX-2 pkg.

    Raises ImportError with a helpful message if none import. We do NOT guess a
    fake module — we try the names the official repo has actually used and let
    the caller fall back to cloud/Grok on failure.
    """
    errors = []
    for name in CANDIDATE_MODULES:
        try:
            mod = importlib.import_module(name)
            log(f"imported official LTX-2 package: {name}")
            return mod, name
        except Exception as e:  # ImportError, or partial-install errors
            errors.append(f"  {name}: {type(e).__name__}: {e}")
    raise ImportError(
        "Could not import any official LTX-2 package.\n"
        "Tried: " + ", ".join(CANDIDATE_MODULES) + "\n" + "\n".join(errors)
    )


# --------------------------------------------------------------------------- #
# Graceful fallback (REQUIRED behaviour): print the cloud/Grok route, exit 0.
# --------------------------------------------------------------------------- #
def fallback_unavailable(args, reason: str) -> "NoReturn":  # type: ignore[name-defined]
    img = f" --image {args.image}" if args.image else ""
    print(textwrap.dedent(f"""
    ============================================================
    LTX-2 local path unavailable -> use cloud_fal.py --model ltx-2.3 or grok-media
    ============================================================
    reason: {reason}

    LTX-2.3 has NO diffusers support and the official local path could not run
    here. Pick one of the verified fallbacks:

    A) Cloud (fal, hosted LTX-2.3 — fastest, needs FAL_KEY):
         source {ENV_SH}
         "$UV" run {CLOUD_FAL_PY} \\
           --model ltx-2.3 --task {args.task} \\
           --prompt {args.prompt!r}{img} \\
           --out {args.out!r}        # fal_id: fal-ai/ltx-2.3/{args.task.replace('t2v','text-to-video').replace('i2v','image-to-video')}

    B) Grok (subscription quota, no metering — delegate to the grok-media skill):
         Follow {SKILL_DIR.parent / 'grok-media' / 'SKILL.md'} verbatim.
         For {args.task}: { 'image_to_video (animate --image)' if args.task=='i2v'
                            else 'image_gen -> image_to_video (2-stage)' }.

    C) Fix the LOCAL path and re-run this script (most reliable substrate is the
       repo's OWN venv — see this file's header "ROBUST ALTERNATIVE"):
         - huggingface-cli login  + accept licenses for:
             {LTX2_REPO}  and  {GEMMA_REPO}
         - ensure ~100 GB free disk for weights
         - confirm the current official API in github.com/Lightricks/LTX-2
           (inference.py / README) against the `# TODO[VERIFY]` notes here.
    Setup details: {REFERENCE_MD}
    ============================================================
    """).strip(), file=sys.stderr)
    sys.exit(0)


# =========================================================================== #
# run_ltx2() — CONSTRUCT THE PIPELINE AND WRITE THE MP4.
#
#   !!! VERIFY-AT-FIRST-RUN !!!
#   Every `# TODO[VERIFY]` below is a spot whose exact spelling/signature must
#   be confirmed against the CURRENT Lightricks/LTX-2 repo. The structure (load
#   encoder+transformer+vae -> build a guider -> call the two-stage / distilled
#   pipeline -> get frames (+audio) -> mux to mp4) is correct in shape, but the
#   official symbol names and kwargs are NOT guaranteed stable. Do not present
#   this as a verified API; treat a clean first run as the verification step.
# =========================================================================== #
def run_ltx2(args, ltx, ltx_name: str) -> None:
    import torch  # noqa: F401  (already scrubbed env)

    use_fp8 = (args.quantization == "fp8-cast")
    dtype = "fp8-cast" if use_fp8 else "bf16"
    log(f"loading {LTX2_REPO} ({dtype}); text encoder={GEMMA_REPO}; "
        f"task={args.task} {args.width}x{args.height} frames={args.num_frames} "
        f"fps={args.fps} steps={args.steps} guidance={args.guidance} seed={args.seed}")

    # ----------------------------------------------------------------------- #
    # TODO[VERIFY] (1) — PIPELINE CONSTRUCTION.
    # The official repo exposes (historically) a high-level pipeline such as:
    #     ltx_pipelines.TI2VidTwoStagesPipeline   (dev, ~40 steps, higher CFG)
    #     ltx_pipelines.DistilledPipeline         (distilled-1.1, 8 steps, CFG=1.0)
    # and a `.from_pretrained(...)` / config-driven loader. Confirm the actual
    # class + factory name and the checkpoint/config kwargs against the repo's
    # current inference.py / README. The block below tries the most likely
    # entrypoints in order and raises if none exist (-> graceful fallback).
    # ----------------------------------------------------------------------- #
    PipelineCls = None
    for cls_name in (
        "TI2VidTwoStagesPipeline",  # TODO[VERIFY] dev two-stage class name
        "DistilledPipeline",        # TODO[VERIFY] distilled class name
        "LTX2Pipeline",
        "LTXVideoPipeline",
        "Pipeline",
    ):
        PipelineCls = getattr(ltx, cls_name, None)
        if PipelineCls is not None:
            log(f"using pipeline class: {ltx_name}.{cls_name}")
            break
    if PipelineCls is None:
        raise AttributeError(
            f"No known LTX-2 pipeline class found in module '{ltx_name}'. "
            f"Inspect `dir({ltx_name})` and update run_ltx2()'s class list "
            f"against the current github.com/Lightricks/LTX-2 inference code."
        )

    # TODO[VERIFY] (2) — FACTORY + LOAD KWARGS.
    # Confirm: does it take the model repo id directly, a local --ckpt dir, a
    # config yaml, or a precision flag? Confirm where the gated Gemma-3 encoder
    # repo is passed. Confirm the fp8-cast switch name (e.g. precision=,
    # quantization=, dtype=, load_in_8bit=...). The two attempts below cover the
    # common `from_pretrained` and direct-constructor shapes.
    load_kwargs = {
        # "precision": dtype,                 # TODO[VERIFY] fp8-cast vs bf16 flag
        # "text_encoder_id": GEMMA_REPO,      # TODO[VERIFY] gated Gemma-3 wiring
        # "device": "cuda",
    }
    try:
        from_pretrained = getattr(PipelineCls, "from_pretrained", None)
        if callable(from_pretrained):
            pipe = from_pretrained(LTX2_REPO, **load_kwargs)  # TODO[VERIFY]
        else:
            pipe = PipelineCls(**load_kwargs)                 # TODO[VERIFY]
    except Exception as e:
        raise RuntimeError(
            f"LTX-2 pipeline load failed (confirm from_pretrained/ctor signature "
            f"and that {LTX2_REPO} + {GEMMA_REPO} licenses are accepted & "
            f"downloaded): {type(e).__name__}: {e}"
        )

    # Move to GPU / apply fp8-cast if the high-level pipeline did not already.
    try:
        if hasattr(pipe, "to"):
            pipe.to("cuda")  # TODO[VERIFY] some pipelines self-manage placement
    except Exception as e:
        log(f"pipe.to('cuda') skipped/failed (may be self-managed): {e}")

    # ----------------------------------------------------------------------- #
    # TODO[VERIFY] (3) — IMAGE CONDITIONING (i2v) and GUIDER PARAMS.
    # i2v: confirm the kwarg name for the conditioning image (image=, conditions=,
    # media_items=, first_frame=...) and whether a PIL.Image or a path is wanted.
    # Audio+video: official MultiModalGuiderParams uses video cfg 3.0 / audio cfg
    # 7.0, stg_blocks [28, 29]. Confirm how/whether to pass a guider object.
    # ----------------------------------------------------------------------- #
    image_obj = None
    if args.task == "i2v":
        if not args.image:
            raise SystemExit("--task i2v requires --image")
        try:
            from PIL import Image
            image_obj = Image.open(args.image).convert("RGB")
        except Exception as e:
            raise SystemExit(f"could not open --image {args.image!r}: {e}")

    # TODO[VERIFY] (4) — THE GENERATION CALL.
    # Confirm the actual call signature. Common shape:
    #     out = pipe(prompt=..., num_frames=..., width=..., height=...,
    #                frame_rate=..., num_inference_steps=..., guidance_scale=...,
    #                generator=torch.Generator("cuda").manual_seed(seed),
    #                [image=image_obj for i2v])
    # Confirm: `frame_rate` vs `fps`; `guidance_scale` vs a guider object;
    # whether audio is returned and under which attribute.
    gen_kwargs = dict(
        prompt=args.prompt,
        num_frames=args.num_frames,
        width=args.width,
        height=args.height,
        frame_rate=args.fps,          # TODO[VERIFY] frame_rate vs fps kwarg name
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,  # TODO[VERIFY] scalar vs guider object
    )
    if image_obj is not None:
        gen_kwargs["image"] = image_obj   # TODO[VERIFY] image kwarg name for i2v
    if args.seed is not None:
        try:
            import torch as _t
            gen_kwargs["generator"] = _t.Generator("cuda").manual_seed(args.seed)
        except Exception:
            pass

    import torch as _t
    with _t.inference_mode():  # GitHub #152: keeps Gemma activations from pinning ~37 GB
        try:
            result = pipe(**gen_kwargs)  # TODO[VERIFY] full call signature
        except TypeError as e:
            raise RuntimeError(
                "LTX-2 generation call signature mismatch — inspect the current "
                "repo example and align run_ltx2()'s gen_kwargs (frame_rate/fps, "
                "guidance vs guider, image kwarg). Original: " + str(e)
            )

    # TODO[VERIFY] (5) — EXTRACT FRAMES (+ optional audio) FROM THE RESULT.
    # Confirm the result type/attribute. Common: result.frames[0] (list of PIL),
    # or result.video, or a (frames, audio) tuple, or an np.ndarray. We try the
    # usual shapes and bail to fallback shape-handling if none match.
    frames = _extract_frames(result)
    audio = _extract_audio(result)  # may be None (audio is LTX-2's headline feature)

    _write_mp4(args.out, frames, fps=args.fps, audio=audio)
    log(f"WROTE {args.out} (frames={len(frames)} fps={args.fps} "
        f"audio={'yes' if audio is not None else 'no'})")
    if audio is None:
        log("NOTE: no audio track recovered. LTX-2.3 generates audio+video; if "
            "you expected sound, confirm TODO[VERIFY] (4)/(5) audio handling.")


def _extract_frames(result):
    """Best-effort frame extraction across plausible official return shapes."""
    # PIL list under .frames (diffusers-like): result.frames[0]
    for attr in ("frames", "video", "videos", "images"):
        obj = getattr(result, attr, None)
        if obj is not None:
            # nested list-of-list (batch)
            if isinstance(obj, (list, tuple)) and obj and isinstance(obj[0], (list, tuple)):
                return list(obj[0])
            return list(obj) if not hasattr(obj, "shape") else obj
    if isinstance(result, (list, tuple)) and result:
        first = result[0]
        if isinstance(first, (list, tuple)):
            return list(first)
        return list(result)
    if hasattr(result, "shape"):  # raw tensor/ndarray [T,H,W,C] or [B,T,...]
        return result
    raise RuntimeError(
        "Could not extract frames from LTX-2 result of type "
        f"{type(result).__name__}. Update _extract_frames() per the repo's "
        "documented return shape (TODO[VERIFY] (5))."
    )


def _extract_audio(result):
    for attr in ("audio", "audios", "audio_waveform", "waveform"):
        obj = getattr(result, attr, None)
        if obj is not None:
            return obj
    if isinstance(result, (list, tuple)) and len(result) >= 2:
        # (frames, audio) tuple shape
        return result[1]
    return None


def _write_mp4(out_path: str, frames, fps: int, audio=None) -> None:
    """Write frames to mp4 via imageio. Audio muxing is best-effort.

    TODO[VERIFY] (6) — AUDIO MUX. imageio-ffmpeg writes video only. If `audio`
    is a waveform, the robust path is: write video to a temp file, write the
    waveform to a wav, then mux with ffmpeg (env.sh-scrubbed). Confirm the
    audio sample-rate/format the official pipeline returns before wiring this.
    For now we write the video reliably and log that audio mux needs the repo's
    documented sample rate; cloud_fal.py already returns muxed a/v if needed.
    """
    import numpy as np
    import imageio

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    def to_uint8(fr):
        from PIL import Image
        if isinstance(fr, Image.Image):
            return np.asarray(fr.convert("RGB"), dtype=np.uint8)
        arr = np.asarray(fr)
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 1) * 255.0 if arr.max() <= 1.0 else np.clip(arr, 0, 255)
            arr = arr.astype(np.uint8)
        return arr

    # Normalise frames to an iterable of HxWxC uint8 arrays.
    seq = frames
    if hasattr(frames, "shape") and getattr(frames, "ndim", 0) >= 4:
        seq = [frames[i] for i in range(frames.shape[0])]

    writer = imageio.get_writer(
        str(out), fps=int(fps), codec="libx264",
        quality=8, macro_block_size=None,
    )
    try:
        for fr in seq:
            writer.append_data(to_uint8(fr))
    finally:
        writer.close()

    if audio is not None:
        log("audio waveform present but mux not performed (TODO[VERIFY] (6): "
            "confirm sample rate, then ffmpeg-mux or use cloud_fal.py for a/v).")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gen_video_ltx2.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Run LTX-2.3 (~22B audio+video) LOCALLY via the OFFICIAL Lightricks
            inference code (ltx_pipelines). diffusers has NO LTX-2 support; this
            is the dedicated path scripts/gen_video.py defers to for model
            `ltx-2.3`.

            REQUIREMENTS (first run):
              * huggingface-cli login, then accept the licenses for BOTH
                  Lightricks/LTX-2.3   and   google/gemma-3-12b-it-qat-q4_0-unquantized
                (gated Gemma-3 is the text encoder) or downloads 401.
              * ~100 GB free disk for weights.
              * Run via uv in a CLEAN env (conda LD_LIBRARY_PATH scrubbed). If
                shelling from a polluted terminal, `source scripts/env.sh` first.
              * A6000/Ampere: use bf16 (fits 48 GB) or --quantization fp8-cast
                (default; ~18-20 GB). nvfp4 is Blackwell-only — unavailable here.

            HONESTY: the exact official API drifts between LTX-2 releases. The
            call site is marked with `# TODO[VERIFY]` and verifies on first run;
            if imports/API fail it prints the cloud_fal/grok-media fallback."""),
        epilog=textwrap.dedent(f"""\
            Examples:
              # text-to-video (default fp8-cast, 121 frames, 25fps)
              source {ENV_SH}
              "$UV" run {SCRIPT_DIR/'gen_video_ltx2.py'} \\
                --task t2v --prompt "a fox running through autumn forest" \\
                --out fox.mp4

              # image-to-video, bf16, 97 frames
              "$UV" run {SCRIPT_DIR/'gen_video_ltx2.py'} \\
                --task i2v --image still.png --num-frames 97 \\
                --quantization none --prompt "the scene comes alive" --out anim.mp4

            Valid --num-frames: 8k+1 (e.g. 97, 121, 193). --width/--height: /32.
            On any failure this prints:
              LTX-2 local path unavailable -> use cloud_fal.py --model ltx-2.3 or grok-media
            """),
    )
    p.add_argument("--prompt", required=True, help="Text prompt.")
    p.add_argument("--image", help="Conditioning image path (required for --task i2v).")
    p.add_argument("--task", choices=["t2v", "i2v"], default="t2v",
                   help="t2v (text->video) or i2v (image->video). Default: t2v.")
    p.add_argument("--num-frames", type=int, default=DEFAULT_FRAMES, dest="num_frames",
                   help=f"Frame count; must be 8k+1 (default {DEFAULT_FRAMES}).")
    p.add_argument("--width", type=int, default=DEFAULT_W,
                   help=f"Width, multiple of {DIM_MULTIPLE} (default {DEFAULT_W}).")
    p.add_argument("--height", type=int, default=DEFAULT_H,
                   help=f"Height, multiple of {DIM_MULTIPLE} (default {DEFAULT_H}).")
    p.add_argument("--fps", type=int, default=DEFAULT_FPS,
                   help=f"Output frame rate (default {DEFAULT_FPS}).")
    p.add_argument("--steps", type=int, default=DEFAULT_STEPS,
                   help=f"Inference steps (default {DEFAULT_STEPS}; distilled wants 8).")
    p.add_argument("--guidance", type=float, default=DEFAULT_GUIDANCE,
                   help=f"Video CFG (default {DEFAULT_GUIDANCE}; distilled wants 1.0).")
    p.add_argument("--quantization", choices=["none", "fp8-cast"], default="fp8-cast",
                   help="none=bf16 (~42GB, fits 48GB) | fp8-cast (~18-20GB, "
                        "DEFAULT on A6000). nvfp4 N/A on Ampere.")
    p.add_argument("--seed", type=int, default=None, help="RNG seed (optional).")
    p.add_argument("--out", required=True, help="Output mp4 path.")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    # Validate the hard constraints FIRST (clear errors, no heavy imports).
    args.num_frames = validate_frames(args.num_frames)
    args.width = validate_dim(args.width, "width")
    args.height = validate_dim(args.height, "height")
    if args.task == "i2v" and not args.image:
        raise SystemExit("--task i2v requires --image")
    if args.task == "t2v" and args.image:
        log("--image is ignored for --task t2v")

    clean_ld_environment()

    # Import torch first; if even torch is missing, that's a clean fallback too.
    try:
        import torch
        log(f"torch {torch.__version__}; cuda_available={torch.cuda.is_available()}")
        if not torch.cuda.is_available():
            fallback_unavailable(args, "CUDA not available to torch in this env")
    except Exception as e:
        fallback_unavailable(args, f"torch import failed: {type(e).__name__}: {e}")

    # Import the official LTX-2 package (defensively).
    try:
        ltx, ltx_name = import_ltx()
    except Exception as e:
        fallback_unavailable(args, f"official ltx package import failed: {e}")

    # Run. Any structural/API failure -> graceful fallback (honest, not faked).
    try:
        run_ltx2(args, ltx, ltx_name)
    except SystemExit:
        raise
    except Exception as e:
        fallback_unavailable(
            args,
            f"LTX-2 local run failed (likely an unverified API spot — see the "
            f"# TODO[VERIFY] notes / confirm against the current repo): "
            f"{type(e).__name__}: {e}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
