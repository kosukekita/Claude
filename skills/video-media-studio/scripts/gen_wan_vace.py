#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers.git",
#   "transformers>=4.56",
#   "accelerate",
#   "peft>=0.13",
#   "safetensors",
#   "huggingface-hub",
#   "hf_transfer",
#   "sentencepiece",
#   "protobuf",
#   "imageio",
#   "imageio-ffmpeg",
#   "av",
#   "pillow",
#   "numpy",
#   "ftfy",
# ]
#
# # cu121 torch for the CUDA 12.2 driver (see reference/setup.md).
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
gen_wan_vace.py — Wan2.1-VACE-14B reference-to-video (r2v) for video-media-studio.

r2v = extract the person/subject's APPEARANCE from reference image(s) and
generate a NEW video of that subject. This is NOT i2v (first-frame animation):
the output does not start from the reference frame; identity comes from
`reference_images`, motion/scene/camera come from the prompt.
Fully local (diffusers WanVACEPipeline) => NSFW-capable, no API censorship.

Reference-image tips (VACE): plain/white background isolates the subject best;
1-3 refs (e.g. full body + face crop) beat a multi-panel sheet grid.

VRAM: 14B bf16 transformer (~28GB) + umT5-xxl (~11GB) -> --offload model
(default) fits one 48GB A6000. VAE stays fp32 (bf16 visibly degrades decode).
Frame rule: Wan is 4k+1 (81 = 5s @ fps 16). dims must be multiples of 16.
flow_shift: 3.0 suits 480p, 5.0 suits 720p (Wan/UniPC convention).
"""

import os
import sys

# --gpu N must take effect BEFORE torch initializes CUDA (other gen scripts on
# this rig hardcode cuda:0; pinning via CUDA_VISIBLE_DEVICES avoids collisions
# with jobs from other sessions).
if "--gpu" in sys.argv:
    os.environ["CUDA_VISIBLE_DEVICES"] = sys.argv[sys.argv.index("--gpu") + 1]

import argparse

import torch
from PIL import Image, ImageOps
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanVACEPipeline
from diffusers.utils import export_to_video

MODEL_ID = "Wan-AI/Wan2.1-VACE-14B-diffusers"

# Wan's canonical negative (quality/anatomy) + this rig's fixed no-tattoo rule.
DEFAULT_NEG = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，"
    "低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，"
    "形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走，"
    "tattoo, tattoos, body ink, lettering on skin"
)


def log(msg: str) -> None:
    print(f"[gen_wan_vace] {msg}", file=sys.stderr, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Wan2.1-VACE-14B reference-to-video (r2v)")
    ap.add_argument("--ref", action="append", required=True,
                    help="reference image path (repeatable; e.g. full body + face crop)")
    ap.add_argument("--prompt", required=True, help="scene/motion for the NEW video")
    ap.add_argument("--negative-prompt", default=DEFAULT_NEG)
    ap.add_argument("--out", required=True, help="output mp4 path")
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--height", type=int, default=832,
                    help="default portrait 480x832 (dims rounded to /16)")
    ap.add_argument("--num-frames", type=int, default=81, help="Wan rule 4k+1 (81=5s)")
    ap.add_argument("--fps", type=int, default=16)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--flow-shift", type=float, default=3.0, help="3.0 for 480p, 5.0 for 720p")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--offload", choices=["model", "sequential", "none"], default="model")
    ap.add_argument("--gpu", help="physical GPU index (applied via CUDA_VISIBLE_DEVICES before torch)")
    args = ap.parse_args()

    width = max(16, (args.width // 16) * 16)
    height = max(16, (args.height // 16) * 16)
    frames = args.num_frames
    if (frames - 1) % 4 != 0:
        frames = ((frames - 1) // 4) * 4 + 1
        log(f"num_frames adjusted to Wan 4k+1 rule: {args.num_frames} -> {frames}")

    refs = []
    for p in args.ref:
        img = ImageOps.exif_transpose(Image.open(p).convert("RGB"))
        refs.append(img)
        log(f"reference: {p} ({img.width}x{img.height})")

    log(f"loading {MODEL_ID} (bf16 transformer, fp32 VAE)…")
    vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanVACEPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=args.flow_shift)

    if args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    elif args.offload == "model":
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")
    log(f"offload={args.offload} device_visible={os.environ.get('CUDA_VISIBLE_DEVICES', 'all')}")

    gen = torch.Generator(device="cuda").manual_seed(args.seed)
    log(f"generating {width}x{height} x{frames}f steps={args.steps} cfg={args.guidance} "
        f"shift={args.flow_shift} seed={args.seed} refs={len(refs)}")
    out = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        reference_images=refs,
        height=height,
        width=width,
        num_frames=frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=gen,
    ).frames[0]

    export_to_video(out, args.out, fps=args.fps)
    log(f"saved -> {args.out}")
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
