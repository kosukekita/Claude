#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "torch==2.5.1",
#     "torchvision==0.20.1",
#     "numpy",
#     "diffusers @ git+https://github.com/huggingface/diffusers",
#     "transformers>=4.56",
#     "accelerate",
#     "safetensors",
#     "sentencepiece",
#     "protobuf",
#     "bitsandbytes",
#     "scipy",
#     "compel==2.0.3",
#     "peft",
#     "controlnet-aux",
#     "Pillow",
#     "matplotlib",
#     "opencv-python-headless",
# ]
#
# # Pin torch to the CUDA 12.1 build: this rig's NVIDIA driver is CUDA 12.2
# # (12020), and the default PyPI torch wheels target a newer CUDA runtime and
# # fail with "driver is too old". cu121 wheels run fine on 12.2. See setup.md.
# # torchvision is REQUIRED for FLUX.2's PixtralProcessor and Qwen/CLIP/Siglip
# # image processors (without it they degrade to Placeholder/Pil stubs and
# # FLUX.2 fails to load). Keep it on the same cu121 index as torch.
# [tool.uv.sources]
# torch = { index = "pytorch-cu121" }
# torchvision = { index = "pytorch-cu121" }
#
# [[tool.uv.index]]
# name = "pytorch-cu121"
# url = "https://download.pytorch.org/whl/cu121"
# explicit = true
# ///
"""
generate_image.py — unified LOCAL-FIRST text-to-image generation.

Backends:
  auto  (default)  Probe free VRAM on the local GPUs and pick the best LOCAL
                   model that fits with a safety margin; if no GPU / not enough
                   VRAM / torch+diffusers unavailable, fall back to instructing
                   the caller to use the grok-media skill (cloud, no metering).
  flux             FLUX.1-dev (quality default, ~24-33GB bf16) or, with
                   --fast, FLUX.1-schnell (1-4 step turbo, Apache-2.0).
  sdxl             Stable Diffusion XL base 1.0 (~10-12GB, fast, tiny VRAM).
  grok             Do NOT run locally. Emit the grok-media delegation contract
                   and exit 0 so the agent runs the Grok path via that skill.

Design notes (verified env: 2x RTX A6000 48GB each, ~96GB total; uv at
/home/kita/.local/bin/uv; anaconda libtinfo.so.6 pollutes LD_LIBRARY_PATH and
has broken subprocesses before):
  * Always run via uv (PEP 723 inline deps) in a clean env — never the conda
    python. The shebang uses `uv run --script`. If you must invoke from a
    polluted shell, source scripts/env.sh first so LD_LIBRARY_PATH is cleaned.
  * VRAM-aware tier selection: probe `nvidia-smi --query-gpu=memory.free`,
    compare against a static per-model bf16 table * margin, and descend a fixed
    priority ladder (single-GPU native -> offload -> grok). Choice is LOGGED.
  * grok-media is a REQUIRED SUB-SKILL for the cloud fallback — this script
    never re-implements the Grok CLI; it prints the handoff contract.

Examples:
  generate_image.py --prompt "a neon-lit city at night" --out city.png
  generate_image.py --backend flux --fast --prompt "..." --out fast.png
  generate_image.py --backend sdxl --size 1024x1024 --prompt "..." --out a.png
  generate_image.py --backend auto --prompt "..." --out a.png --offload
  generate_image.py --backend grok --prompt "..."        # emits delegation
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap

# --------------------------------------------------------------------------- #
# Static model table (single source of truth for THIS script).
# vram_bf16_gb = approximate peak VRAM at bf16 incl. text encoder spikes.
# vram_offload_floor_gb = approximate VRAM with model-cpu-offload / 4bit.
# turbo models pin guidance~=0 and few steps; high CFG breaks them.
# --------------------------------------------------------------------------- #
MODELS: dict[str, dict] = {
    "flux.1-dev": {
        "repo": "black-forest-labs/FLUX.1-dev",
        "pipeline": "FluxPipeline",
        "vram_bf16_gb": 33.0,
        "vram_offload_floor_gb": 12.0,
        "default_steps": 40,
        "default_guidance": 3.5,
        "turbo": False,
        "gated": True,
        "license": "FLUX.1 community (non-commercial), GATED on HF",
    },
    "flux.1-krea-dev": {
        # FLUX.1 variant marketed for "aesthetic photography". NOTE (real-world
        # eval 2026-06): on this user's JP daily-snapshot prompts it scored LOW —
        # it tends to render SOCIAL-APP UI SCREENS (Instagram grid / iPhone app
        # list) instead of a plain photo when the prompt mentions iPhone / phone
        # / TikTok / Instagram. NOT a default; left selectable only via explicit
        # --backend flux.1-krea-dev. Preferred image trio = z-image-turbo / Codex
        # (GPT Image) / Grok. See SKILL.md.
        "repo": "black-forest-labs/FLUX.1-Krea-dev",
        "pipeline": "FluxPipeline",
        "vram_bf16_gb": 33.0,
        "vram_offload_floor_gb": 12.0,
        "default_steps": 32,
        "default_guidance": 4.5,
        "turbo": False,
        "gated": True,
        "license": "FLUX.1 community (non-commercial), GATED on HF",
    },
    "flux.1-schnell": {
        "repo": "black-forest-labs/FLUX.1-schnell",
        "pipeline": "FluxPipeline",
        "vram_bf16_gb": 24.0,
        "vram_offload_floor_gb": 12.0,
        "default_steps": 4,
        "default_guidance": 0.0,
        "turbo": True,
        "gated": False,
        "license": "Apache-2.0 (commercial OK)",
    },
    "sdxl": {
        "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "pipeline": "StableDiffusionXLPipeline",
        "vram_bf16_gb": 12.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 30,
        "default_guidance": 7.0,
        "turbo": False,
        "gated": False,
        "license": "CreativeML OpenRAIL++-M",
    },
    "qwen-image": {
        # 20B model: bf16 needs >48GB on a single A6000 (verified OOM at native),
        # so it is set above 48 to FORCE offload on auto/explicit paths.
        "repo": "Qwen/Qwen-Image",
        "pipeline": "QwenImagePipeline",
        "vram_bf16_gb": 56.0,
        "vram_offload_floor_gb": 20.0,
        "default_steps": 50,
        "default_guidance": 4.0,
        "turbo": False,
        "gated": False,
        "license": "Apache-2.0 (commercial OK)",
    },
    "flux.2-dev": {
        # 32B transformer + Mistral3/Pixtral text encoder. Even bf16 + model
        # cpu-offload OOMs on a single 48GB A6000 (verified). REQUIRES 4-bit
        # quantization (bitsandbytes) to fit (~20GB) -> quant_4bit forces it.
        "repo": "black-forest-labs/FLUX.2-dev",
        "pipeline": "Flux2Pipeline",
        "vram_bf16_gb": 64.0,
        "vram_offload_floor_gb": 20.0,
        "default_steps": 28,
        "default_guidance": 3.5,
        "turbo": False,
        "gated": True,
        "quant_4bit": True,             # always load 4-bit on this rig
        "quant_components": ["transformer", "text_encoder"],
        "license": "FLUX.2 community (non-commercial), GATED on HF",
    },
    "z-image-turbo": {
        "repo": "Tongyi-MAI/Z-Image-Turbo",
        "pipeline": "ZImagePipeline",
        "vram_bf16_gb": 16.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 9,             # 9 steps == 8 DiT forwards
        "default_guidance": 0.0,        # distilled w/o CFG; high guidance breaks it
        "turbo": True,
        "gated": False,
        "license": "Apache-2.0 (commercial OK)",
    },
    # Chroma1-HD: FLUX.1-schnell pruned to 8.9B, UNCENSORED BY DESIGN (no NSFW
    # filtering in training). FLUX-class photoreal that produces explicit content
    # raw, no jailbreak/LoRA needed. Fills Z-Image's gap. diffusers git-main.
    "chroma": {
        "repo": "lodestones/Chroma1-HD",
        "pipeline": "ChromaPipeline",
        "vram_bf16_gb": 20.0,
        "vram_offload_floor_gb": 10.0,
        "default_steps": 40,
        "default_guidance": 4.0,        # true CFG sweet spot 3-5; 7+ burns/plastics
        "turbo": False,
        "gated": False,
        "chroma_schedule": True,        # beta-sigmas + dynamic shift (quality)
        "license": "Apache-2.0 (commercial OK)",
    },
    # NoobAI-XL: Illustrious-XL retrained on extended Danbooru2023. ANIME/illustration,
    # native booru tags, the gateway to the huge SDXL LoRA universe Z-Image can't touch.
    # We use the EPS (1.1) variant so the standard SDXL pipeline works out of the box;
    # the v-pred variant needs v_prediction + zero-SNR scheduler config (noobai-xl-vpred).
    "noobai-xl": {
        "repo": "Laxhar/noobai-XL-1.1",
        "pipeline": "StableDiffusionXLPipeline",
        "vram_bf16_gb": 12.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 28,
        "default_guidance": 5.0,
        "turbo": False,
        "gated": False,
        "license": "Fair-AI-public-1.0 (anime; booru tags)",
        "vpred": False,
    },
    # NoobAI-XL v-pred 1.0 — sharper but needs v_prediction + zero-SNR scheduler.
    "noobai-xl-vpred": {
        "repo": "Laxhar/noobai-XL-Vpred-1.0",
        "pipeline": "StableDiffusionXLPipeline",
        "vram_bf16_gb": 12.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 28,
        "default_guidance": 5.0,
        "turbo": False,
        "gated": False,
        "license": "Fair-AI-public-1.0 (anime; booru tags)",
        "vpred": True,
    },
    # Pony Diffusion V6 XL — SDXL-based, the other huge NSFW anime/illustration
    # base (separate lineage from Illustrious/NoobAI). REQUIRES its own score tags
    # in the prompt: `score_9, score_8_up, score_7_up, ...` for quality, and
    # `source_anime / source_pony / source_furry` to steer the style. diffusers
    # format (votepurchase mirror) so it drops into the standard SDXL pipeline.
    "pony": {
        "repo": "votepurchase/ponyDiffusionV6XL",
        "pipeline": "StableDiffusionXLPipeline",
        "vram_bf16_gb": 12.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 28,
        "default_guidance": 7.0,
        "turbo": False,
        "gated": False,
        "license": "Fair-AI-public-1.0 (anime; score tags)",
        "vpred": False,
        # votepurchase/ponyDiffusionV6XL ships model_index.json defaulting to
        # EDMDPMSolverMultistepScheduler, but Pony V6 is a normal eps/scaled_linear
        # SDXL model — the EDM scheduler ignores its betas and produces PURE NOISE.
        # Force a standard Euler (scaled_linear, epsilon) scheduler at load time.
        "force_euler": True,
    },
    # Manga Vision IL — Illustrious-XL (same booru-tag family as NoobAI, uncensored)
    # finetune SPECIALIZED for black-and-white MANGA pages: auto ink + screentones
    # without needing monochrome/greyscale tags. Best for 白黒漫画 NSFW. diffusers
    # format (~6.5GB fp16), drops into the standard SDXL pipeline. eps (no vpred).
    "manga-vision-il": {
        "repo": "John6666/manga-vision-il-v1-sdxl",
        "pipeline": "StableDiffusionXLPipeline",
        "vram_bf16_gb": 12.0,
        "vram_offload_floor_gb": 8.0,
        "default_steps": 28,
        "default_guidance": 6.0,
        "turbo": False,
        "gated": False,
        "license": "Illustrious / Fair-AI (anime/manga; booru tags)",
        "vpred": False,
    },
}

# --------------------------------------------------------------------------- #
# ControlNet registry (SDXL only). Each entry maps a short --control TYPE to the
# HF ControlNet repo + how to PRE-PROCESS a raw image into the control hint.
# xinsir's SDXL ControlNets are the community default (high quality) and are
# already cached on this rig. openpose locks limb count/joint positions; depth
# locks front/back ordering for overlaps (entangled / restraint / multi-person
# panels). Both stack on the same StableDiffusionXLControlNetPipeline.
#   preprocess (the detector run on the source image; can be skipped per-run
#   with --no-control-preprocess when the image is ALREADY a control hint):
#     "openpose" -> controlnet_aux OpenposeDetector (skeleton from a photo/pose)
#     "depth"    -> controlnet_aux MidasDetector / DPT (depth map from an image)
#     "canny"    -> cv2.Canny edge map
# --------------------------------------------------------------------------- #
CONTROLNETS: dict[str, dict] = {
    "openpose": {
        "repo": "xinsir/controlnet-openpose-sdxl-1.0",
        "preprocess": "openpose",
    },
    "depth": {
        "repo": "xinsir/controlnet-depth-sdxl-1.0",
        "preprocess": "depth",
    },
    "canny": {
        "repo": "xinsir/controlnet-canny-sdxl-1.0",
        "preprocess": "canny",
    },
}

# auto ladder: best-quality LOCAL model first, then cheaper/smaller, then grok.
AUTO_LADDER = ["flux.1-dev", "sdxl"]

DEFAULT_MARGIN = 1.1


def log(msg: str) -> None:
    """Human-readable WHY log goes to stderr so stdout stays clean."""
    print(f"[generate_image] {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# VRAM probe
# --------------------------------------------------------------------------- #
def free_vram_gb() -> list[float]:
    """Return free VRAM in GB per GPU via nvidia-smi. [] if unavailable."""
    smi = shutil.which("nvidia-smi")
    if not smi:
        return []
    try:
        out = subprocess.run(
            [smi, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        log(f"nvidia-smi failed: {exc}")
        return []
    if out.returncode != 0:
        log(f"nvidia-smi returned {out.returncode}: {out.stderr.strip()}")
        return []
    gpus: list[float] = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            gpus.append(float(line) / 1024.0)  # MiB -> GiB
        except ValueError:
            continue
    return gpus


def torch_available() -> bool:
    try:
        import torch  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


# --------------------------------------------------------------------------- #
# Backend / model selection
# --------------------------------------------------------------------------- #
def select_model(
    backend: str, fast: bool, want_offload: bool, margin: float
) -> tuple[str | None, bool]:
    """
    Resolve (model_key, offload) for a LOCAL run, or (None, False) to signal
    that the caller should fall back to grok. Logs the reasoning.
    Returns model_key=None ONLY for the grok handoff.
    """
    if backend == "grok":
        return None, False

    gpus = free_vram_gb()
    if gpus:
        log(f"free VRAM per GPU (GB): {[round(g, 1) for g in gpus]}")
    else:
        log("no GPU detected via nvidia-smi (or it is unavailable)")
    best_free = max(gpus) if gpus else 0.0

    # Explicit backend choices ------------------------------------------------
    if backend == "flux":
        key = "flux.1-schnell" if fast else "flux.1-dev"
        return _fit_or_offload(key, best_free, want_offload, margin)

    if backend == "sdxl":
        return _fit_or_offload("sdxl", best_free, want_offload, margin)

    if backend in {"qwen-image", "flux.2-dev", "z-image-turbo", "flux.1-krea-dev",
                   "chroma", "noobai-xl", "noobai-xl-vpred", "manga-vision-il", "pony"}:
        return _fit_or_offload(backend, best_free, want_offload, margin)

    # auto --------------------------------------------------------------------
    if backend == "auto":
        if not torch_available():
            log("torch/diffusers not importable -> cannot run locally")
            return None, False
        if best_free <= 0.0:
            log("no usable GPU VRAM -> falling back to grok")
            return None, False
        ladder = list(AUTO_LADDER)
        if fast:
            # prefer the turbo FLUX in fast mode
            ladder = ["flux.1-schnell"] + [m for m in ladder if m != "flux.1-dev"]
        for key in ladder:
            m = MODELS[key]
            need = m["vram_bf16_gb"] * margin
            if best_free >= need:
                log(
                    f"auto -> {key}: fits native "
                    f"({best_free:.1f}GB free >= {need:.1f}GB needed, margin {margin})"
                )
                return key, False
        # nothing fits native; try offload floor on the smallest model
        for key in reversed(ladder):
            m = MODELS[key]
            floor = m["vram_offload_floor_gb"] * margin
            if best_free >= floor:
                log(
                    f"auto -> {key}: fits with OFFLOAD "
                    f"({best_free:.1f}GB free >= {floor:.1f}GB floor); slower"
                )
                return key, True
        log("auto -> no local model fits even with offload -> grok fallback")
        return None, False

    raise ValueError(f"unknown backend: {backend}")


def _fit_or_offload(
    key: str, best_free: float, want_offload: bool, margin: float
) -> tuple[str | None, bool]:
    """For an explicit local backend, decide native vs offload, or grok."""
    if not torch_available():
        log("torch/diffusers not importable -> cannot run locally -> grok")
        return None, False
    m = MODELS[key]
    need = m["vram_bf16_gb"] * margin
    floor = m["vram_offload_floor_gb"] * margin
    if best_free <= 0.0:
        log(f"{key}: no GPU VRAM available -> grok fallback")
        return None, False
    if want_offload:
        log(f"{key}: offload requested by --offload")
        return key, True
    if best_free >= need:
        log(f"{key}: fits native ({best_free:.1f}GB >= {need:.1f}GB)")
        return key, False
    if best_free >= floor:
        log(
            f"{key}: too tight for native ({best_free:.1f}GB < {need:.1f}GB) "
            f"-> enabling OFFLOAD (>= {floor:.1f}GB floor); slower"
        )
        return key, True
    log(
        f"{key}: insufficient VRAM even for offload "
        f"({best_free:.1f}GB < {floor:.1f}GB) -> grok fallback"
    )
    return None, False


# --------------------------------------------------------------------------- #
# grok-media delegation (NOT a re-implementation — REQUIRED SUB-SKILL)
# --------------------------------------------------------------------------- #
def emit_grok_delegation(prompt: str, out: str, reason: str) -> None:
    msg = textwrap.dedent(
        f"""
        ============================================================
        LOCAL image generation not available -> use grok-media skill
        ============================================================
        reason: {reason}

        Do NOT re-implement the Grok CLI here. Follow the grok-media skill
        for ALL of: auth gate, clean-dir execution, NL tool-naming, and
        session-dir output recovery. Contract:

          0. Auth gate (run first):
               "$HOME/.grok/bin/grok.exe" models 2>&1 | head -3
             If "You are not authenticated.", ask the user to run
             `login --device-auth` in their own terminal. Do not automate.

          1. Clean dir:  WORK="$(mktemp -d)"; cd "$WORK"

          2. Generate (name the built-in tool in natural language):
               "$HOME/.grok/bin/grok.exe" -p \\
                 'Use your image_gen tool to create an image: {prompt}'

          3. Recover output (it is NOT in cwd; it lands under the session dir):
               "$HOME/.grok/bin/grok.exe" -r -p \\
                 'What is the absolute file path of the image you just generated? Reply with ONLY the path.'
             or glob:
               ls -t "$HOME/.grok/sessions/"*"/"*"/images/"*.jpg 2>/dev/null | head -3

          4. Copy the recovered image to: {out}
             then deliver with SendUserFile.

        (An empty CLI response does NOT mean failure — always verify via step 3.)
        ============================================================
        """
    ).strip()
    print(msg)


# --------------------------------------------------------------------------- #
# Local generation
# --------------------------------------------------------------------------- #
def parse_size(size: str) -> tuple[int, int]:
    """Parse WxH; round each dim down to a multiple of 16 (SDXL/FLUX safe)."""
    s = size.lower().replace("×", "x").strip()
    if "x" not in s:
        raise argparse.ArgumentTypeError(f"--size must be WxH, got {size!r}")
    w_str, h_str = s.split("x", 1)
    w, h = int(w_str), int(h_str)
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError(f"--size dims must be positive: {size!r}")
    rw, rh = (w // 16) * 16, (h // 16) * 16
    if (rw, rh) != (w, h):
        log(f"rounded --size {w}x{h} -> {rw}x{rh} (multiple of 16)")
    return rw, rh


def _expand_weights(
    weights: list[float] | None, n: int, default: float
) -> list[float]:
    """Normalize a per-item weight list to length n.

    A single value applies to all items; a short list is padded with `default`;
    a long list is truncated. Shared by --lora-scale and --control-weight so the
    two paths normalize identically.
    """
    out = list(weights or [])
    if len(out) == 1:
        out = out * n
    out = out[:n]
    while len(out) < n:
        out.append(default)
    return out


def _parse_control_specs(
    control: list[str] | None,
) -> list[tuple[str, str]]:
    """Parse --control specs into (type, image_path) pairs.

    Accepted forms (repeatable):
      --control openpose=pose.png   explicit type
      --control depth=ref.jpg
      --control pose.png            bare path -> defaults to openpose
    """
    specs: list[tuple[str, str]] = []
    for raw in control or []:
        if "=" in raw:
            ctype, path = raw.split("=", 1)
            ctype = ctype.strip().lower()
        else:
            ctype, path = "openpose", raw
        if ctype not in CONTROLNETS:
            raise argparse.ArgumentTypeError(
                f"--control type {ctype!r} unknown; choose from {list(CONTROLNETS)}"
            )
        path = path.strip()
        if not os.path.isfile(path):
            raise argparse.ArgumentTypeError(f"--control image not found: {path}")
        specs.append((ctype, path))
    return specs


def _prepare_control_hint(ctype: str, path: str, width: int, height: int,
                          preprocess: bool):
    """Turn a source image into the control hint for ControlNet.

    If preprocess is True, run the matching controlnet_aux detector (skeleton /
    depth / canny). If False, the image is assumed to ALREADY be a control hint
    (e.g. a hand-made OpenPose skeleton) and is only resized. Returns a PIL.Image.
    """
    from PIL import Image  # noqa: PLC0415

    img = Image.open(path).convert("RGB")
    if not preprocess:
        log(f"control[{ctype}]: using {path} as a pre-made hint (no detector)")
        return img.resize((width, height))

    pp = CONTROLNETS[ctype]["preprocess"]
    if pp == "openpose":
        from controlnet_aux import OpenposeDetector  # noqa: PLC0415
        det = OpenposeDetector.from_pretrained("lllyasviel/Annotators")
        hint = det(img, hand_and_face=True)
    elif pp == "depth":
        from controlnet_aux import MidasDetector  # noqa: PLC0415
        det = MidasDetector.from_pretrained("lllyasviel/Annotators")
        hint = det(img)
    elif pp == "canny":
        import cv2  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415
        arr = cv2.Canny(np.array(img), 100, 200)
        hint = Image.fromarray(arr).convert("RGB")
    else:
        raise ValueError(f"no preprocessor for {ctype}")
    log(f"control[{ctype}]: preprocessed {path} with {pp} detector")
    return hint.resize((width, height))


def run_local(
    key: str,
    offload: bool,
    prompt: str,
    negative: str | None,
    width: int,
    height: int,
    steps: int | None,
    guidance: float | None,
    seed: int | None,
    out: str,
    lora: list[str] | None = None,
    lora_scale: list[float] | None = None,
    control: list[str] | None = None,
    control_weight: list[float] | None = None,
    control_preprocess: bool = True,
) -> int:
    import torch  # noqa: PLC0415
    from diffusers import (  # noqa: PLC0415
        FluxPipeline,
        StableDiffusionXLPipeline,
    )

    m = MODELS[key]
    repo = m["repo"]
    want_cls = m["pipeline"]

    # --- ControlNet gating ----------------------------------------------------
    # ControlNet is SDXL-only here. If --control is given on a non-SDXL backend,
    # warn and ignore it (the base run still proceeds). On SDXL, we build a
    # StableDiffusionXLControlNetPipeline instead of the plain SDXL pipeline.
    control_specs: list[tuple[str, str]] = _parse_control_specs(control)
    if control_specs and want_cls != "StableDiffusionXLPipeline":
        log(f"{key}: --control ignored ({want_cls} is not an SDXL pipeline)")
        control_specs = []
    use_controlnet = bool(control_specs)

    # The newer pipelines (Qwen-Image, FLUX.2, Z-Image) are diffusers git-main
    # only. Import them lazily/defensively so older diffusers still loads the
    # FLUX/SDXL paths, and we give a clear message + grok fallback if missing.
    extra_cls: dict = {}
    if want_cls not in {"FluxPipeline", "StableDiffusionXLPipeline"}:
        try:
            import diffusers as _df  # noqa: PLC0415
            cls = getattr(_df, want_cls, None)
            if cls is None:
                raise ImportError(want_cls)
            extra_cls[want_cls] = cls
        except Exception as exc:  # noqa: BLE001
            log(
                f"{want_cls} not available in this diffusers build ({exc}); "
                f"need diffusers git-main. Falling back to grok-media."
            )
            emit_grok_delegation(prompt, out, f"{want_cls} unavailable: {exc}")
            return 0
    if steps is None:
        steps = m["default_steps"]
    if guidance is None:
        guidance = m["default_guidance"]
    if m["turbo"] and guidance and guidance > 1.0:
        log(
            f"WARNING: {key} is a turbo model; guidance {guidance} is too high. "
            f"Forcing guidance=0.0 (high CFG breaks turbo)."
        )
        guidance = 0.0

    log(
        f"loading {key} ({repo}); offload={offload}; "
        f"{width}x{height}; steps={steps}; guidance={guidance}"
    )

    pipe_cls = {
        "FluxPipeline": FluxPipeline,
        "StableDiffusionXLPipeline": StableDiffusionXLPipeline,
        **extra_cls,
    }[want_cls]

    from_kwargs: dict = {"torch_dtype": torch.bfloat16}
    # Z-Image's loader is happier with low_cpu_mem_usage disabled (per model card).
    if want_cls == "ZImagePipeline":
        from_kwargs["low_cpu_mem_usage"] = False

    # --- ControlNet: load the control models and swap to the CN-aware SDXL
    # pipeline. We pass the ControlNetModel(s) into from_pretrained so the rest
    # of the load path (scheduler swap, LoRA fuse, compel, offload) is identical
    # to the plain SDXL path below — only the pipeline class and the call kwargs
    # differ. Build control hints AFTER we know the target size.
    # nets holds one (ControlNetModel, hint_image, weight) tuple per --control,
    # so the parallel model/hint/weight arrays stay aligned by construction.
    nets: list[tuple] = []
    if use_controlnet:
        from diffusers import (  # noqa: PLC0415
            ControlNetModel,
            StableDiffusionXLControlNetPipeline,
        )
        weights = _expand_weights(control_weight, len(control_specs), 0.9)
        for (ctype, cpath), w in zip(control_specs, weights):
            cn_repo = CONTROLNETS[ctype]["repo"]
            model = ControlNetModel.from_pretrained(cn_repo, torch_dtype=torch.bfloat16)
            hint = _prepare_control_hint(ctype, cpath, width, height, control_preprocess)
            nets.append((model, hint, w))
            log(f"{key}: ControlNet {ctype} ({cn_repo}) weight={w}")
        pipe_cls = StableDiffusionXLControlNetPipeline
        models = [n[0] for n in nets]
        from_kwargs["controlnet"] = models[0] if len(models) == 1 else models

    # 4-bit quantization (bitsandbytes) for models too big for 48GB even with
    # offload (e.g. FLUX.2-dev, 32B+Mistral3). Quantizes the heavy components
    # to ~NF4 so the pipeline fits, then still uses cpu-offload for headroom.
    if m.get("quant_4bit"):
        try:
            from diffusers import PipelineQuantizationConfig  # noqa: PLC0415
            comps = m.get("quant_components", ["transformer", "text_encoder"])
            from_kwargs["quantization_config"] = PipelineQuantizationConfig(
                quant_backend="bitsandbytes_4bit",
                quant_kwargs={
                    "load_in_4bit": True,
                    "bnb_4bit_quant_type": "nf4",
                    "bnb_4bit_compute_dtype": torch.bfloat16,
                },
                components_to_quantize=comps,
            )
            log(f"{key}: loading with bitsandbytes 4-bit NF4 (components={comps})")
            offload = True  # 4-bit still benefits from offload headroom
        except Exception as exc:  # noqa: BLE001
            log(f"{key}: 4-bit quantization unavailable ({exc}); trying bf16+offload")

    pipe = pipe_cls.from_pretrained(repo, **from_kwargs)

    # v-prediction models (e.g. NoobAI-XL v-pred) need the scheduler switched to
    # v_prediction + zero-terminal-SNR, else output is pure noise. Reconfigure
    # the loaded scheduler in place from its own config.
    if m.get("vpred"):
        pipe.scheduler = pipe.scheduler.from_config(
            pipe.scheduler.config,
            prediction_type="v_prediction",
            rescale_betas_zero_snr=True,
        )
        log(f"{key}: scheduler set to v_prediction + zero-SNR")

    # Some SDXL checkpoints (e.g. Pony V6) ship a model_index.json that defaults to
    # EDMDPMSolverMultistepScheduler, which silently ignores the model's scaled_linear
    # betas and renders pure rainbow noise. Swap to a vanilla Euler scheduler built
    # from the standard SDXL beta schedule (epsilon, scaled_linear).
    if m.get("force_euler"):
        from diffusers import EulerDiscreteScheduler  # noqa: PLC0415
        pipe.scheduler = EulerDiscreteScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            prediction_type="epsilon",
            steps_offset=1,
            timestep_spacing="leading",
        )
        log(f"{key}: scheduler forced to EulerDiscreteScheduler (eps/scaled_linear)")

    # Chroma's stock FlowMatchEuler runs uniform sigmas with no shift, which is
    # the main cause of soft/low-quality output. Switch to beta sigmas + flux-style
    # dynamic shifting (base 0.5 / max 1.15) — the diffusers equivalent of ComfyUI's
    # recommended beta+shift~1 schedule. Big quality win.
    if m.get("chroma_schedule"):
        try:
            from diffusers import FlowMatchEulerDiscreteScheduler  # noqa: PLC0415
            pipe.scheduler = FlowMatchEulerDiscreteScheduler.from_config(
                pipe.scheduler.config,
                use_beta_sigmas=True,
                use_dynamic_shifting=True,
                base_shift=0.5,
                max_shift=1.15,
            )
            log(f"{key}: scheduler -> FlowMatchEuler beta-sigmas + dynamic shift")
        except Exception as exc:  # noqa: BLE001
            log(f"{key}: chroma scheduler tweak failed ({exc}); using stock scheduler")

    # Stack character/style LoRAs on SDXL backends (Pony/NoobAI/SDXL). diffusers
    # loads each as a named adapter, then fuses them with per-LoRA weights so the
    # base weights carry the LoRA at inference (no runtime adapter dispatch). Must
    # happen AFTER scheduler swaps and BEFORE offload/to(cuda) so the fused weights
    # land on the right device. Non-SDXL pipelines ignore --lora with a warning.
    if lora:
        if want_cls != "StableDiffusionXLPipeline":
            log(f"{key}: --lora ignored ({want_cls} is not an SDXL pipeline)")
        else:
            if lora_scale and len(lora_scale) not in (1, len(lora)):
                log(
                    f"{key}: {len(lora_scale)} --lora-scale for {len(lora)} --lora; "
                    f"padding/truncating to match"
                )
            scales = _expand_weights(lora_scale, len(lora), 1.0)
            names = []
            for i, lp in enumerate(lora):
                adapter = f"lora_{i}"
                pipe.load_lora_weights(lp, adapter_name=adapter)
                names.append(adapter)
                log(f"{key}: loaded LoRA {adapter}={lp} scale={scales[i]}")
            pipe.set_adapters(names, adapter_weights=scales[: len(names)])
            pipe.fuse_lora(adapter_names=names, lora_scale=1.0)
            pipe.unload_lora_weights()
            log(f"{key}: fused {len(names)} LoRA(s) into base weights")

    if offload:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    gen = None
    if seed is not None:
        gen = torch.Generator("cpu").manual_seed(seed)

    kwargs: dict = {
        "height": height,
        "width": width,
        "num_inference_steps": steps,
        "guidance_scale": guidance,
    }
    if gen is not None:
        kwargs["generator"] = gen

    # ControlNet call kwargs: the SDXL ControlNet pipeline takes `image` as the
    # control hint(s) and `controlnet_conditioning_scale` as the per-net weight.
    if use_controlnet:
        hints = [n[1] for n in nets]
        cn_weights = [n[2] for n in nets]
        kwargs["image"] = hints[0] if len(hints) == 1 else hints
        kwargs["controlnet_conditioning_scale"] = (
            cn_weights[0] if len(cn_weights) == 1 else cn_weights
        )

    # --- Long-prompt handling for SDXL (Pony/NoobAI/Manga-Vision/SDXL) --------
    # CLIP truncates at 77 tokens; Pony-style prompts (score tags + character
    # block + outfit + pose + background + lighting) routinely exceed that and
    # the tail (outfit/pose/background) gets silently dropped. compel chunks the
    # prompt into 77-token windows and concatenates the embeddings, so nothing
    # is lost. Pony's own docs recommend compel weighting for exactly this. We
    # only engage it for SDXL pipelines (dual encoder + pooled output); FLUX /
    # Qwen / Z-Image / Chroma keep their native prompt path.
    used_compel = False
    if want_cls == "StableDiffusionXLPipeline":
        try:
            from compel import Compel, ReturnedEmbeddingsType  # noqa: PLC0415

            compel = Compel(
                tokenizer=[pipe.tokenizer, pipe.tokenizer_2],
                text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
                returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
                requires_pooled=[False, True],
                truncate_long_prompts=False,
            )
            prompt_embeds, pooled_prompt_embeds = compel(prompt)
            embeds = {
                "prompt_embeds": prompt_embeds,
                "pooled_prompt_embeds": pooled_prompt_embeds,
            }
            if negative:
                negative_prompt_embeds, negative_pooled_prompt_embeds = compel(negative)
                # pad +/- to equal length so diffusers can stack them
                prompt_embeds, negative_prompt_embeds = (
                    compel.pad_conditioning_tensors_to_same_length(
                        [prompt_embeds, negative_prompt_embeds]
                    )
                )
                embeds["prompt_embeds"] = prompt_embeds
                embeds["negative_prompt_embeds"] = negative_prompt_embeds
                embeds["negative_pooled_prompt_embeds"] = negative_pooled_prompt_embeds
            kwargs.update(embeds)
            used_compel = True
            log(f"{key}: compel long-prompt embeddings (no 77-token truncation)")
        except Exception as exc:  # noqa: BLE001
            log(f"{key}: compel unavailable ({exc}); falling back to truncated prompt")

    if not used_compel:
        kwargs["prompt"] = prompt
        # FLUX(.1/.2) ignore negative_prompt; SDXL / Qwen-Image / Z-Image / Chroma accept it.
        if negative and want_cls in {
            "StableDiffusionXLPipeline", "QwenImagePipeline", "ZImagePipeline",
            "ChromaPipeline",
        }:
            kwargs["negative_prompt"] = negative

    image = pipe(**kwargs).images[0]
    out_dir = os.path.dirname(os.path.abspath(out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    image.save(out)
    log(f"saved -> {os.path.abspath(out)}")
    print(os.path.abspath(out))
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_image.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Unified LOCAL-FIRST text-to-image generation (diffusers), with
            VRAM-aware tier selection + offload, falling back to grok-media
            when local cannot run.

            Backends:
              auto   probe VRAM, pick best fitting local model, else grok
              flux   FLUX.1-dev (or --fast -> FLUX.1-schnell turbo)
              sdxl   Stable Diffusion XL base 1.0 (small/fast)
              grok   delegate to the grok-media skill (cloud, no metering)
            """
        ),
        epilog=textwrap.dedent(
            """\
            examples:
              %(prog)s --prompt "a cat astronaut" --out cat.png
              %(prog)s --backend flux --fast --prompt "..." --out f.png
              %(prog)s --backend sdxl --size 768x1344 --prompt "..." --out s.png
              %(prog)s --backend grok --prompt "..."      # prints handoff

            env/clean-run note: run via `uv run` (PEP723 deps). If your shell
            has anaconda's libtinfo on LD_LIBRARY_PATH, source scripts/env.sh
            first to avoid subprocess breakage.
            """
        ),
    )
    p.add_argument(
        "--backend",
        choices=[
            "auto", "flux", "sdxl", "grok", "openrouter",
            "qwen-image", "flux.2-dev", "z-image-turbo", "flux.1-krea-dev",
            "chroma", "noobai-xl", "noobai-xl-vpred", "manga-vision-il", "pony",
        ],
        default="auto",
        help="generation backend (default: auto). qwen-image/flux.2-dev/"
             "z-image-turbo/chroma need diffusers git-main. chroma=uncensored "
             "photoreal base; noobai-xl=anime/booru SDXL. openrouter=explicit "
             "cloud API (key in ~/.config/openrouter.key), use --or-model to "
             "pick the model; NOT part of the auto ladder.",
    )
    p.add_argument(
        "--or-model",
        default="google/gemini-2.5-flash-image-preview",
        dest="or_model",
        help="OpenRouter image-output model id (only with --backend openrouter; "
             "default: google/gemini-2.5-flash-image-preview)",
    )
    p.add_argument("--prompt", required=True, help="text prompt")
    p.add_argument("--negative-prompt", default=None, help="negative prompt (SDXL)")
    p.add_argument("--out", default="image.png", help="output PNG path")
    p.add_argument(
        "--size",
        type=str,
        default="1024x1024",
        help="WxH, e.g. 1024x1024 (rounded to multiple of 16)",
    )
    p.add_argument(
        "--fast",
        action="store_true",
        help="prefer a turbo model (FLUX.1-schnell) for speed",
    )
    p.add_argument(
        "--offload",
        action="store_true",
        help="force CPU offload (slower, lower VRAM) for explicit backends",
    )
    p.add_argument("--steps", type=int, default=None, help="override inference steps")
    p.add_argument("--guidance", type=float, default=None, help="override guidance scale")
    p.add_argument("--seed", type=int, default=None, help="random seed (reproducible)")
    p.add_argument(
        "--lora",
        action="append",
        default=None,
        metavar="PATH",
        help="LoRA .safetensors to stack on an SDXL backend (Pony/NoobAI/SDXL). "
        "Repeatable for multiple LoRAs. Ignored by non-SDXL pipelines.",
    )
    p.add_argument(
        "--lora-scale",
        type=float,
        action="append",
        default=None,
        metavar="W",
        help="weight per --lora (same order). Single value applies to all. Default 1.0.",
    )
    p.add_argument(
        "--control",
        action="append",
        default=None,
        metavar="TYPE=IMG",
        help="ControlNet hint for SDXL backends, e.g. openpose=pose.png or "
        "depth=ref.jpg (bare path defaults to openpose). Repeatable to STACK "
        "multiple ControlNets (openpose+depth is the default for complex / "
        "entangled / multi-person panels). Ignored by non-SDXL pipelines.",
    )
    p.add_argument(
        "--control-weight",
        type=float,
        action="append",
        default=None,
        metavar="W",
        help="conditioning scale per --control (same order). Single value "
        "applies to all. Default 0.9.",
    )
    p.add_argument(
        "--no-control-preprocess",
        action="store_true",
        help="treat each --control image as an ALREADY-MADE hint (skeleton/depth "
        "map) and skip the detector. Default: run the matching detector.",
    )
    p.add_argument(
        "--margin",
        type=float,
        default=DEFAULT_MARGIN,
        help=f"VRAM safety margin multiplier (default {DEFAULT_MARGIN})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="only resolve and log the backend choice; do not generate",
    )
    return p


def delegate_openrouter_image(args) -> int:
    """Explicit, user-named cloud path. Shell out to cloud_openrouter.py so the
    OpenRouter key/HTTP logic lives in ONE place; this script stays local-only."""
    import subprocess  # noqa: PLC0415

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "cloud_openrouter.py")
    cmd = [script, "image", "--model", args.or_model,
           "--prompt", args.prompt, "--out", args.out]
    log(f"backend=openrouter -> delegating to cloud_openrouter.py (model {args.or_model})")
    return subprocess.call(cmd)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.backend == "openrouter":
        return delegate_openrouter_image(args)

    try:
        width, height = parse_size(args.size)
        # Validate --control here (same layer as --size) so a bad type / missing
        # image fails fast with exit 2, instead of raising inside run_local and
        # getting swallowed by the generic except -> spurious grok fallback.
        _parse_control_specs(args.control)
    except argparse.ArgumentTypeError as exc:
        log(str(exc))
        return 2

    model_key, offload = select_model(
        backend=args.backend,
        fast=args.fast,
        want_offload=args.offload,
        margin=args.margin,
    )

    if model_key is None:
        # grok handoff (explicit --backend grok, or local impossible)
        reason = (
            "user requested --backend grok"
            if args.backend == "grok"
            else "no local backend can run (VRAM/deps); see log above"
        )
        emit_grok_delegation(args.prompt, args.out, reason)
        return 0

    if args.dry_run:
        log(f"DRY RUN: would generate with {model_key} (offload={offload})")
        print(f"backend={model_key} offload={offload}")
        return 0

    try:
        return run_local(
            key=model_key,
            offload=offload,
            prompt=args.prompt,
            negative=args.negative_prompt,
            width=width,
            height=height,
            steps=args.steps,
            guidance=args.guidance,
            seed=args.seed,
            out=args.out,
            lora=args.lora,
            lora_scale=args.lora_scale,
            control=args.control,
            control_weight=args.control_weight,
            control_preprocess=not args.no_control_preprocess,
        )
    except Exception as exc:  # noqa: BLE001
        log(f"LOCAL generation failed: {type(exc).__name__}: {exc}")
        log("falling back to grok-media delegation")
        emit_grok_delegation(
            args.prompt, args.out, f"local run raised {type(exc).__name__}: {exc}"
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
