#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
#   "transformers>=4.56",
#   "accelerate",
#   "safetensors",
#   "peft",
#   "compel==2.0.3",
#   "opencv-python-headless",
#   "numpy",
#   "Pillow",
# ]
#
# # Pin torch to the cu121 build: this rig's NVIDIA driver is CUDA 12.2 (12020);
# # default PyPI wheels target a newer CUDA runtime and fail "driver too old".
# [tool.uv.sources]
# torch = { index = "pytorch-cu121" }
# torchvision = { index = "pytorch-cu121" }
#
# [[tool.uv.index]]
# name = "pytorch-cu121"
# url = "https://download.pytorch.org/whl/cu121"
# explicit = true
# ///
"""Face-only inpaint to enforce CHARACTER CONSISTENCY across panels.

The 1st-stage image (gen_image.py, weak LoRA, weak face control) has the right
pose/outfit/background but the FACE (=character identity) drifts panel to panel.
This re-paints ONLY the detected face region with the same character LoRA applied
STRONGLY, at a MID denoise strength so the face's orientation/hair stay from the
source while the features get re-drawn into the LoRA's face.

Why mid strength (0.4-0.5), not 1.0 or 0.1:
  1.0 = repaint face from scratch -> identity matches but ORIENTATION breaks
        (a frontal face pasted onto a 3/4 turned head).
  0.1 = barely perturb -> the drifted source face survives, identity NOT fixed.
  0.4-0.5 = keep orientation/hair from source, swap the features into the LoRA face.

Pipeline mirrors gen_image.py's pony path exactly: Euler (eps/scaled_linear)
scheduler, LoRA fuse, compel long-prompt embeddings.

Usage:
  face_inpaint.py --in p1.png --out p1_fixed.png \
      --lora .../msnpcr1woman_pony_v1.safetensors --lora-scale 0.9 \
      --prompt "score_9, score_8_up, ..., source_anime, msnpcr1woman, <face descriptors>" \
      --negative-prompt "..." --strength 0.45 --steps 30 --guidance 5
"""
from __future__ import annotations

import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image

PONY_REPO = "votepurchase/ponyDiffusionV6XL"
YUNET = "/home/kita/.claude/skills/video-media-studio/scripts/models/face_detection_yunet_2023mar.onnx"


def log(m: str) -> None:
    print(m, file=sys.stderr, flush=True)


def detect_faces(model_path: str, bgr: np.ndarray, score_min: float) -> np.ndarray:
    h, w = bgr.shape[:2]
    det = cv2.FaceDetectorYN.create(model_path, "", (w, h))
    det.setInputSize((w, h))
    det.setScoreThreshold(float(score_min))
    _, faces = det.detect(bgr)
    if faces is not None and len(faces):
        return faces
    # fall back to looser thresholds (profile / partial faces)
    for s in (0.5, 0.4, 0.3):
        det.setScoreThreshold(s)
        _, faces = det.detect(bgr)
        if faces is not None and len(faces):
            log(f"face found at lowered score {s}")
            return faces
    return np.empty((0, 15), np.float32)


def build_face_mask(
    bgr: np.ndarray, faces: np.ndarray, expand: float, feather_frac: float
) -> tuple[Image.Image, int]:
    """White (inpaint) over each face as a feathered ellipse on a black canvas."""
    H, W = bgr.shape[:2]
    mask = np.zeros((H, W), np.float32)
    n = 0
    for f in faces:
        x, y, fw, fh = float(f[0]), float(f[1]), float(f[2]), float(f[3])
        ex, ey = fw * expand, fh * expand
        x0 = max(0, int(x - ex)); y0 = max(0, int(y - ey))
        x1 = min(W, int(x + fw + ex)); y1 = min(H, int(y + fh + ey))
        bw, bh = x1 - x0, y1 - y0
        if bw < 8 or bh < 8:
            continue
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        cv2.ellipse(mask, (cx, cy), (bw // 2, bh // 2), 0, 0, 360, 1.0, -1)
        n += 1
    if n:
        feather = int(max(H, W) * feather_frac) | 1
        feather = max(11, feather)
        mask = cv2.GaussianBlur(mask, (feather, feather), 0)
    m8 = (np.clip(mask, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(m8), n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", required=True,
                    help="MUST contain the LoRA trigger + score tags + face descriptors")
    ap.add_argument("--negative-prompt", dest="negative", default="")
    ap.add_argument("--lora", action="append", default=[],
                    help="character LoRA path (repeatable)")
    ap.add_argument("--lora-scale", dest="lora_scale", action="append", type=float,
                    default=[], help="per-LoRA strength (default 0.9, strong for face)")
    ap.add_argument("--strength", type=float, default=0.45,
                    help="denoise strength; 0.4-0.5 keeps orientation, swaps features")
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--expand", type=float, default=0.30,
                    help="grow detected face box by this fraction each side")
    ap.add_argument("--feather", type=float, default=0.03,
                    help="mask feather as fraction of max(H,W); softens the seam")
    ap.add_argument("--model", default=YUNET)
    ap.add_argument("--save-mask", default=None, help="also write the mask for inspection")
    a = ap.parse_args()

    bgr = cv2.imread(a.inp)
    if bgr is None:
        log(f"ERROR: cannot read {a.inp}")
        return 2
    faces = detect_faces(a.model, bgr, 0.6)
    if len(faces) == 0:
        log("WARNING: no face detected; copying source unchanged")
        cv2.imwrite(a.out, bgr)
        return 3
    mask_img, n = build_face_mask(bgr, faces, a.expand, a.feather)
    if n == 0:
        log("WARNING: faces too small; copying source unchanged")
        cv2.imwrite(a.out, bgr)
        return 3
    if a.save_mask:
        mask_img.save(a.save_mask)
        log(f"saved mask -> {a.save_mask}")
    log(f"inpainting {n} face region(s)")

    # source as RGB PIL at its native size
    src = Image.open(a.inp).convert("RGB")
    W, H = src.size

    import torch  # noqa: PLC0415
    from diffusers import (  # noqa: PLC0415
        EulerDiscreteScheduler,
        StableDiffusionXLInpaintPipeline,
    )

    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
        PONY_REPO, torch_dtype=torch.bfloat16, use_safetensors=True
    )
    # Pony V6 ships an EDM scheduler that renders pure noise; force vanilla Euler
    # (eps / scaled_linear) — identical to gen_image.py's pony path.
    pipe.scheduler = EulerDiscreteScheduler(
        beta_start=0.00085,
        beta_end=0.012,
        beta_schedule="scaled_linear",
        prediction_type="epsilon",
        steps_offset=1,
        timestep_spacing="leading",
    )
    log("scheduler forced to EulerDiscreteScheduler (eps/scaled_linear)")

    # fuse character LoRA(s) strongly (default 0.9) so the limited repaint reliably
    # carries the LoRA's face features.
    if a.lora:
        scales = a.lora_scale or []
        if len(scales) == 1:
            scales = scales * len(a.lora)
        while len(scales) < len(a.lora):
            scales.append(0.9)
        names = []
        for i, lp in enumerate(a.lora):
            adapter = f"lora_{i}"
            pipe.load_lora_weights(lp, adapter_name=adapter)
            names.append(adapter)
            log(f"loaded LoRA {adapter}={lp} scale={scales[i]}")
        pipe.set_adapters(names, adapter_weights=scales[: len(names)])
        pipe.fuse_lora(adapter_names=names, lora_scale=1.0)
        pipe.unload_lora_weights()
        log(f"fused {len(names)} LoRA(s)")

    pipe.to("cuda")

    gen = None
    if a.seed is not None:
        gen = torch.Generator("cpu").manual_seed(a.seed)

    # compel long-prompt embeddings (Pony prompts exceed 77 tokens).
    from compel import Compel, ReturnedEmbeddingsType  # noqa: PLC0415

    compel = Compel(
        tokenizer=[pipe.tokenizer, pipe.tokenizer_2],
        text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
        returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
        requires_pooled=[False, True],
        truncate_long_prompts=False,
    )
    prompt_embeds, pooled = compel(a.prompt)
    kw = dict(prompt_embeds=prompt_embeds, pooled_prompt_embeds=pooled)
    if a.negative:
        neg_embeds, neg_pooled = compel(a.negative)
        prompt_embeds, neg_embeds = compel.pad_conditioning_tensors_to_same_length(
            [prompt_embeds, neg_embeds]
        )
        kw["prompt_embeds"] = prompt_embeds
        kw["negative_prompt_embeds"] = neg_embeds
        kw["negative_pooled_prompt_embeds"] = neg_pooled

    result = pipe(
        image=src,
        mask_image=mask_img,
        height=H,
        width=W,
        strength=a.strength,
        num_inference_steps=a.steps,
        guidance_scale=a.guidance,
        generator=gen,
        **kw,
    ).images[0]

    result.save(a.out)
    log(f"saved -> {a.out}")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
