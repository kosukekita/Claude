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
# # required for the image conditioning processors. peft is needed for LoRA stacking.
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
gen_ltx23_lora.py — LTX-2.3 (22B) image-to-video WITH one or more LoRAs stacked
on top of the official diffusers base (diffusers/LTX-2.3-Diffusers).

This is gen_ltx23.py + LoRA loading. The official base stays the foundation
(see below for why); each --lora is loaded onto it via the diffusers
LTX2LoraLoaderMixin and blended by --lora-scale.

WHY the official base (not a "custom base model"):
  Community LTX-2 "models" like lynaNSFW/LTX2BFN are themselves LoRAs (a single
  ~100-200MB safetensors with diffusion_model.*.lora_A/B keys), not full
  checkpoints. The only real full base in the chain is Lightricks/LTX-2, which
  diffusers ships as diffusers/LTX-2.3-Diffusers. So the faithful way to honor a
  "base_model: X" tag where X is itself a LoRA is to STACK X as one more LoRA on
  the official base. This script does exactly that — pass multiple --lora.

LoRA key compatibility (verified):
  The lynaNSFW motion LoRA uses PEFT-standard keys
  `diffusion_model.transformer_blocks.N.{attn,ff,...}.lora_A/B.weight` (rank 64,
  bf16, 2496 tensors incl. audio_attn / audio_to_video_attn). diffusers'
  _convert_non_diffusers_ltx2_lora_to_diffusers (non_diffusers_prefix=
  'diffusion_model') remaps all 2496 -> `transformer.*`, so load_lora_weights()
  ingests it directly. No ComfyUI/wan2gp runtime needed.

Convenience:
  --nsfw-motion is a shortcut for the lynaNSFW/LTX2.3_NSFW_motion motion LoRA
  (author recommends strength ~0.7 with the distilled/undistilled model and NO
  distilled-LoRA in the stack).

Run:
  source scripts/env.sh
  "$UV" run scripts/gen_ltx23_lora.py --image in.jpg --prompt "..." \
    --nsfw-motion --lora-scale 0.7 \
    --width 768 --height 512 --num-frames 121 --fps 24 --out out.mp4
  # arbitrary LoRA(s), HF id or local path, each with its own scale:
  "$UV" run scripts/gen_ltx23_lora.py --image in.jpg --prompt "..." \
    --lora lynaNSFW/LTX2.3_NSFW_motion --lora-scale 0.7 \
    --lora /path/to/other.safetensors --lora-scale 0.5 --out out.mp4
"""
from __future__ import annotations

import argparse
import os
import sys


def log(msg: str) -> None:
    print(f"[gen_ltx23_lora] {msg}", file=sys.stderr, flush=True)


REPO = "diffusers/LTX-2.3-Diffusers"

# Known community LoRAs. The motion LoRA's repo declares a chain of "base_model"
# tags that are ALL themselves LoRAs (LTX2BFN -> SPROUT -> Lightricks/LTX-2);
# only the last is a full base. We stack the motion LoRA on the official base.
NSFW_MOTION_REPO = "lynaNSFW/LTX2.3_NSFW_motion"
NSFW_MOTION_FILE = "LTX2.3-NSFWMOTION_00750.safetensors"


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


def resolve_lora(spec: str) -> tuple[str, str | None]:
    """Return (path_or_repo, weight_name). Local file -> (path, None).
    HF repo id -> (repo, None) unless a known single-file repo we name explicitly."""
    if os.path.exists(spec):
        return spec, None
    # Known single-file repos: name the file so diffusers grabs the right one.
    if spec == NSFW_MOTION_REPO:
        return spec, NSFW_MOTION_FILE
    return spec, None


def main() -> int:
    p = argparse.ArgumentParser(
        prog="gen_ltx23_lora.py",
        description="LTX-2.3 (22B) i2v with stacked LoRA(s) on the official "
                    "diffusers base (highest-quality local i2v; ~24GB offload).",
    )
    p.add_argument("--image", required=True, help="input still image (i2v)")
    p.add_argument("--prompt", default="", help="text prompt (describe the motion)")
    p.add_argument("--negative-prompt",
                   default="worst quality, inconsistent motion, blurry, jittery, distorted")
    p.add_argument("--out", default="ltx23_lora.mp4", help="output mp4 path")
    # LoRA stacking: --lora repeatable; --lora-scale repeatable (pairs by order;
    # a single --lora-scale applies to all loras).
    p.add_argument("--lora", action="append", default=[],
                   help="LoRA HF repo id or local .safetensors path. Repeatable.")
    p.add_argument("--lora-scale", action="append", default=[], type=float,
                   help="strength per --lora (pairs by order; one value = all). "
                        "Default 0.7 (author's recommended motion strength).")
    p.add_argument("--nsfw-motion", action="store_true",
                   help=f"shortcut: prepend {NSFW_MOTION_REPO} to the LoRA stack")
    p.add_argument("--fuse", action="store_true",
                   help="fuse LoRA into weights (slightly faster, can't unload). "
                        "Default: keep as adapters (safer with offload).")
    p.add_argument("--width", type=int, default=None,
                   help="width (mult of 32); default: auto from input image aspect")
    p.add_argument("--height", type=int, default=None,
                   help="height (mult of 32); default: auto from input image aspect")
    p.add_argument("--max-side", type=int, default=1152,
                   help="longest side when auto-sizing from the image (default 1152)")
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
                   help="run the 2x spatial latent upsampler (sharper, slower)")
    p.add_argument("--no-audio", action="store_true",
                   help="drop the generated audio track from the mp4")
    args = p.parse_args()

    # Assemble the LoRA stack (order matters only for naming).
    loras: list[str] = []
    if args.nsfw_motion:
        loras.append(NSFW_MOTION_REPO)
    loras.extend(args.lora)
    if not loras:
        log("no --lora given and --nsfw-motion not set; this is plain LTX-2.3 i2v "
            "(use gen_ltx23.py instead). Continuing without LoRA.")

    # Pair scales: one value -> all; else pair by order; default 0.7.
    scales = list(args.lora_scale)
    if not scales:
        scales = [0.7] * len(loras)
    elif len(scales) == 1:
        scales = scales * len(loras)
    elif len(scales) != len(loras):
        log(f"--lora-scale count ({len(scales)}) != --lora count ({len(loras)}); "
            f"padding/truncating to match with last value.")
        while len(scales) < len(loras):
            scales.append(scales[-1])
        scales = scales[:len(loras)]

    # Auto-size to the INPUT IMAGE aspect ratio when width/height are not given.
    if args.width is None or args.height is None:
        from PIL import Image as _Image
        with _Image.open(args.image) as _im:
            iw, ih = _im.size
        ms = args.max_side
        if iw >= ih:
            args.width = ms
            args.height = max(32, round(ms * ih / iw))
        else:
            args.height = ms
            args.width = max(32, round(ms * iw / ih))
        log(f"auto-size from image {iw}x{ih} (aspect {iw/ih:.3f}) "
            f"-> {args.width}x{args.height} (max-side {ms})")

    args.width = snap(args.width, 32, "width")
    args.height = snap(args.height, 32, "height")
    args.num_frames = snap_frames(args.num_frames)
    log(f"final size {args.width}x{args.height} (aspect {args.width/args.height:.3f})")

    import torch
    from diffusers.utils import load_image

    try:
        from diffusers import LTX2ImageToVideoPipeline
    except Exception as exc:  # noqa: BLE001
        log(f"LTX2ImageToVideoPipeline unavailable ({exc}); diffusers git-main "
            f"is required for LTX-2.3.")
        return 3

    log(f"loading {REPO} (bf16); offload={args.offload}")
    pipe = LTX2ImageToVideoPipeline.from_pretrained(REPO, torch_dtype=torch.bfloat16)

    # --- LoRA stacking (BEFORE offload hooks, on the assembled pipeline) ---
    adapter_names: list[str] = []
    for i, (spec, scale) in enumerate(zip(loras, scales)):
        path_or_repo, weight_name = resolve_lora(spec)
        name = f"lora{i}"
        kwargs = {"adapter_name": name}
        if weight_name:
            kwargs["weight_name"] = weight_name
        log(f"loading LoRA[{i}] {spec} (scale {scale}) as adapter '{name}'"
            + (f" file={weight_name}" if weight_name else ""))
        try:
            pipe.load_lora_weights(path_or_repo, **kwargs)
            adapter_names.append(name)
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            log(f"LoRA load FAILED for {spec}: {exc}")
            return 4

    if adapter_names:
        used_scales = scales[:len(adapter_names)]
        pipe.set_adapters(adapter_names, adapter_weights=used_scales)
        log(f"adapters active: {adapter_names} scales={used_scales}")
        if args.fuse:
            pipe.fuse_lora(adapter_names=adapter_names)
            pipe.unload_lora_weights()
            log("fused LoRA into transformer weights")

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
        f"{args.steps}steps cfg={args.guidance} rescale={args.guidance_rescale} "
        f"loras={len(adapter_names)}")
    out = pipe(**call)
    video, audio = (out[0], out[1]) if isinstance(out, (tuple, list)) and len(out) >= 2 else (out[0], None)

    if args.upscale:
        try:
            from diffusers import LTX2LatentUpsamplePipeline  # noqa: F401
            from diffusers.pipelines.ltx2.latent_upsampler import LTX2LatentUpsamplerModel
            log("loading latent upsampler for 2x spatial upscale")
            ups = LTX2LatentUpsamplerModel.from_pretrained(
                REPO, subfolder="latent_upsampler", torch_dtype=torch.bfloat16)
            from diffusers import LTX2LatentUpsamplePipeline as _UP
            up_pipe = _UP(vae=pipe.vae, latent_upsampler=ups)
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
