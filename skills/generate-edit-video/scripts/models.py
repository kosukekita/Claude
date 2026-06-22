#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Single source of truth for the model matrix used by this skill.

This module is PURE DATA + a thin ``get()`` accessor. It has NO heavy imports
(no torch / diffusers), NO side effects at import time, and uses the standard
library only. It is imported by:

  * scripts/gen_video.py   -> calls models.get(model_id) for the video matrix
                              (falls back to its own builtin mirror if absent).
  * scripts/probe_backend.py (optional) -> reads the same matrix to decide the
                              backend (local-single / local-offload / cloud / ...).
  * reference/models.md    -> documents one authoritative table.
  * scripts/gen_image.py / probe_backend.py -> read the local image entries.

Keys/values for the video models mirror gen_video.py's FALLBACK_MODELS EXACTLY
so the two never drift. ``get()`` returns a deep-ish COPY (so callers can mutate
freely) or ``None`` for an unknown id.

Run ``uv run scripts/models.py`` to dump the whole table as JSON.
"""

from __future__ import annotations

import copy
import json

# --------------------------------------------------------------------------- #
# VIDEO MODEL MATRIX (authoritative; mirrors gen_video.py FALLBACK_MODELS)
# --------------------------------------------------------------------------- #
# task:     t2v | i2v
# pipeline: wan | ltx (which diffusers family) ; ltx2 => defer to gen_video_ltx2.py
# vram_*_gb are per-clip single-card peaks INCLUDING text-encoder spikes.
# frame_rule is a (multiple, remainder) tuple: num_frames % multiple == remainder.
# dim_multiple is the spatial rounding for width/height.
# --------------------------------------------------------------------------- #
MODELS: dict[str, dict] = {
    # --- Wan (diffusers) ----------------------------------------------------- #
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
    # --- LTX-Video 0.9.x (diffusers) ---------------------------------------- #
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
    # --- LTX-2.3 (NOT in diffusers; defer to gen_video_ltx2.py) ------------- #
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

# Per-task default model (mirrors gen_video.py DEFAULT_MODEL_FOR_TASK).
DEFAULT_MODEL_FOR_TASK = {
    "t2v": "wan2.1-t2v-1.3b",   # fast, fits trivially, good iteration default
    "i2v": "wan2.2-i2v-a14b",   # quality default; on 48GB use fp8/offload
}

# --------------------------------------------------------------------------- #
# LOCAL IMAGE MODELS (reference table for reference/models.md + probe_backend)
# --------------------------------------------------------------------------- #
# `local_impl` flags whether gen_image.py actually implements the model locally.
# Implemented locally: FLUX.1-dev, FLUX.1-schnell, SDXL.
# Reference-only (NOT implemented locally -> route to cloud/Grok):
#   Z-Image-Turbo, Qwen-Image, FLUX.2-dev, SD3.5-Large.
# vram_bf16_gb = approx peak VRAM at bf16 incl. text-encoder spikes.
# vram_offload_floor_gb = approx VRAM with model-cpu-offload / 4bit.
# These mirror gen_image.py MODELS for the implemented ones (do not drift).
# --------------------------------------------------------------------------- #
IMAGE_MODELS: dict[str, dict] = {
    # --- implemented locally by gen_image.py -------------------------------- #
    "flux.1-dev": {
        "task": "t2i", "pipeline": "FluxPipeline",
        "repo": "black-forest-labs/FLUX.1-dev",
        "vram_bf16_gb": 33.0, "vram_offload_floor_gb": 12.0,
        "default_steps": 40, "default_guidance": 3.5,
        "turbo": False, "gated": True, "local_impl": True,
        "license": "FLUX.1 community (non-commercial), GATED on HF",
        "vram_note": "~24-33GB bf16; fits one A6000; ~12GB with cpu-offload/4bit.",
    },
    "flux.1-schnell": {
        "task": "t2i", "pipeline": "FluxPipeline",
        "repo": "black-forest-labs/FLUX.1-schnell",
        "vram_bf16_gb": 24.0, "vram_offload_floor_gb": 12.0,
        "default_steps": 4, "default_guidance": 0.0,
        "turbo": True, "gated": False, "local_impl": True,
        "license": "Apache-2.0 (commercial OK)",
        "vram_note": "1-4 step turbo, ~24GB bf16; ~12GB offload. guidance pinned ~0.",
    },
    "sdxl": {
        "task": "t2i", "pipeline": "StableDiffusionXLPipeline",
        "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "vram_bf16_gb": 12.0, "vram_offload_floor_gb": 8.0,
        "default_steps": 30, "default_guidance": 7.0,
        "turbo": False, "gated": False, "local_impl": True,
        "license": "CreativeML OpenRAIL++-M",
        "vram_note": "~10-12GB bf16, fast and tiny; ~8GB offload.",
    },
    # --- reference-only: NOT implemented locally -> cloud/Grok -------------- #
    "z-image-turbo": {
        "task": "t2i", "pipeline": None,
        "repo": "Tongyi-MAI/Z-Image-Turbo",
        "vram_bf16_gb": 13.0, "vram_offload_floor_gb": 8.0,
        "default_steps": 8, "default_guidance": 1.0,
        "turbo": True, "gated": False, "local_impl": False,
        "license": "Apache-2.0 (commercial OK)",
        "vram_note": "6B turbo, ~13GB bf16; few-step. Not wired locally -> cloud/Grok.",
    },
    "qwen-image": {
        "task": "t2i", "pipeline": None,
        "repo": "Qwen/Qwen-Image",
        "vram_bf16_gb": 40.0, "vram_offload_floor_gb": 20.0,
        "default_steps": 50, "default_guidance": 4.0,
        "turbo": False, "gated": False, "local_impl": False,
        "license": "Apache-2.0 (commercial OK)",
        "vram_note": "20B MMDiT, ~40GB+ bf16 (tight on 48GB); strong text. -> cloud/Grok.",
    },
    "flux.2-dev": {
        "task": "t2i", "pipeline": None,
        "repo": "black-forest-labs/FLUX.2-dev",
        "vram_bf16_gb": 64.0, "vram_offload_floor_gb": 24.0,
        "default_steps": 40, "default_guidance": 3.5,
        "turbo": False, "gated": True, "local_impl": False,
        "license": "FLUX.2 community (non-commercial), GATED on HF",
        "vram_note": "~32B, >48GB bf16 single-card -> needs offload/multi/cloud. -> cloud/Grok.",
    },
    "sd3.5-large": {
        "task": "t2i", "pipeline": None,
        "repo": "stabilityai/stable-diffusion-3.5-large",
        "vram_bf16_gb": 18.0, "vram_offload_floor_gb": 10.0,
        "default_steps": 28, "default_guidance": 3.5,
        "turbo": False, "gated": True, "local_impl": False,
        "license": "Stability Community License (GATED on HF)",
        "vram_note": "8B MMDiT, ~18GB bf16; ~10GB offload. Not wired locally -> cloud/Grok.",
    },
}

# Unified lookup so get() resolves both video and image ids from one table.
_ALL: dict[str, dict] = {}
_ALL.update(MODELS)
_ALL.update(IMAGE_MODELS)


def get(model_id: str):
    """Return a COPY of the spec for ``model_id`` (video or image), or None.

    A deep copy is returned so callers may freely mutate (e.g. setdefault
    'family'/'pipeline') without corrupting this module's tables. The
    frame_rule tuple is preserved as a tuple.
    """
    spec = _ALL.get(model_id)
    if spec is None:
        return None
    return copy.deepcopy(spec)


def all_ids() -> list:
    """All known model ids (video first, then image), preserving insertion order."""
    return list(_ALL.keys())


def _json_default(o):
    # tuples already serialize as JSON arrays; this is just a safety net.
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(f"not JSON serializable: {type(o)!r}")


if __name__ == "__main__":
    out = {
        "video_models": MODELS,
        "default_model_for_task": DEFAULT_MODEL_FOR_TASK,
        "image_models": IMAGE_MODELS,
    }
    print(json.dumps(out, indent=2, default=_json_default, ensure_ascii=False))
