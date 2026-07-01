#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "torch==2.5.1",
#   "torchvision==0.20.1",
#   "diffusers @ git+https://github.com/huggingface/diffusers",
#   "transformers>=4.56",
#   "accelerate",
#   "peft",
#   "pillow",
#   "sentencepiece",
#   "protobuf",
#   "safetensors",
# ]
#
# # cu121 torch: this rig's driver is CUDA 12.2; default wheels target newer CUDA
# # and fail. torchvision required for Qwen image processors. Same pin as gen_qwen_edit.py.
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
gen_v2v_qwen.py — video-to-video ANIME stylization that KEEPS THE SAME PERSON,
using Qwen-Image-Edit (2509/2511) + an anime LoRA, frame by frame.

WHY this exists (and why the SDXL+IP-Adapter path was wrong): a real human video
must become anime while staying the SAME person every frame. Qwen-Image-Edit is
a reference/instruction editor that preserves identity (face/hair/bangs) — the
skill's established answer for "reference NSFW = Qwen-Image-Edit". The anime LoRA
`prithivMLmods/Qwen-Image-Edit-2511-Anime` (trigger "Transform into anime.")
restyles to anime while, per its card, "preserving the original pose, subject
proportions, viewing angle, and camera perspective" — exactly what frame-by-frame
needs. Verified on a single A/B frame: Qwen+LoRA kept the exact expression/pose;
the earlier Pony+IP-Adapter path produced a generic different anime face.

This loads the model ONCE and streams all frames through it (vs gen_qwen_edit.py
which reloads per call). Temporal coherence levers: FIXED seed, SAME prompt, SAME
model+LoRA every frame. (Per-frame editors still have residual flicker — that is
inherent; smooth in post if needed.)

Pipeline: ffmpeg extract @ --fps -> per-frame Qwen-Edit+LoRA -> ffmpeg reassemble
to the ORIGINAL duration (so dropping fps does not change the clip length).

Resume-safe: existing per-frame PNGs and a non-empty --out are skipped.
Output contract: WHY logs to stderr; final mp4 abs path to stdout.

NSFW: runs entirely LOCAL (Qwen-Image-Edit is uncensored locally). Nothing leaves
the box.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_SH = SCRIPT_DIR / "env.sh"
UV = os.environ.get("UV") or "/home/kita/.local/bin/uv"
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

DEFAULT_BASE = "Qwen/Qwen-Image-Edit-2511"
DEFAULT_ANIME_LORA = "prithivMLmods/Qwen-Image-Edit-2511-Anime"
ANIME_TRIGGER = "Transform into anime."
DEFAULT_NEG = (
    "deformed hands, extra fingers, distorted faces, fused bodies, extra limbs, "
    "warping, watermark, text, logo, low quality, blurry, jpeg artifacts"
)


def log(msg: str) -> None:
    print(f"[gen_v2v_qwen] {msg}", file=sys.stderr, flush=True)


# ---- clean LD / re-exec through env.sh so torch loads without conda libtinfo ----
def clean_ld_environment() -> None:
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [p for p in ld.split(os.pathsep)
                if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p]
        new = os.pathsep.join(kept)
        if new:
            os.environ["LD_LIBRARY_PATH"] = new
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")


def sh(s) -> str:
    return "'" + str(s).replace("'", "'\\''") + "'" if s is not None else "''"


def reexec_clean() -> None:
    if os.environ.get("_GEV_CLEANED") == "1" or not ENV_SH.exists():
        clean_ld_environment()
        return
    os.environ["_GEV_CLEANED"] = "1"
    cmd = (f'source {sh(str(ENV_SH))}; exec "$UV" run {sh(str(Path(__file__).resolve()))} '
           + " ".join(sh(a) for a in sys.argv[1:]))
    log("re-exec through env.sh for a clean LD_LIBRARY_PATH")
    os.execvp("bash", ["bash", "-lc", cmd])


def run(cmd: list) -> None:
    env = os.environ.copy()
    env.pop("_GEV_CLEANED", None)
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"cmd failed ({res.returncode}): {' '.join(map(str, cmd))}\n{res.stderr.strip()}")


def probe_fps(video: str) -> float:
    try:
        out = subprocess.run(
            [FFPROBE, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", video],
            capture_output=True, text=True, timeout=30)
        s = out.stdout.strip()
        if "/" in s:
            n, d = s.split("/")
            return float(n) / float(d) if float(d) else 24.0
        return float(s) if s else 24.0
    except Exception:  # noqa: BLE001
        return 24.0


def snap16(v: int) -> int:
    return max(16, int(round(v / 16) * 16))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Video->anime keeping the SAME person, via Qwen-Image-Edit + anime LoRA, frame by frame.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--in", dest="input", required=True, help="source video (real human)")
    ap.add_argument("--out", required=True, help="output mp4")
    ap.add_argument("--repo", default=DEFAULT_BASE, help=f"Qwen edit base. Default {DEFAULT_BASE}.")
    ap.add_argument("--lora", action="append", default=None,
                    help=f"LoRA hf-id|path. Repeatable to stack (e.g. anime + NSFW). "
                         f"Default (if none given) {DEFAULT_ANIME_LORA}. '' to disable all.")
    ap.add_argument("--lora-scale", action="append", type=float, default=None,
                    help="per-LoRA strength, matched to --lora order. "
                         "If fewer than --lora, the last value fills the rest. Default 1.0.")
    ap.add_argument("--prompt", default=ANIME_TRIGGER,
                    help=f"edit instruction (every frame). Default the LoRA trigger '{ANIME_TRIGGER}'.")
    ap.add_argument("--negative-prompt", default=DEFAULT_NEG)
    ap.add_argument("--fps", type=float, default=8.0,
                    help="frames per second to GENERATE (lower = fewer frames = faster). "
                         "Output is restored to the source duration. Default 8.")
    ap.add_argument("--max-side", type=int, default=1280,
                    help="longest side fed to Qwen (snapped /16). Default 1280 (~1MP).")
    ap.add_argument("--steps", type=int, default=8, help="inference steps (LoRA is a 4-8 step model).")
    ap.add_argument("--guidance", type=float, default=1.0, help="true_cfg_scale (LoRA wants ~1.0).")
    ap.add_argument("--seed", type=int, default=12345, help="FIXED across all frames (coherence).")
    ap.add_argument("--offload", choices=["none", "model", "sequential"], default="model")
    ap.add_argument("--gpu", type=int, default=None, help="pin to a physical GPU (before torch import).")
    ap.add_argument("--start", type=int, default=0, help="first frame index (resume).")
    ap.add_argument("--end", type=int, default=None, help="last frame index exclusive (default all).")
    ap.add_argument("--seconds", type=float, default=None,
                    help="only process the first N seconds of the source (quick test).")
    ap.add_argument("--work-dir", default=None, help="scratch dir for frames (default <out>.frames).")
    args = ap.parse_args()

    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
        log(f"pinned to physical GPU {args.gpu}")

    out_path = Path(args.out).expanduser().resolve()
    if out_path.exists() and out_path.stat().st_size > 0:
        log(f"output exists, skipping: {out_path}")
        print(str(out_path)); return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)

    work_dir = Path(args.work_dir).expanduser().resolve() if args.work_dir \
        else out_path.with_suffix(out_path.suffix + ".frames")
    src_dir = work_dir / "src"
    out_dir = work_dir / "out"
    src_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- extract frames at --fps ----
    existing = sorted(src_dir.glob("frame_*.png"))
    if not existing:
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y"]
        if args.seconds:
            cmd += ["-t", f"{args.seconds}"]
        cmd += ["-i", args.input, "-vf", f"fps={args.fps}", "-start_number", "0",
                str(src_dir / "frame_%06d.png")]
        log(f"extracting frames @ {args.fps}fps" + (f" (first {args.seconds}s)" if args.seconds else ""))
        run(cmd)
    src_frames = sorted(src_dir.glob("frame_*.png"))
    if not src_frames:
        raise RuntimeError("no frames extracted")
    log(f"{len(src_frames)} frames to stylize")

    end = min(args.end if args.end is not None else len(src_frames), len(src_frames))

    # ---- load model ONCE ----
    import torch  # noqa: PLC0415
    from PIL import Image, ImageOps  # noqa: PLC0415
    from diffusers import QwenImageEditPlusPipeline  # noqa: PLC0415

    log(f"loading {args.repo} (bf16); offload={args.offload}")
    pipe = QwenImageEditPlusPipeline.from_pretrained(args.repo, torch_dtype=torch.bfloat16)
    # Resolve LoRA list: default to the anime LoRA if the user gave none; '' disables all.
    lora_ids = args.lora if args.lora is not None else [DEFAULT_ANIME_LORA]
    lora_ids = [x for x in lora_ids if x]  # drop '' entries (disable)
    if lora_ids:
        scales = args.lora_scale or []
        # pad scales to match: last given value fills the rest, else 1.0
        while len(scales) < len(lora_ids):
            scales.append(scales[-1] if scales else 1.0)
        names = [f"lora{i}" for i in range(len(lora_ids))]
        for name, lid in zip(names, lora_ids):
            log(f"loading LoRA {lid} as '{name}'")
            pipe.load_lora_weights(lid, adapter_name=name)
        try:
            pipe.set_adapters(names, adapter_weights=scales[:len(names)])
            log(f"active LoRAs: {list(zip(lora_ids, scales[:len(names)]))}")
        except Exception as exc:  # noqa: BLE001
            log(f"set_adapters failed ({exc}); LoRAs at default weight")
    if args.offload == "model":
        pipe.enable_model_cpu_offload()
    elif args.offload == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.to("cuda")

    def load_resized(p: Path):
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        w, h = im.size
        scale = min(1.0, args.max_side / max(w, h))
        nw, nh = snap16(round(w * scale)), snap16(round(h * scale))
        return im.resize((nw, nh), Image.LANCZOS) if (nw, nh) != (w, h) else im

    # ---- per-frame loop (fixed seed/prompt/model for coherence) ----
    n_done = 0
    for i in range(args.start, end):
        dst = out_dir / f"frame_{i:06d}.png"
        if dst.exists() and dst.stat().st_size > 0:
            continue
        img = load_resized(src_frames[i])
        gen = torch.Generator(device="cpu").manual_seed(args.seed)
        out = pipe(
            image=[img],
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
            num_inference_steps=args.steps,
            true_cfg_scale=args.guidance,
            generator=gen,
        ).images[0]
        out.save(dst)
        n_done += 1
        if n_done == 1 or n_done % 5 == 0 or i == end - 1:
            log(f"frame {i - args.start + 1}/{end - args.start} (idx {i}) -> {dst.name}")

    # ---- reassemble to the ORIGINAL duration (so dropped fps != shorter clip) ----
    expected = [out_dir / f"frame_{i:06d}.png" for i in range(args.start, end)]
    missing = [p.name for p in expected if not (p.exists() and p.stat().st_size > 0)]
    if missing:
        raise RuntimeError(f"{len(missing)} stylized frames missing; first: {missing[:5]}")
    src_dur = None
    try:
        o = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", args.input], capture_output=True, text=True, timeout=30)
        src_dur = float(o.stdout.strip())
    except Exception:  # noqa: BLE001
        pass
    n = len(expected)
    # If we sub-sampled the source to --seconds, the output should be that long.
    target_dur = args.seconds if args.seconds else src_dur
    out_fps = (n / target_dur) if (target_dur and target_dur > 0) else args.fps
    log(f"reassembling {n} frames -> {out_path} (output fps {out_fps:.3f} to fill {target_dur}s)")
    concat_list = out_dir / "_concat.txt"
    dur = 1.0 / out_fps if out_fps else 1.0 / args.fps
    lines = []
    for p in expected:
        lines.append(f"file {sh(str(p))}")
        lines.append(f"duration {dur:.6f}")
    lines.append(f"file {sh(str(expected[-1]))}")
    concat_list.write_text("\n".join(lines) + "\n")
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "concat", "-safe", "0", "-i", str(concat_list),
           "-vsync", "cfr", "-r", f"{out_fps}",
           "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1", "-pix_fmt", "yuv420p",
           "-c:v", "libx264", "-crf", "16", "-preset", "slow",
           "-movflags", "+faststart", str(out_path)]
    run(cmd)
    log(f"WROTE {out_path}")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    if "--help" not in sys.argv and "-h" not in sys.argv:
        reexec_clean()
    raise SystemExit(main())
