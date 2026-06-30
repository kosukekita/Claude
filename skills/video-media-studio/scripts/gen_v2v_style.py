#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "numpy",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
#   "transformers>=4.56",
#   "accelerate",
#   "safetensors",
#   "sentencepiece",
#   "protobuf",
#   "scipy",
#   "compel==2.0.3",
#   "controlnet-aux==0.0.10",
#   "opencv-python-headless",
#   "pillow",
#   "einops",
#   "timm",
#   "matplotlib",
#   "scikit-image",
# ]
#
# # cu121 torch: this rig's driver is CUDA 12.2; default wheels target newer CUDA
# # and fail ("driver too old" / accelerator not found). torchvision is required by
# # CLIP/Siglip image processors and by controlnet-aux. Same pin as gen_image.py.
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
gen_v2v_style.py — NSFW video-to-video STYLE TRANSFER (real <-> anime) with a
LOCKED character, for the video-media-studio skill.

This is the diffusers (ComfyUI-free) port of the "Approach A" workflow:
per-frame img2img + strong reference control. The roles map like this:

  ComfyUI node                     -> here (diffusers, additions minimised)
  ------------------------------------------------------------------------
  base anime model (Pony/Illust.)  -> --style-model pony|noobai-xl|sdxl|...
  ControlNet OpenPose + Depth      -> xinsir/controlnet-{openpose,depth}-sdxl-1.0
  IP-Adapter FaceID / Reference    -> ip-adapter-plus-face_sdxl_vit-h.bin (CLIP
                                      ViT-H; NO insightface => no build hell)
  InstantID / Reactor              -> intentionally dropped (insightface-heavy);
                                      Plus-Face + ControlNet covers character lock
  VHS load/combine                 -> ffmpeg extract + export_to_video reassemble
  RIFE / seamless segments         -> --blend-prev (carry prev output into next
                                      init) + fixed seed/model/style/negative

WHY these choices (verified): FaceID/InstantID need insightface (antelopev2) to
extract a face embedding out-of-band and are painful to build; ip-adapter-plus-
face_sdxl_vit-h.bin runs on a plain CLIP ViT-H image encoder via the standard
pipe.load_ip_adapter(), so the whole stack is diffusers-native. SDXL ControlNet /
IP-Adapter are architecture-shared, so Pony/NoobAI/SDXL/AbsoluteReality-style
checkpoints all accept them; we just reuse gen_image.py's scheduler fixes
(NoobAI v-pred => v_prediction+zero-SNR; Pony => forced EulerDiscrete) and its
compel long-prompt path (Pony score-tag prompts blow past 77 tokens).

TEMPORAL FLICKER is intrinsic to per-frame img2img. The anti-drift levers
(borrowed from chain_video.py) are: ONE fixed seed for every frame, the SAME
style prompt + model + negative for every frame, ControlNet (pose+depth) pinning
the motion, --blend-prev mixing the previous transformed frame into the next
init image, and optional face-only refinement for tiny faces.

Backend: local-single on ONE A6000. Defaults to the freest GPU (or --gpu N).
Pin to GPU 1 with --gpu 1 when GPU 0 is busy (training etc.).

Output contract: WHY logs to stderr ([gen_v2v_style] ...); the final mp4's
absolute path is printed to stdout (chainable). Resume-safe: existing per-frame
PNGs and an existing non-empty --out are skipped.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths / constants (mirror gen_video.py conventions)
# --------------------------------------------------------------------------- #
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_SH = SCRIPT_DIR / "env.sh"
PROBE_PY = SCRIPT_DIR / "probe_backend.py"
UV = os.environ.get("UV") or "/home/kita/.local/bin/uv"
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

# Style bases that are plain SDXL checkpoints (SDXL ControlNet/IP-Adapter load
# straight onto them). repo + scheduler quirks mirror gen_image.py's MODELS.
# real-leaning -> sdxl (base) ; anime/illustration -> pony / noobai-xl(-vpred).
STYLE_MODELS: dict[str, dict] = {
    "sdxl": {
        "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "default_steps": 30, "default_guidance": 6.0,
        "vpred": False, "force_euler": False,
        "note": "neutral SDXL base (real-ish). Swap for AbsoluteReality/CyberRealistic via --style-repo.",
    },
    "pony": {
        "repo": "votepurchase/ponyDiffusionV6XL",
        "default_steps": 28, "default_guidance": 7.0,
        "vpred": False, "force_euler": True,   # EDM default -> pure noise; force Euler
        "note": "Pony V6XL anime. Needs score_9, score_8_up, ... + source_anime in the prompt.",
    },
    "noobai-xl": {
        "repo": "Laxhar/noobai-XL-1.1",
        "default_steps": 28, "default_guidance": 5.0,
        "vpred": False, "force_euler": False,
        "note": "NoobAI-XL eps (anime, booru tags).",
    },
    "noobai-xl-vpred": {
        "repo": "Laxhar/noobai-XL-Vpred-1.0",
        "default_steps": 28, "default_guidance": 5.0,
        "vpred": True, "force_euler": False,   # v_prediction + zero-SNR or it's noise
        "note": "NoobAI-XL v-pred (sharper anime; needs v_prediction scheduler).",
    },
    "manga-vision-il": {
        "repo": "John6666/manga-vision-il-v1-sdxl",
        "default_steps": 28, "default_guidance": 6.0,
        "vpred": False, "force_euler": False,
        "note": "Illustrious finetune for B/W manga pages.",
    },
}

# SDXL ControlNets (xinsir = current best; diffusers ControlNetModel loads them).
CONTROLNETS: dict[str, str] = {
    "openpose": "xinsir/controlnet-openpose-sdxl-1.0",
    "depth": "xinsir/controlnet-depth-sdxl-1.0",
    "canny": "xinsir/controlnet-canny-sdxl-1.0",
}
SDXL_VAE_FP16_FIX = "madebyollin/sdxl-vae-fp16-fix"   # avoids fp16 black frames
IPADAPTER_REPO = "h94/IP-Adapter"
IPADAPTER_FACE_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.bin"   # CLIP ViT-H, no insightface
IPADAPTER_IMAGE_ENCODER_SUBFOLDER = "models/image_encoder"     # ViT-H (NOT sdxl_models/image_encoder)

# Fixed anti-drift negative (copied verbatim from chain_video.py — the proven
# anti-style/colour-drift string). Pinning this across every frame is the main
# flicker lever, same as pinning it across chained clips.
DEFAULT_NEGATIVE = (
    "color shift, color drift, style change, inconsistent style, inconsistent "
    "lighting, palette change, blurry, low quality, low resolution, jpeg "
    "artifacts, compression artifacts, flicker, flickering, ghosting, morphing, "
    "warping, distorted face, deformed, disfigured, extra limbs, extra fingers, "
    "duplicate, watermark, text, subtitles, oversaturated, washed out, "
    "tattoo, tattoos, body ink, lettering on skin"
)


def log(msg: str) -> None:
    print(f"[gen_v2v_style] {msg}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Clean LD / re-exec through env.sh (mirror gen_video.py so torch loads clean)
# --------------------------------------------------------------------------- #
def clean_ld_environment() -> None:
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p for p in ld.split(os.pathsep)
            if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p
        ]
        new = os.pathsep.join(kept)
        if new:
            os.environ["LD_LIBRARY_PATH"] = new
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")


def sh(s) -> str:
    if s is None:
        return "''"
    return "'" + str(s).replace("'", "'\\''") + "'"


def reexec_clean() -> None:
    """Re-exec once through env.sh so the heavy torch import sees a scrubbed
    LD_LIBRARY_PATH even when invoked from a conda shell. Guarded by _GEV_CLEANED.
    """
    if os.environ.get("_GEV_CLEANED") == "1" or not ENV_SH.exists():
        clean_ld_environment()
        return
    os.environ["_GEV_CLEANED"] = "1"
    cmd = (f'source {sh(str(ENV_SH))}; exec "$UV" run {sh(str(Path(__file__).resolve()))} '
           + " ".join(sh(a) for a in sys.argv[1:]))
    log("re-exec through env.sh for a clean LD_LIBRARY_PATH")
    os.execvp("bash", ["bash", "-lc", cmd])


# --------------------------------------------------------------------------- #
# GPU selection (single-card pin; must run BEFORE torch import)
# --------------------------------------------------------------------------- #
def freest_gpu_index() -> int:
    """Pick the GPU with the most free VRAM via nvidia-smi. 0 if unknown."""
    smi = "nvidia-smi"
    try:
        out = subprocess.run(
            [smi, "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15,
        )
        frees = [int(x) for x in out.stdout.split()]
        if frees:
            return max(range(len(frees)), key=lambda i: frees[i])
    except Exception as exc:  # noqa: BLE001
        log(f"nvidia-smi probe failed ({exc}); defaulting to GPU 0")
    return 0


def pin_single_gpu(idx: int) -> None:
    """Restrict torch to one physical GPU. MUST be set before torch import."""
    os.environ["CUDA_VISIBLE_DEVICES"] = str(idx)
    log(f"pinned to physical GPU {idx} (CUDA_VISIBLE_DEVICES={idx}; torch sees it as cuda:0)")


# --------------------------------------------------------------------------- #
# ffmpeg helpers (extract frames / probe fps / reassemble)
# --------------------------------------------------------------------------- #
def run(cmd: list) -> None:
    env = os.environ.copy()
    env.pop("_GEV_CLEANED", None)
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"command failed ({res.returncode}): {' '.join(map(str, cmd))}\n{res.stderr.strip()}"
        )


def probe_fps(video: str) -> float:
    """Return the source video's frame rate (falls back to 24)."""
    try:
        out = subprocess.run(
            [FFPROBE, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", video],
            capture_output=True, text=True, timeout=30,
        )
        s = out.stdout.strip()
        if "/" in s:
            n, d = s.split("/")
            return float(n) / float(d) if float(d) else 24.0
        return float(s) if s else 24.0
    except Exception:  # noqa: BLE001
        return 24.0


def extract_frames(video: str, out_dir: Path, fps: float | None) -> list[Path]:
    """Extract frames to PNG (frame_000000.png ...). Lossless, resume-safe-ish."""
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(out_dir.glob("frame_*.png"))
    if existing:
        log(f"frames already extracted: {len(existing)} in {out_dir} (skip extract)")
        return existing
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", video]
    if fps:
        cmd += ["-vf", f"fps={fps}"]
    cmd += ["-start_number", "0", str(out_dir / "frame_%06d.png")]
    log(f"extracting frames -> {out_dir}" + (f" @ {fps}fps" if fps else " (source fps)"))
    run(cmd)
    frames = sorted(out_dir.glob("frame_*.png"))
    if not frames:
        raise RuntimeError(f"no frames extracted from {video}")
    log(f"extracted {len(frames)} frames")
    return frames


def snap8(v: int) -> int:
    """SDXL VAE stride: round dimension to a multiple of 8."""
    return max(8, (v // 8) * 8)


# --------------------------------------------------------------------------- #
# Core: build pipeline + transform frames
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        description="NSFW video-to-video style transfer (real<->anime) with a locked "
                    "character: per-frame SDXL img2img + ControlNet(OpenPose/Depth) + "
                    "IP-Adapter Plus-Face. ComfyUI-free, diffusers-native.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # real -> anime (Pony), pose+depth, face-lock from a reference still, GPU 1\n"
            "  gen_v2v_style.py --in real.mp4 --out anime.mp4 \\\n"
            "      --style-model pony --gpu 1 \\\n"
            "      --face-ref char_face.png --face-scale 0.7 \\\n"
            "      --controlnet openpose,depth --strength 0.72 \\\n"
            "      --prompt 'score_9, score_8_up, source_anime, 1girl, anime style, ...'\n\n"
            "  # print the chosen backend/GPU and exit (no generation)\n"
            "  gen_v2v_style.py --in real.mp4 --out a.mp4 --prompt '...' --print-decision\n"
        ),
    )
    ap.add_argument("--in", dest="input", required=True, help="source video to restyle")
    ap.add_argument("--out", required=True, help="output mp4")
    ap.add_argument("--prompt", required=True, help="target-style prompt (same for EVERY frame)")
    ap.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE,
                    help="fixed negative applied to every frame (anti-drift). '' to disable.")
    ap.add_argument("--style-model", default="pony", choices=list(STYLE_MODELS),
                    help="SDXL style base (anime: pony/noobai-xl[-vpred]/manga-vision-il; "
                         "real-ish: sdxl). Default pony.")
    ap.add_argument("--style-repo", default=None,
                    help="override the HF repo of the style base (e.g. a real-photo SDXL "
                         "checkpoint). Scheduler quirks follow --style-model.")
    ap.add_argument("--controlnet", default="openpose,depth",
                    help="comma list of motion controls: openpose,depth,canny (default openpose,depth). "
                         "'' = none (img2img only).")
    ap.add_argument("--cn-scale", default=None,
                    help="comma list of conditioning scales matching --controlnet "
                         "(default 1.0 for pose, 0.6 for depth/canny).")
    ap.add_argument("--openpose-include-face", action="store_true",
                    help="include OpenPose face landmarks. Default off: tiny real-video face keypoints "
                         "often fight anime face synthesis on Pony/SDXL.")
    ap.add_argument("--strength", type=float, default=0.72,
                    help="img2img denoise. 0.65-0.8 is safer for real->anime faces; "
                         "0.35-0.55 keeps more source texture. Default 0.72.")
    ap.add_argument("--face-ref", default=None,
                    help="reference still of the character's FACE (locks identity via IP-Adapter "
                         "Plus-Face). Omit to skip face-lock.")
    ap.add_argument("--face-scale", type=float, default=0.7,
                    help="IP-Adapter scale 0.5-0.9 (higher = stronger identity). Default 0.7.")
    ap.add_argument("--face-ref-crop", choices=["auto", "detect", "none"], default="auto",
                    help="crop --face-ref to the detected face before feeding IP-Adapter. "
                         "auto falls back to an upper-body crop if detection fails. Default auto.")
    ap.add_argument("--face-ref-crop-pad", type=float, default=2.4,
                    help="face-ref crop expansion multiplier around the detected face. Default 2.4.")
    ap.add_argument("--min-face-px", type=int, default=96,
                    help="avoid shrinking frames when a detected face would fall below this width. "
                         "0 disables. Default 96.")
    ap.add_argument("--no-face-safe-resize", action="store_true",
                    help="do not override --max-side shrinking to preserve tiny detected faces.")
    ap.add_argument("--face-refine", choices=["auto", "on", "off"], default="auto",
                    help="ADetailer-like second img2img pass on the detected face crop. "
                         "auto enables it for small faces. Default auto.")
    ap.add_argument("--face-refine-size", type=int, default=512,
                    help="square working size for face refinement, snapped to /8. Default 512.")
    ap.add_argument("--face-refine-strength", type=float, default=0.5,
                    help="denoise for face-only refinement. Default 0.5.")
    ap.add_argument("--face-refine-steps", type=int, default=None,
                    help="steps for face-only refinement (default: max(12, --steps//2)).")
    ap.add_argument("--face-refine-pad", type=float, default=2.0,
                    help="face crop expansion multiplier for face-only refinement. Default 2.0.")
    ap.add_argument("--blend-prev", type=float, default=0.0,
                    help="EXPERIMENTAL temporal carry: fraction of the PREVIOUS transformed frame "
                         "blended into the next init image. Default 0 (OFF) — it ACCUMULATES "
                         "degradation: each frame eats its own slightly-worse output, so faces and "
                         "backgrounds rot toward the end of a clip (verified: >0 caused face collapse "
                         "+ rainbow noise in later frames). Only try a SMALL value (~0.1) on very "
                         "short clips, and inspect the tail. Anti-flicker comes from fixed seed + "
                         "same prompt/model/negative + ControlNet, NOT from this.")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--seed", type=int, default=12345, help="FIXED across all frames (anti-drift).")
    ap.add_argument("--fps", type=float, default=None, help="resample source to this fps before/after (default: keep source).")
    ap.add_argument("--max-side", type=int, default=1024,
                    help="longest output side in px (SDXL likes ~1024). Default 1024. "
                         "Shrink-only unless --allow-upscale.")
    ap.add_argument("--allow-upscale", action="store_true",
                    help="allow scaling sources SMALLER than --max-side up to it "
                         "(default: only shrink larger sources, never upscale).")
    ap.add_argument("--gpu", type=int, default=None, help="pin to this physical GPU (default: freest).")
    ap.add_argument("--offload", action="store_true", help="cpu-offload the pipeline (slower, less VRAM).")
    ap.add_argument("--work-dir", default=None,
                    help="scratch dir for frames (default: <out>.frames next to --out).")
    ap.add_argument("--start", type=int, default=0, help="first frame index to process (resume).")
    ap.add_argument("--end", type=int, default=None, help="last frame index (exclusive); default all.")
    ap.add_argument("--print-decision", action="store_true",
                    help="print GPU/backend decision as JSON and exit (no generation).")
    args = ap.parse_args()

    # ---- decide GPU first (before torch import) ----
    gpu = args.gpu if args.gpu is not None else freest_gpu_index()

    if args.print_decision:
        decision = {
            "task": "v2v-style",
            "style_model": args.style_model,
            "style_repo": args.style_repo or STYLE_MODELS[args.style_model]["repo"],
            "controlnets": [c for c in args.controlnet.split(",") if c],
            "face_lock": bool(args.face_ref),
            "face_ref_crop": args.face_ref_crop,
            "face_refine": args.face_refine,
            "openpose_include_face": bool(args.openpose_include_face),
            "gpu": gpu,
            "offload": bool(args.offload),
            "strength": args.strength,
            "blend_prev": args.blend_prev,
            "backend": "local-offload" if args.offload else "local-single",
            "device": f"cuda:{gpu}",
        }
        print(json.dumps(decision))
        log(f"decision: {decision['backend']} on GPU {gpu}; "
            f"style={decision['style_repo']}; cn={decision['controlnets']}; "
            f"face_lock={decision['face_lock']}")
        return 0

    out_path = Path(args.out).expanduser().resolve()
    if out_path.exists() and out_path.stat().st_size > 0:
        log(f"output already exists, skipping: {out_path}")
        print(str(out_path))
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pin_single_gpu(gpu)

    # ---- imports (now that GPU is pinned and LD is clean) ----
    import numpy as np  # noqa: PLC0415
    import torch  # noqa: PLC0415
    from PIL import Image, ImageDraw, ImageFilter, ImageOps  # noqa: PLC0415
    from diffusers import (  # noqa: PLC0415
        AutoencoderKL,
        ControlNetModel,
        EulerAncestralDiscreteScheduler,
        EulerDiscreteScheduler,
        StableDiffusionXLControlNetImg2ImgPipeline,
        StableDiffusionXLImg2ImgPipeline,
    )
    from transformers import CLIPVisionModelWithProjection  # noqa: PLC0415

    dtype = torch.float16  # SDXL ControlNet/IP-Adapter stack is fp16-native (xinsir spec)

    spec = STYLE_MODELS[args.style_model]
    repo = args.style_repo or spec["repo"]
    steps = args.steps if args.steps is not None else spec["default_steps"]
    guidance = args.guidance if args.guidance is not None else spec["default_guidance"]

    cn_names = [c.strip() for c in args.controlnet.split(",") if c.strip()]
    for c in cn_names:
        if c not in CONTROLNETS:
            log(f"unknown controlnet '{c}'; valid: {list(CONTROLNETS)}")
            return 2
    if args.strength < 0.65 and args.style_model in {"pony", "noobai-xl", "noobai-xl-vpred", "manga-vision-il"}:
        log(f"warning: --strength {args.strength} is low for real->anime face redraw; "
            "0.7-0.8 is usually safer when the source face is small or photoreal")

    def clamp_box(box: tuple[int, int, int, int], w: int, h: int) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = box
        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(x1 + 1, min(w, x2))
        y2 = max(y1 + 1, min(h, y2))
        return x1, y1, x2, y2

    def expand_square_box(
        box: tuple[int, int, int, int],
        image_size: tuple[int, int],
        pad: float,
    ) -> tuple[int, int, int, int]:
        w, h = image_size
        x1, y1, x2, y2 = box
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        side = max(x2 - x1, y2 - y1) * max(1.0, pad)
        side = min(side, float(max(w, h)))
        nx1 = int(round(cx - side / 2.0))
        ny1 = int(round(cy - side / 2.0))
        nx2 = int(round(cx + side / 2.0))
        ny2 = int(round(cy + side / 2.0))
        if nx1 < 0:
            nx2 -= nx1
            nx1 = 0
        if ny1 < 0:
            ny2 -= ny1
            ny1 = 0
        if nx2 > w:
            nx1 -= nx2 - w
            nx2 = w
        if ny2 > h:
            ny1 -= ny2 - h
            ny2 = h
        return clamp_box((nx1, ny1, nx2, ny2), w, h)

    def detect_face_box(img: Image.Image) -> tuple[int, int, int, int] | None:
        """Detect the most useful face box with OpenCV cascades; no insightface."""
        try:
            import cv2  # noqa: PLC0415
        except Exception as exc:  # noqa: BLE001
            log(f"OpenCV unavailable for face detection ({exc})")
            return None

        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape[:2]
        candidates: list[tuple[float, tuple[int, int, int, int]]] = []

        cascade_names = [
            ("haarcascade_frontalface_alt2.xml", False),
            ("haarcascade_frontalface_default.xml", False),
            ("haarcascade_profileface.xml", False),
            ("haarcascade_profileface.xml", True),
        ]
        for name, flipped in cascade_names:
            path = Path(cv2.data.haarcascades) / name
            if not path.exists():
                continue
            cascade = cv2.CascadeClassifier(str(path))
            if cascade.empty():
                continue
            base = cv2.flip(gray, 1) if flipped else gray
            for up in (1.0, 1.5, 2.0):
                if up == 1.0:
                    scaled = base
                else:
                    scaled = cv2.resize(base, None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC)
                min_face = max(20, int(min(w, h) * 0.035 * up))
                faces = cascade.detectMultiScale(
                    scaled,
                    scaleFactor=1.06,
                    minNeighbors=4,
                    flags=cv2.CASCADE_SCALE_IMAGE,
                    minSize=(min_face, min_face),
                )
                for x, y, fw, fh in faces:
                    ox1 = int(round(x / up))
                    oy1 = int(round(y / up))
                    ox2 = int(round((x + fw) / up))
                    oy2 = int(round((y + fh) / up))
                    if flipped:
                        ox1, ox2 = w - ox2, w - ox1
                    box = clamp_box((ox1, oy1, ox2, oy2), w, h)
                    bx1, by1, bx2, by2 = box
                    area = (bx2 - bx1) * (by2 - by1)
                    upper_bias = 1.25 if (by1 + by2) / 2.0 < h * 0.62 else 1.0
                    candidates.append((area * upper_bias, box))
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]

    def fallback_upper_face_crop(img: Image.Image) -> Image.Image:
        w, h = img.size
        side = min(w, max(256, int(round(h * 0.48))))
        x1 = max(0, (w - side) // 2)
        y1 = 0
        return img.crop(clamp_box((x1, y1, x1 + side, y1 + side), w, h))

    def make_face_ref_image(img: Image.Image) -> Image.Image:
        if args.face_ref_crop == "none":
            log(f"face-ref crop disabled; using full reference image {img.size}")
            return img
        box = detect_face_box(img)
        if box:
            crop_box = expand_square_box(box, img.size, args.face_ref_crop_pad)
            crop = img.crop(crop_box)
            log(f"face-ref cropped from {img.size} to {crop.size} using detected face box {box}")
            return crop
        if args.face_ref_crop == "auto":
            crop = fallback_upper_face_crop(img)
            log(f"face-ref face detection failed; using upper fallback crop {crop.size} from {img.size}")
            return crop
        log("face-ref face detection failed; using full reference image")
        return img

    def scale_box(
        box: tuple[int, int, int, int],
        sx: float,
        sy: float,
        size: tuple[int, int],
    ) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = box
        w, h = size
        return clamp_box(
            (int(round(x1 * sx)), int(round(y1 * sy)), int(round(x2 * sx)), int(round(y2 * sy))),
            w,
            h,
        )

    def paste_feathered(base: Image.Image, patch: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
        x1, y1, x2, y2 = box
        patch = patch.resize((x2 - x1, y2 - y1), Image.LANCZOS)
        mask = Image.new("L", patch.size, 0)
        draw = ImageDraw.Draw(mask)
        feather = max(8, min(patch.size) // 10)
        draw.rectangle((feather, feather, patch.size[0] - feather, patch.size[1] - feather), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max(2, feather // 2)))
        merged = base.copy()
        merged.paste(patch, (x1, y1), mask)
        return merged

    # ---- frame extraction ----
    work_dir = Path(args.work_dir).expanduser().resolve() if args.work_dir \
        else out_path.with_suffix(out_path.suffix + ".frames")
    src_frames = extract_frames(args.input, work_dir / "src", args.fps)
    out_frames_dir = work_dir / "out"
    out_frames_dir.mkdir(parents=True, exist_ok=True)
    src_fps = args.fps or probe_fps(args.input)

    end = args.end if args.end is not None else len(src_frames)
    end = min(end, len(src_frames))
    if args.start >= end:
        log(f"nothing to do: start={args.start} >= end={end}")
        return 2

    # ---- annotators (controlnet_aux) — loaded once ----
    pose_anno = depth_anno = None
    if "openpose" in cn_names:
        from controlnet_aux import OpenposeDetector  # noqa: PLC0415
        log("loading OpenposeDetector (lllyasviel/Annotators)")
        pose_anno = OpenposeDetector.from_pretrained("lllyasviel/Annotators")
    if "depth" in cn_names:
        from controlnet_aux import MidasDetector  # noqa: PLC0415
        log("loading MidasDetector (lllyasviel/Annotators)")
        depth_anno = MidasDetector.from_pretrained("lllyasviel/Annotators")

    def make_control_maps(frame_img):
        """Build the control_image list in the SAME order as cn_names."""
        maps = []
        for c in cn_names:
            if c == "openpose":
                maps.append(
                    pose_anno(
                        frame_img,
                        include_hand=True,
                        include_face=bool(args.openpose_include_face),
                    )
                )
            elif c == "depth":
                maps.append(depth_anno(frame_img))
            elif c == "canny":
                import cv2  # noqa: PLC0415
                arr = cv2.Canny(np.array(frame_img), 100, 200)
                arr = np.stack([arr] * 3, axis=-1)
                maps.append(Image.fromarray(arr))
        return maps

    # ---- ControlNet models ----
    controlnets = []
    for c in cn_names:
        log(f"loading ControlNet {c}: {CONTROLNETS[c]}")
        controlnets.append(ControlNetModel.from_pretrained(CONTROLNETS[c], torch_dtype=dtype))

    # ---- VAE (fp16-fix avoids black frames) + image encoder for IP-Adapter ----
    vae = AutoencoderKL.from_pretrained(SDXL_VAE_FP16_FIX, torch_dtype=dtype)
    image_encoder = None
    if args.face_ref:
        log(f"loading IP-Adapter image encoder (ViT-H): {IPADAPTER_REPO}/{IPADAPTER_IMAGE_ENCODER_SUBFOLDER}")
        image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            IPADAPTER_REPO, subfolder=IPADAPTER_IMAGE_ENCODER_SUBFOLDER, torch_dtype=dtype)

    # ---- pipeline (ControlNet img2img, or plain img2img if no controlnet) ----
    log(f"loading style base {args.style_model} ({repo}); controlnets={cn_names or 'none'}; "
        f"offload={args.offload}; strength={args.strength}; seed={args.seed}")
    pipe_kwargs = dict(vae=vae, torch_dtype=dtype)
    if image_encoder is not None:
        pipe_kwargs["image_encoder"] = image_encoder
    if controlnets:
        pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
            repo, controlnet=controlnets if len(controlnets) > 1 else controlnets[0], **pipe_kwargs)
    else:
        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(repo, **pipe_kwargs)

    # ---- scheduler fixes (mirror gen_image.py) ----
    if spec.get("vpred"):
        pipe.scheduler = pipe.scheduler.from_config(
            pipe.scheduler.config, prediction_type="v_prediction", rescale_betas_zero_snr=True)
        log(f"{args.style_model}: scheduler set to v_prediction + zero-SNR")
    elif spec.get("force_euler"):
        pipe.scheduler = EulerDiscreteScheduler(
            beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear",
            prediction_type="epsilon", steps_offset=1, timestep_spacing="leading")
        log(f"{args.style_model}: scheduler forced to EulerDiscreteScheduler (eps/scaled_linear)")
    else:
        # EulerAncestral is xinsir's recommended SDXL-ControlNet scheduler.
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
        log(f"{args.style_model}: scheduler -> EulerAncestralDiscreteScheduler")

    if args.offload:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    # ---- IP-Adapter Plus-Face (CLIP ViT-H; no insightface) ----
    face_ref_img = None
    if args.face_ref:
        log(f"loading IP-Adapter Plus-Face: {IPADAPTER_REPO}/sdxl_models/{IPADAPTER_FACE_WEIGHT} "
            f"(scale={args.face_scale})")
        pipe.load_ip_adapter(IPADAPTER_REPO, subfolder="sdxl_models",
                             weight_name=IPADAPTER_FACE_WEIGHT)
        pipe.set_ip_adapter_scale(args.face_scale)
        face_ref_src = ImageOps.exif_transpose(Image.open(args.face_ref)).convert("RGB")
        face_ref_img = make_face_ref_image(face_ref_src)

    # ---- compel long-prompt embeddings (Pony score-tag prompts > 77 tokens) ----
    prompt_embeds = pooled = neg_embeds = neg_pooled = None
    used_compel = False
    try:
        from compel import Compel, ReturnedEmbeddingsType  # noqa: PLC0415
        compel = Compel(
            tokenizer=[pipe.tokenizer, pipe.tokenizer_2],
            text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
            returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
            requires_pooled=[False, True],
            truncate_long_prompts=False,
        )
        prompt_embeds, pooled = compel(args.prompt)
        if args.negative_prompt:
            neg_embeds, neg_pooled = compel(args.negative_prompt)
            prompt_embeds, neg_embeds = compel.pad_conditioning_tensors_to_same_length(
                [prompt_embeds, neg_embeds])
        used_compel = True
        log("compel long-prompt embeddings (no 77-token truncation)")
    except Exception as exc:  # noqa: BLE001
        log(f"compel unavailable ({exc}); falling back to truncated prompt strings")

    def text_kwargs() -> dict:
        if used_compel:
            kw = {"prompt_embeds": prompt_embeds, "pooled_prompt_embeds": pooled}
            if neg_embeds is not None:
                kw["negative_prompt_embeds"] = neg_embeds
                kw["negative_pooled_prompt_embeds"] = neg_pooled
            return kw
        kw = {"prompt": args.prompt}
        if args.negative_prompt:
            kw["negative_prompt"] = args.negative_prompt
        return kw

    # default conditioning scales: pose strong, depth/canny softer
    if args.cn_scale:
        cn_scales = [float(x) for x in args.cn_scale.split(",") if x.strip()]
        if len(cn_scales) != len(cn_names):
            log(f"--cn-scale count {len(cn_scales)} != controlnet count {len(cn_names)}")
            return 2
    else:
        cn_scales = [1.0 if c == "openpose" else 0.6 for c in cn_names]

    # ---- per-frame loop ----
    base_text = text_kwargs()
    prev_out = None
    n_done = 0
    face_refine_steps = args.face_refine_steps if args.face_refine_steps is not None else max(12, steps // 2)
    face_refine_size = snap8(args.face_refine_size)

    def pipe_call_kwargs(
        image: Image.Image,
        strength: float,
        generator_seed: int,
        num_steps: int,
        control_images=None,
        control_scales=None,
    ) -> dict:
        kw = dict(base_text)
        kw.update(
            image=image,
            strength=strength,
            num_inference_steps=num_steps,
            guidance_scale=guidance,
            generator=torch.Generator("cpu").manual_seed(generator_seed),
        )
        if control_images is not None:
            kw["control_image"] = control_images
            kw["controlnet_conditioning_scale"] = control_scales
        if face_ref_img is not None:
            kw["ip_adapter_image"] = face_ref_img
        return kw

    def refine_face_if_needed(
        out_img: Image.Image,
        detected_face_box: tuple[int, int, int, int] | None,
    ) -> Image.Image:
        if args.face_refine == "off" or detected_face_box is None:
            return out_img
        fw = detected_face_box[2] - detected_face_box[0]
        should_refine = args.face_refine == "on" or fw < max(args.min_face_px, 1) * 1.35
        if not should_refine:
            return out_img

        crop_box = expand_square_box(detected_face_box, out_img.size, args.face_refine_pad)
        face_init = out_img.crop(crop_box).resize((face_refine_size, face_refine_size), Image.LANCZOS)
        refine_kwargs = pipe_call_kwargs(
            image=face_init,
            strength=args.face_refine_strength,
            generator_seed=args.seed + 100_003,
            num_steps=face_refine_steps,
        )
        if controlnets:
            blank = Image.new("RGB", (face_refine_size, face_refine_size), (0, 0, 0))
            refine_maps = [blank.copy() for _ in cn_names]
            refine_kwargs["control_image"] = refine_maps if len(refine_maps) > 1 else refine_maps[0]
            zero_scales = [0.0 for _ in cn_names]
            refine_kwargs["controlnet_conditioning_scale"] = (
                zero_scales if len(zero_scales) > 1 else zero_scales[0])
        refined = pipe(**refine_kwargs).images[0]
        return paste_feathered(out_img, refined, crop_box)

    for i in range(args.start, end):
        src = src_frames[i]
        dst = out_frames_dir / f"frame_{i:06d}.png"
        if dst.exists() and dst.stat().st_size > 0:
            prev_out = ImageOps.exif_transpose(Image.open(dst)).convert("RGB")
            continue

        raw_frame_img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        raw_face_box = detect_face_box(raw_frame_img) if (
            args.min_face_px > 0
            or args.face_refine != "off"
            or args.face_ref_crop != "none"
        ) else None
        # size: scale longest side to --max-side, snap to /8. Shrink-only by
        # default — upscaling a low-res source feeds a blurry init into img2img
        # and wastes VRAM; pass --allow-upscale to scale small sources up to
        # SDXL's ~1024 sweet spot when you want that.
        w, h = raw_frame_img.size
        scale = args.max_side / max(w, h)
        if not args.allow_upscale:
            scale = min(1.0, scale)
        if (
            raw_face_box is not None
            and args.min_face_px > 0
            and not args.no_face_safe_resize
        ):
            raw_fw = raw_face_box[2] - raw_face_box[0]
            if raw_fw > 0 and raw_fw * scale < args.min_face_px:
                face_scale = args.min_face_px / raw_fw
                if not args.allow_upscale:
                    face_scale = min(1.0, face_scale)
                if face_scale > scale:
                    log(f"frame {i}: preserving small face ({raw_fw * scale:.0f}px -> "
                        f"{raw_fw * face_scale:.0f}px); effective max-side "
                        f"{round(max(w, h) * face_scale)} overrides requested {args.max_side}")
                    scale = face_scale
        ow, oh = snap8(round(w * scale)), snap8(round(h * scale))
        frame_img = raw_frame_img
        if (ow, oh) != (w, h):
            frame_img = raw_frame_img.resize((ow, oh), Image.LANCZOS)
        frame_face_box = scale_box(raw_face_box, ow / w, oh / h, (ow, oh)) if raw_face_box else None

        # init image: optionally blend the previous transformed frame in (temporal carry)
        init_img = frame_img
        if prev_out is not None and args.blend_prev > 0:
            pv = prev_out.resize((ow, oh), Image.LANCZOS)
            init_img = Image.blend(frame_img, pv, args.blend_prev)

        call_kwargs = pipe_call_kwargs(
            image=init_img,
            strength=args.strength,
            generator_seed=args.seed,
            num_steps=steps,
        )
        if controlnets:
            maps = [m.resize((ow, oh), Image.LANCZOS) for m in make_control_maps(frame_img)]
            call_kwargs["control_image"] = maps if len(maps) > 1 else maps[0]
            call_kwargs["controlnet_conditioning_scale"] = (
                cn_scales if len(cn_scales) > 1 else cn_scales[0])

        out_img = pipe(**call_kwargs).images[0]
        out_img = refine_face_if_needed(out_img, frame_face_box)
        out_img.save(dst)
        prev_out = out_img
        n_done += 1
        if n_done == 1 or n_done % 10 == 0 or i == end - 1:
            log(f"frame {i - args.start + 1}/{end - args.start} (idx {i}) -> {dst.name}")

    # ---- reassemble (exactly the processed range, in order) ----
    # Use a concat-demuxer list of the EXACT frames in [start, end) rather than an
    # image2 sequence + -start_number: the sequence demuxer stops at the first gap,
    # so a resumed/partial run with a hole would silently truncate or drop the tail.
    # The explicit list is gap-proof and fails loudly if a frame in the range is
    # missing instead of producing a short/holed video.
    expected = [out_frames_dir / f"frame_{i:06d}.png" for i in range(args.start, end)]
    missing = [p.name for p in expected if not (p.exists() and p.stat().st_size > 0)]
    if missing:
        raise RuntimeError(
            f"{len(missing)} output frame(s) missing in [{args.start},{end}); "
            f"first few: {missing[:5]}. Re-run the missing range before reassembly."
        )
    log(f"reassembling {len(expected)} frames @ {src_fps:.3f}fps -> {out_path}")
    concat_list = out_frames_dir / "_concat.txt"
    # concat demuxer needs a duration per still + a fps filter to realise it.
    dur = 1.0 / src_fps if src_fps else 1.0 / 24.0
    lines = []
    for p in expected:
        lines.append(f"file {sh(str(p))}")
        lines.append(f"duration {dur:.6f}")
    lines.append(f"file {sh(str(expected[-1]))}")  # last frame repeated (concat quirk)
    concat_list.write_text("\n".join(lines) + "\n")
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "concat", "-safe", "0", "-i", str(concat_list),
           "-vsync", "cfr", "-r", f"{src_fps}",
           "-vf", "scale=-2:trunc(ih/2)*2,setsar=1", "-pix_fmt", "yuv420p",
           "-c:v", "libx264", "-crf", "17", "-preset", "slow",
           "-movflags", "+faststart", str(out_path)]
    run(cmd)
    log(f"WROTE {out_path}")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    # Re-exec through env.sh for a clean LD_LIBRARY_PATH before torch import
    # (skip for the lightweight --print-decision / --help paths).
    if "--print-decision" not in sys.argv and "--help" not in sys.argv and "-h" not in sys.argv:
        reexec_clean()
    raise SystemExit(main())
