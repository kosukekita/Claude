#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers.git",
#   "transformers>=4.56",
#   "accelerate",
#   "safetensors",
#   "sentencepiece",
#   "protobuf",
#   "imageio",
#   "imageio-ffmpeg",
#   "pillow",
#   "numpy",
#   "ftfy",
# ]
#
# # cu121 torch for the CUDA 12.2 driver (see reference/setup.md). torchvision is
# # required for the image conditioning / CLIP-style processors.
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
gen_ltx23.py — LTX-2.3 (22B) image-to-video via diffusers LTX2ImageToVideoPipeline.

This is the HIGHEST-QUALITY local i2v path in this skill (Codex/HF rank LTX-2.3
above Wan2.2-I2V-A14B for visual quality). Unlike Wan-A14B (which needs
fp8+offload and runs ~146s/step), LTX-2.3 fits ~24GB with
enable_sequential_cpu_offload — comfortable on a single 48GB A6000.

Key facts (HF diffusers docs):
  * repo: diffusers/LTX-2.3-Diffusers ; class: LTX2ImageToVideoPipeline
  * returns (video, audio) — audio is generated too (24kHz)
  * LTX-2.3 specific call args: stg_scale=1.0, modality_scale=3.0,
    guidance_rescale=0.7 (prevents OVEREXPOSURE — the failure we saw on
    LTX-Video-0.9.8), spatio_temporal_guidance_blocks=[28], use_cross_timestep=True
  * bf16 recommended (no fp8 needed). VAE tiling for memory.
  * Gemma-3 is OPTIONAL (prompt enhancement only) — we DO NOT require it, so no
    gated dependency for plain i2v.
  * frame rule 8k+1 (121, 193), dims multiple of 32.

Run:
  source scripts/env.sh
  "$UV" run scripts/gen_ltx23.py --image in.jpg --prompt "..." \
    --width 768 --height 512 --num-frames 121 --fps 24 --out out.mp4
  # optional 2x spatial upscale (slower, sharper):
  "$UV" run scripts/gen_ltx23.py ... --upscale
"""
from __future__ import annotations

import argparse
import os
import sys


def log(msg: str) -> None:
    print(f"[gen_ltx23] {msg}", file=sys.stderr, flush=True)


REPO = "diffusers/LTX-2.3-Diffusers"


def snap(v: int, mult: int, name: str) -> int:
    if v % mult != 0:
        fixed = max(mult, (v // mult) * mult)
        log(f"{name} {v} not divisible by {mult} -> {fixed}")
        return fixed
    return v


def snap_frames(n: int) -> int:
    # 8k + 1 rule
    if (n - 1) % 8 != 0 or n < 1:
        fixed = max(1, ((n - 1) // 8) * 8 + 1)
        log(f"num_frames {n} violates 8k+1 -> {fixed}")
        return fixed
    return n


def main() -> int:
    p = argparse.ArgumentParser(
        prog="gen_ltx23.py",
        description="LTX-2.3 (22B) image-to-video via diffusers "
                    "(highest-quality local i2v; ~24GB with sequential offload).",
    )
    p.add_argument("--image", required=True, help="input still image (i2v)")
    p.add_argument("--prompt", default="", help="text prompt (describe the motion)")
    p.add_argument("--negative-prompt",
                   default="worst quality, inconsistent motion, blurry, jittery, distorted")
    p.add_argument("--out", default="ltx23.mp4", help="output mp4 path")
    p.add_argument("--width", type=int, default=768, help="width (mult of 32)")
    p.add_argument("--height", type=int, default=512, help="height (mult of 32)")
    p.add_argument("--num-frames", type=int, default=121, help="8k+1 (121, 193)")
    p.add_argument("--fps", type=float, default=24.0)
    p.add_argument("--steps", type=int, default=30)
    p.add_argument("--guidance", type=float, default=3.0)
    p.add_argument("--guidance-rescale", type=float, default=0.7,
                   help="prevents overexposure (LTX-2.3 default 0.7)")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--offload", choices=["sequential", "model", "none"],
                   default="sequential",
                   help="VRAM strategy (sequential ~24GB; safest on 48GB)")
    p.add_argument("--upscale", action="store_true",
                   help="run the 2x spatial/temporal latent upsampler (sharper, slower)")
    p.add_argument("--no-audio", action="store_true",
                   help="drop the generated audio track from the mp4")
    args = p.parse_args()

    args.width = snap(args.width, 32, "width")
    args.height = snap(args.height, 32, "height")
    args.num_frames = snap_frames(args.num_frames)

    import torch
    from diffusers.utils import load_image

    try:
        from diffusers import LTX2ImageToVideoPipeline
    except Exception as exc:  # noqa: BLE001
        log(f"LTX2ImageToVideoPipeline unavailable ({exc}); diffusers git-main "
            f"is required for LTX-2.3. Falling back: use gen_video.py --backend "
            f"wan --model wan2.2-i2v-a14b, or cloud_fal.py --model ltx-2.3.")
        return 3

    log(f"loading {REPO} (bf16); offload={args.offload}")
    pipe = LTX2ImageToVideoPipeline.from_pretrained(REPO, torch_dtype=torch.bfloat16)

    if args.offload == "sequential":
        pipe.enable_sequential_cpu_offload(device="cuda:0")
    elif args.offload == "model":
        pipe.enable_model_cpu_offload(device="cuda:0")
    else:
        pipe.to("cuda")
    try:
        pipe.vae.enable_tiling()
    except Exception:
        pass

    image = load_image(args.image)
    gen = torch.Generator("cpu").manual_seed(args.seed) if args.seed is not None else None

    call = dict(
        image=image,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        width=args.width,
        height=args.height,
        num_frames=args.num_frames,
        frame_rate=args.fps,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        guidance_rescale=args.guidance_rescale,
        # LTX-2.3 specific guidance (improves coherence; prevents overexposure)
        stg_scale=1.0,
        modality_scale=3.0,
        spatio_temporal_guidance_blocks=[28],
        use_cross_timestep=True,
        output_type="np",
        return_dict=False,
    )
    if gen is not None:
        call["generator"] = gen

    log(f"generating: {args.width}x{args.height} {args.num_frames}f "
        f"{args.steps}steps cfg={args.guidance} rescale={args.guidance_rescale}")
    out = pipe(**call)
    # returns (video, audio) when return_dict=False
    video, audio = (out[0], out[1]) if isinstance(out, (tuple, list)) and len(out) >= 2 else (out[0], None)

    if args.upscale:
        try:
            from diffusers import LTX2LatentUpsamplePipeline
            from diffusers.pipelines.ltx2.latent_upsampler import LTX2LatentUpsamplerModel
            log("loading latent upsampler for 2x spatial upscale")
            ups = LTX2LatentUpsamplerModel.from_pretrained(
                REPO, subfolder="latent_upsampler", torch_dtype=torch.bfloat16)
            up_pipe = LTX2LatentUpsamplePipeline(vae=pipe.vae, latent_upsampler=ups)
            up_pipe.enable_model_cpu_offload(device="cuda:0")
            up_pipe.vae.enable_tiling()
            up = up_pipe(video=video, width=args.width * 2, height=args.height * 2,
                         output_type="np", return_dict=False)
            video = up[0]
            if len(up) >= 2 and up[1] is not None:
                audio = up[1]
            log("upscale done")
        except Exception as exc:  # noqa: BLE001
            log(f"upscale skipped ({exc})")

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    from diffusers.utils import export_to_video
    try:
        if audio is not None and not args.no_audio:
            from diffusers.utils import encode_video
            sr = getattr(getattr(pipe, "vocoder", None), "config", None)
            sr = getattr(sr, "output_sampling_rate", 24000) if sr else 24000
            encode_video(video[0], fps=args.fps,
                         audio=audio[0].float().cpu() if hasattr(audio[0], "float") else audio[0],
                         audio_sample_rate=sr, output_path=args.out)
            log(f"WROTE {args.out} (with audio @ {sr}Hz)")
        else:
            export_to_video(video[0], args.out, fps=args.fps)
            log(f"WROTE {args.out} (video only)")
    except Exception as exc:  # noqa: BLE001
        log(f"encode_video failed ({exc}); falling back to export_to_video (no audio)")
        export_to_video(video[0], args.out, fps=args.fps)
        log(f"WROTE {args.out} (video only, fallback)")

    print(os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
