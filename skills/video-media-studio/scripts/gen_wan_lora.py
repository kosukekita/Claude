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
# # cu121 torch for the CUDA 12.2 driver (see reference/setup.md). torchvision is
# # required for the image conditioning processors. peft is needed for LoRA.
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
gen_wan_lora.py — Wan2.2-I2V-A14B (image-to-video) with stacked community LoRAs,
for the video-media-studio skill. The NSFW-leaning counterpart of gen_ltx23_lora.py
but for Wan, whose human-motion realism + LoRA ecosystem beat LTX-2.3 for NSFW.

KEY FACT — Wan2.2-A14B is a MoE with TWO denoising experts:
  transformer    = HIGH-noise expert (early steps)   -> LoRA loaded with load_into_transformer_2=False
  transformer_2  = LOW-noise expert  (late steps)     -> LoRA loaded with load_into_transformer_2=True
Community Wan2.2 LoRAs therefore ship as HIGH/LOW pairs. You MUST load each side
into its matching expert or the effect is half-applied. This script pairs them
automatically: pass --lora <HIGH_file> --lora-low <LOW_file> (or a HF repo + a
basename that has _HIGH/_LOW or high_noise/low_noise variants).

bf16 ~80GB doesn't fit one A6000 -> default --offload model (or fp8 if added).
Frame rule: Wan is 4k+1 (81 = 5s @ fps 16). dims multiple of 16.
"""

import argparse
import re
import sys
import torch
from PIL import Image, ImageOps
from huggingface_hub import hf_hub_download
from diffusers import WanImageToVideoPipeline
from diffusers.utils import export_to_video

BASE = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"
DEFAULT_NEG = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，"
    "最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，"
    "画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，"
    "杂乱的背景，三条腿，背景人很多，倒着走, tattoo, body ink, lettering on skin, "
    "deformed hands, extra fingers, watermark, text"
)
LORA_SET_REPO = "lkzd7/WAN2.2_LoraSet_NSFW"


def log(msg):
    print(f"[gen_wan_lora] {msg}", file=sys.stderr, flush=True)


def load_img(p):
    return ImageOps.exif_transpose(Image.open(p)).convert("RGB")


def round16(x):
    return max(16, (int(x) // 16) * 16)


def resolve_pair(lora, lora_low, repo):
    """
    Return (high_path, low_path). Each of lora/lora_low may be a local path or a
    filename inside `repo` (downloaded). If only --lora is given and it contains a
    HIGH marker, derive the LOW filename automatically.
    """
    def fetch(name):
        import os
        if name and os.path.isfile(name):
            return name
        return hf_hub_download(repo, name)

    high = lora
    low = lora_low
    if high and not low:
        # derive the LOW counterpart from common HIGH/LOW naming schemes
        cand = None
        for hi, lo in [("_HIGH", "_LOW"), ("-HIGH", "-LOW"), ("_H.", "_L."),
                       ("high_noise", "low_noise"), ("HN", "LN"), ("_HIGH_", "_LOW_")]:
            if hi in high:
                cand = high.replace(hi, lo)
                break
        if cand and cand != high:
            low = cand
            log(f"derived LOW counterpart: {low}")
        else:
            log("WARN: could not derive LOW counterpart; loading HIGH only "
                "(effect will be partial on a MoE model)")
    return (fetch(high) if high else None,
            fetch(low) if low else None)


def main():
    ap = argparse.ArgumentParser(description="Wan2.2-I2V-A14B i2v with HIGH/LOW MoE LoRA pair")
    ap.add_argument("--image", required=True, help="input still (i2v conditioning)")
    ap.add_argument("--prompt", required=True, help="describe the motion/action")
    ap.add_argument("--negative-prompt", default=DEFAULT_NEG)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lora", help="HIGH-noise LoRA: local path or filename in --lora-repo")
    ap.add_argument("--lora-low", help="LOW-noise LoRA (if not auto-derivable from --lora)")
    ap.add_argument("--lora-repo", default=LORA_SET_REPO, help="HF repo to fetch LoRA filenames from")
    ap.add_argument("--lora-scale", type=float, default=1.0)
    ap.add_argument("--width", type=int, default=None)
    ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--max-side", type=int, default=832, help="cap the longer side (keeps VRAM in check)")
    ap.add_argument("--num-frames", type=int, default=81, help="Wan rule 4k+1 (81=5s)")
    ap.add_argument("--fps", type=int, default=16)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--guidance", type=float, default=3.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--offload", choices=["none", "model", "sequential"], default="model")
    args = ap.parse_args()

    if (args.num_frames - 1) % 4 != 0:
        log(f"WARN: num_frames={args.num_frames} not 4k+1; Wan may error. Use 81/121/161...")

    img = load_img(args.image)
    w0, h0 = img.size
    if args.width and args.height:
        W, H = round16(args.width), round16(args.height)
    else:
        scale = args.max_side / max(w0, h0)
        W, H = round16(w0 * scale), round16(h0 * scale)
    log(f"input {w0}x{h0} -> gen {W}x{H}, {args.num_frames}f @ {args.fps}fps")

    log(f"loading {BASE} (bf16); offload={args.offload}")
    pipe = WanImageToVideoPipeline.from_pretrained(BASE, torch_dtype=torch.bfloat16)

    # ---- LoRA: load HIGH into transformer, LOW into transformer_2 ----
    if args.lora:
        high_path, low_path = resolve_pair(args.lora, args.lora_low, args.lora_repo)
        if high_path:
            log(f"LoRA HIGH -> transformer (high-noise expert): {high_path.split('/')[-1]}")
            pipe.load_lora_weights(high_path, adapter_name="hi", load_into_transformer_2=False)
        if low_path:
            log(f"LoRA LOW  -> transformer_2 (low-noise expert): {low_path.split('/')[-1]}")
            pipe.load_lora_weights(low_path, adapter_name="lo", load_into_transformer_2=True)
        # set strengths
        try:
            pipe.set_adapters(["hi", "lo"][: (1 if not low_path else 2)],
                              adapter_weights=[args.lora_scale] * (1 if not low_path else 2))
        except Exception as e:
            log(f"set_adapters note: {e}")
        log(f"LoRA scale={args.lora_scale}")

    if args.offload == "model":
        pipe.enable_model_cpu_offload()
    elif args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")

    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    log(f"generating: {W}x{H} {args.num_frames}f steps={args.steps} guidance={args.guidance} seed={args.seed}")
    result = pipe(
        image=img,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        height=H, width=W,
        num_frames=args.num_frames,
        guidance_scale=args.guidance,
        num_inference_steps=args.steps,
        generator=gen,
    ).frames[0]

    export_to_video(result, args.out, fps=args.fps)
    log(f"WROTE {args.out} ({W}x{H} {args.num_frames}f {args.fps}fps)")


if __name__ == "__main__":
    main()
