#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
#   "transformers>=4.56",
#   "accelerate",
#   "pillow",
#   "sentencepiece",
#   "protobuf",
#   "safetensors",
# ]
#
# # cu121 torch: this rig's driver is CUDA 12.2; default wheels target newer CUDA
# # and fail ("driver too old" / accelerator not found). torchvision required for
# # CLIP/Siglip image processors. Same pin as gen_image.py.
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
gen_kontext.py — FLUX.1 Kontext [dev] in-context image editing for the
video-media-studio skill. Reference-conditioned: feed ONE input image + an
instruction prompt; Kontext preserves the identity of people/objects while
changing pose / background / style, no fine-tuning. Understands OpenPose-style
pose cues directly.

NOTE: FLUX.1 [dev]-family license is NON-COMMERCIAL (gated). bf16 ~24GB on one
A6000; --offload model if tight.
"""

import argparse
import sys
import torch
from PIL import Image, ImageOps
from diffusers import FluxKontextPipeline

REPO = "black-forest-labs/FLUX.1-Kontext-dev"
# FLUX ignores negative_prompt; we steer with positive phrasing instead.


def log(msg):
    print(f"[gen_kontext] {msg}", file=sys.stderr, flush=True)


def load_img(p):
    im = Image.open(p)
    return ImageOps.exif_transpose(im).convert("RGB")


def main():
    ap = argparse.ArgumentParser(description="FLUX.1 Kontext [dev] reference image editing")
    ap.add_argument("--image", required=True, help="single input/reference image")
    ap.add_argument("--prompt", required=True, help="instruction (what to change/produce)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default=None, help="WxH (default: keep input aspect)")
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--guidance", type=float, default=2.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--offload", choices=["none", "model", "sequential"], default="model")
    args = ap.parse_args()

    img = load_img(args.image)
    log(f"ref={args.image} size={img.size}")

    log(f"loading {REPO} (bf16); offload={args.offload}")
    pipe = FluxKontextPipeline.from_pretrained(REPO, torch_dtype=torch.bfloat16)
    if args.offload == "model":
        pipe.enable_model_cpu_offload()
    elif args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")

    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    kw = dict(
        image=img,
        prompt=args.prompt,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=gen,
    )
    if args.size:
        w, h = (int(x) for x in args.size.lower().split("x"))
        kw["width"], kw["height"] = w, h
    log(f"generating: steps={args.steps} guidance={args.guidance} seed={args.seed}")
    out = pipe(**kw).images[0]
    out.save(args.out)
    log(f"WROTE {args.out} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
