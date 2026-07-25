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
#   "controlnet-aux==0.0.10",
#   "matplotlib",
#   "scipy",
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
gen_wan_vace.py - Wan2.1-VACE-14B reference/control video wrapper.

VACE single-task R2V is reference image(s) + prompt, with no driving video.
Driving a reference subject with another video is a composition task
(R2V + Pose/Depth/Gray V2V). In diffusers that means `video` should be a
VACE-recognizable control video, not the raw RGB source person.
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
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanVACEPipeline
from diffusers.utils import export_to_video, load_video

MODEL_ID = "Wan-AI/Wan2.1-VACE-14B-diffusers"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# Wan's canonical negative (quality/anatomy) + this rig's fixed no-tattoo rule.
DEFAULT_NEG = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，"
    "低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，"
    "形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走，"
    "tattoo, tattoos, body ink, lettering on skin"
)


def log(msg: str) -> None:
    print(f"[gen_wan_vace] {msg}", file=sys.stderr, flush=True)


def prepare_detector(detector):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(min(8, os.cpu_count() or 1))
    detector.to(device)
    log(f"detector device: {device}; CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')}")
    return detector


def fit_frames(raw: list[Image.Image], width: int, height: int, frames: int) -> list[Image.Image]:
    if not raw:
        raise ValueError("motion/mask video has no frames")
    out = []
    for i in range(frames):
        frame = raw[min(i, len(raw) - 1)]
        out.append(ImageOps.exif_transpose(frame).convert("RGB").resize((width, height), Image.LANCZOS))
    return out


def read_video_frames(path: str) -> list[Image.Image]:
    src = Path(path)
    if src.is_dir():
        files = sorted(p for p in src.iterdir() if p.suffix.lower() in IMAGE_EXTS)
        if not files:
            raise ValueError(f"frame directory has no supported image files: {path}")
        return [Image.open(p) for p in files]
    return load_video(path)


def make_gray_video(frames: list[Image.Image]) -> list[Image.Image]:
    return [ImageOps.grayscale(frame).convert("RGB") for frame in frames]


def make_pose_video(frames: list[Image.Image], include_face: bool) -> list[Image.Image]:
    from controlnet_aux import OpenposeDetector  # noqa: PLC0415

    log("loading OpenposeDetector (lllyasviel/Annotators) for VACE pose control")
    detector = prepare_detector(OpenposeDetector.from_pretrained("lllyasviel/Annotators"))
    return [
        detector(frame, include_hand=True, include_face=include_face).convert("RGB").resize(frame.size, Image.LANCZOS)
        for frame in frames
    ]


def make_depth_video(frames: list[Image.Image]) -> list[Image.Image]:
    from controlnet_aux import MidasDetector  # noqa: PLC0415

    log("loading MidasDetector (lllyasviel/Annotators) for VACE depth control")
    detector = prepare_detector(MidasDetector.from_pretrained("lllyasviel/Annotators"))
    return [detector(frame).convert("RGB").resize(frame.size, Image.LANCZOS) for frame in frames]


def load_mask_video(path: str, width: int, height: int, frames: int) -> list[Image.Image]:
    raw = read_video_frames(path)
    fitted = fit_frames(raw, width, height, frames)
    return [ImageOps.grayscale(frame) for frame in fitted]


def bbox_masks_from_control(frames: list[Image.Image], expand_ratio: float) -> list[Image.Image]:
    masks = []
    for frame in frames:
        arr = np.asarray(frame.convert("RGB"))
        active = np.any(arr > 16, axis=2)
        mask = Image.new("L", frame.size, 0)
        if active.any():
            ys, xs = np.where(active)
            x1, x2 = int(xs.min()), int(xs.max()) + 1
            y1, y2 = int(ys.min()), int(ys.max()) + 1
            pad = int(max(x2 - x1, y2 - y1) * expand_ratio)
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(frame.width, x2 + pad), min(frame.height, y2 + pad)
            mask.paste(255, (x1, y1, x2, y2))
        else:
            mask.paste(255)
        masks.append(mask)
    return masks


def save_debug_frames(frames: list[Image.Image], masks: list[Image.Image] | None, out_dir: str) -> None:
    dst = Path(out_dir)
    dst.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames[:8]):
        frame.save(dst / f"control_{i:03d}.png")
    if masks is not None:
        for i, mask in enumerate(masks[:8]):
            mask.save(dst / f"mask_{i:03d}.png")
    log(f"saved conditioning preview frames -> {dst}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Wan2.1-VACE-14B reference + VACE control video")
    ap.add_argument("--ref", action="append", required=True,
                    help="reference image path (repeatable; e.g. full body + face crop)")
    ap.add_argument("--motion-video", default=None,
                    help="driving video (mp4/dir of frames). Converted to --control-mode before VACE.")
    ap.add_argument("--control-mode", choices=["pose", "depth", "gray", "raw"], default="pose",
                    help="pose/depth/gray build a VACE control video from --motion-video. "
                         "raw passes the RGB source through and usually leaks the source identity.")
    ap.add_argument("--openpose-include-face", action="store_true",
                    help="include face keypoints in pose control. Default off to avoid leaking source face geometry.")
    ap.add_argument("--mask-video", default=None,
                    help="optional white-generate/black-keep mask video or frame dir. Use for inpainting-style swaps.")
    ap.add_argument("--mask-mode", choices=["full", "control-bbox", "none"], default="full",
                    help="full=white everywhere, correct for pose/depth/gray control. "
                         "control-bbox generates only a bbox around non-black control pixels. "
                         "none omits the mask argument, which diffusers also treats as all-white.")
    ap.add_argument("--mask-expand", type=float, default=0.25,
                    help="bbox expansion ratio for --mask-mode control-bbox")
    ap.add_argument("--save-conditioning-dir", default=None,
                    help="save first control/mask frames for inspection")
    ap.add_argument("--dry-run-conditioning", action="store_true",
                    help="prepare control/mask frames, optionally save them, then exit before loading Wan")
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
    ap.add_argument("--conditioning-scale", type=float, default=1.0,
                    help="VACE control branch scale. Start with 1.0 for pose/depth/gray; "
                         "lower to 0.6-0.8 if motion control overwhelms identity.")
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

    # Driving video is useful only after converting it into a VACE control video.
    # Raw RGB person video carries the original person's appearance in the control
    # latent stream and tends to pass through that identity.
    video = None
    mask = None
    if args.motion_video:
        raw = read_video_frames(args.motion_video)  # list[PIL] (mp4 or dir of frames)
        drive = fit_frames(raw, width, height, frames)
        if args.control_mode == "pose":
            video = make_pose_video(drive, include_face=bool(args.openpose_include_face))
        elif args.control_mode == "depth":
            video = make_depth_video(drive)
        elif args.control_mode == "gray":
            video = make_gray_video(drive)
        else:
            video = drive
            log("WARNING: --control-mode raw passes the source RGB video into VACE; "
                "source identity/texture is expected to leak.")

        if args.mask_video:
            mask = load_mask_video(args.mask_video, width, height, frames)
            log(f"mask video: {args.mask_video} -> {len(mask)} frames")
        elif args.mask_mode == "full":
            white = Image.new("L", (width, height), 255)
            mask = [white] * frames
        elif args.mask_mode == "control-bbox":
            mask = bbox_masks_from_control(video, args.mask_expand)

        if args.save_conditioning_dir:
            save_debug_frames(video, mask, args.save_conditioning_dir)
        log(f"motion video: {args.motion_video} -> {len(video)} {args.control_mode} control frames, "
            f"mask={args.mask_video or args.mask_mode}")
    else:
        log("WARNING: no --motion-video: this is VACE single-task R2V (reference_images + prompt), "
            "not motion transfer from another video.")

    if args.dry_run_conditioning:
        if video is None:
            log("dry run complete: no motion/control video was provided")
        else:
            log(f"dry run complete: control_frames={len(video)} mask_frames={0 if mask is None else len(mask)}")
        return 0

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
        f"shift={args.flow_shift} seed={args.seed} refs={len(refs)} cscale={args.conditioning_scale}")
    call_kwargs = dict(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        reference_images=refs,
        height=height,
        width=width,
        num_frames=frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        conditioning_scale=args.conditioning_scale,
        generator=gen,
    )
    if video is not None:
        call_kwargs["video"] = video
        call_kwargs["mask"] = mask
    out = pipe(**call_kwargs).frames[0]

    export_to_video(out, args.out, fps=args.fps)
    log(f"saved -> {args.out}")
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
