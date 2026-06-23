#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch",
#   "git+https://github.com/huggingface/diffusers",
#   "transformers>=4.51.3",
#   "accelerate",
#   "pillow",
#   "sentencepiece",
#   "safetensors",
# ]
# ///
"""
gen_qwen_edit.py — Qwen-Image-Edit-2509 (the "Plus" multi-reference editor) for the
video-media-studio skill. Reference-conditioned image generation: feed 1-3 input
images (person + person / person + scene) and a prompt; the model keeps the
identity / body-type of the references while producing a new pose / scene.

This is the LOCAL answer to "Z-Image quality but with a reference image" — Qwen
shares the Qwen-Image (20B) backbone, Apache-2.0, strong character consistency.

Backend: local-single on one A6000 (bf16 ~40GB; --offload model if tight).
"""

import argparse
import sys
import torch
from PIL import Image, ImageOps
from diffusers import QwenImageEditPlusPipeline

REPO = "Qwen/Qwen-Image-Edit-2509"
DEFAULT_NEG = (
    "tattoo, tattoos, body ink, lettering on skin, deformed hands, extra fingers, "
    "distorted faces, fused bodies, extra limbs, warping, watermark, text, logo, "
    "low quality, blurry, plastic skin, oversaturated, cartoon, illustration, cgi"
)


def log(msg):
    print(f"[gen_qwen_edit] {msg}", file=sys.stderr, flush=True)


def load_img(p):
    im = Image.open(p)
    im = ImageOps.exif_transpose(im).convert("RGB")
    return im


def main():
    ap = argparse.ArgumentParser(description="Qwen-Image-Edit-2509 reference-conditioned image gen")
    ap.add_argument("--image", action="append", required=True,
                    help="reference image (repeat 1-3 times; e.g. man + woman + scene)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative-prompt", default=DEFAULT_NEG)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default=None, help="WxH for output (default: keep ref aspect)")
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--guidance", type=float, default=4.0, help="true_cfg_scale")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--offload", choices=["none", "model", "sequential"], default="model")
    args = ap.parse_args()

    if len(args.image) > 3:
        log(f"WARN: {len(args.image)} images given; Qwen-Edit-2509 is tuned for 1-3. Using first 3.")
        args.image = args.image[:3]
    imgs = [load_img(p) for p in args.image]
    log(f"refs={len(imgs)} sizes={[im.size for im in imgs]}")

    log(f"loading {REPO} (bf16); offload={args.offload}")
    pipe = QwenImageEditPlusPipeline.from_pretrained(REPO, torch_dtype=torch.bfloat16)
    if args.offload == "model":
        pipe.enable_model_cpu_offload()
    elif args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")

    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    kw = dict(
        image=imgs,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        num_inference_steps=args.steps,
        true_cfg_scale=args.guidance,
        generator=gen,
    )
    if args.size:
        w, h = (int(x) for x in args.size.lower().split("x"))
        kw["width"], kw["height"] = w, h
    log(f"generating: steps={args.steps} cfg={args.guidance} seed={args.seed}")
    out = pipe(**kw).images[0]
    out.save(args.out)
    log(f"WROTE {args.out} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
