#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
chain_video.py — build ONE long, continuous video by CHAINING image-to-video.

For each scene it takes the LAST FRAME of the previous clip, feeds that frame as
the --image to the next i2v generation, and so on. The result is a sequence of
short clips that flow into one another (the start of clip N matches the end of
clip N-1), suitable for 5-10 shot mini-sequences from a single starting still.

It does NOT generate video itself: it shells out to sibling scripts/gen_video.py
(via `uv run`, in a CONDA-SCRUBBED environment) once per scene, always with
--task i2v --image <last_frame_of_prev> --out <scenes_dir>/scene_<n>.mp4. The
last-frame extraction is done with ffmpeg (-sseof -0.1 -frames:v 1).

stdlib-only / PEP723. The only external programs it touches are ffmpeg and
scripts/gen_video.py (which itself owns all torch/diffusers/cloud logic).

---------------------------------------------------------------------------
STYLE-DRIFT MITIGATION (important — read this)
---------------------------------------------------------------------------
i2v chaining is lossy: each generation slightly re-interprets colour, lighting,
identity and rendering style, and re-encoding the seam frame adds compression
artefacts. Over 5-10 chained clips this COMPOUNDS into visible drift (the look
slowly mutates, faces morph, palette shifts). This script fights that with:

  1. A FIXED default negative prompt (--negative-prompt) that is applied to
     EVERY scene unless a scene overrides it in scenes.json. Pinning the same
     negatives across the whole chain keeps the model away from the same failure
     modes each step. The built-in default targets the usual drift symptoms:
     colour shift, style change, blur, flicker, warping, extra limbs, etc.
  2. A HIGH-QUALITY last-frame extract (PNG, lossless) so the seed frame fed to
     the next clip carries no extra JPEG/H.264 mush.
  3. Keeping a STABLE --model across the whole chain (one --model flag) instead
     of letting each clip pick a different backend, which would change the look.
  4. Per-scene prompts that should RE-STATE the persistent style descriptors
     (same subject, same lens, same palette) — see the example below. The
     prompt is your strongest anti-drift lever; restate the look every scene.

You can additionally reduce drift by re-using a fixed --seed-ish behaviour, but
gen_video.py owns seeding; pass it through scenes.json `model`/prompt as needed.

---------------------------------------------------------------------------
scenes.json SHAPE
---------------------------------------------------------------------------
A JSON ARRAY of scene objects. `prompt` is required; everything else optional
and, when present, overrides the chain-wide default for THAT scene only:

  [
    {
      "prompt": "same red fox, 35mm cinematic, teal-orange palette, trotting left across snow, slow dolly",
      "negative_prompt": "color shift, style change, blurry, flicker, extra limbs, warped face",
      "num_frames": 81
    },
    {
      "prompt": "same red fox, 35mm cinematic, teal-orange palette, stops and looks up at falling snow",
      "model": "wan2.2-i2v-a14b"
    },
    {
      "prompt": "same red fox, 35mm cinematic, teal-orange palette, leaps over a frozen log, motion blur on legs"
    }
  ]

Tip: keep the leading style descriptors IDENTICAL in every prompt.

---------------------------------------------------------------------------
EXAMPLES
---------------------------------------------------------------------------
  # Start from a still, generate 3 chained clips:
  chain_video.py --scenes-dir out/run1 --prompts-file scenes.json \\
      --first-image start.png

  # Start from an already-made clip 0 (its last frame seeds scene 1):
  chain_video.py --scenes-dir out/run1 --prompts-file scenes.json \\
      --first-clip out/run1/scene_0.mp4

  # Resume a partially-finished run (existing scene_*.mp4 are skipped):
  chain_video.py --scenes-dir out/run1 --prompts-file scenes.json \\
      --first-image start.png

  # Only (re)build scenes 3..5:
  chain_video.py --scenes-dir out/run1 --prompts-file scenes.json \\
      --first-image start.png --start 3 --end 5
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GEN_VIDEO_PY = SCRIPT_DIR / "gen_video.py"
EDIT_VIDEO_PY = SCRIPT_DIR / "edit_video.py"
ENV_SH = SCRIPT_DIR / "env.sh"
UV = os.environ.get("UV") or shutil.which("uv") or "/home/kita/.local/bin/uv"
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"

DEFAULT_MODEL = "wan2.2-i2v-a14b"

# A fixed, chain-wide negative prompt aimed squarely at the symptoms of i2v
# chaining drift. Applied to every scene that doesn't override it.
DEFAULT_NEGATIVE = (
    "color shift, color drift, style change, inconsistent style, inconsistent "
    "lighting, palette change, blurry, low quality, low resolution, jpeg "
    "artifacts, compression artifacts, flicker, flickering, ghosting, morphing, "
    "warping, distorted face, deformed, disfigured, extra limbs, extra fingers, "
    "duplicate, watermark, text, subtitles, oversaturated, washed out"
)


def log(msg: str) -> None:
    print(f"[chain_video] {msg}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Clean environment (strip anaconda libtinfo LD_LIBRARY_PATH pollution) so the
# ffmpeg and gen_video.py subprocesses don't inherit the broken conda libs.
# --------------------------------------------------------------------------- #
def clean_env() -> dict:
    env = os.environ.copy()
    ld = env.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p
            for p in ld.split(os.pathsep)
            if p
            and "anaconda" not in p
            and "miniconda" not in p
            and "conda" not in p
        ]
        new = os.pathsep.join(kept)
        if new:
            env["LD_LIBRARY_PATH"] = new
        else:
            env.pop("LD_LIBRARY_PATH", None)
        if new != ld:
            log("scrubbed conda paths from LD_LIBRARY_PATH for subprocesses")
    # Make sure the child python re-scrub guard in gen_video.py isn't tripped
    # by a stale flag inherited from some parent.
    env.pop("_GEV_CLEANED", None)
    env.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    return env


# --------------------------------------------------------------------------- #
# ffmpeg: extract the LAST frame of a clip as a lossless PNG.
# -sseof -0.1 seeks to 0.1s before EOF; -frames:v 1 grabs one frame from there.
# --------------------------------------------------------------------------- #
def extract_last_frame(clip: Path, out_png: Path, env: dict) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG,
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-sseof", "-0.1",
        "-i", str(clip),
        "-frames:v", "1",
        "-q:v", "1",
        str(out_png),
    ]
    log(f"ffmpeg extract last frame: {clip.name} -> {out_png.name}")
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0 or not out_png.exists():
        # Fallback: some short/odd clips have nothing 0.1s before EOF; grab the
        # very last decodable frame by walking the whole file instead.
        log("  -sseof grab failed; retrying with full-decode last-frame method")
        cmd2 = [
            FFMPEG,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(clip),
            "-vf", "select='eq(n\\,0)'+reverse",  # placeholder; replaced below
        ]
        # The robust portable fallback: decode all, keep only the final frame.
        cmd2 = [
            FFMPEG,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(clip),
            "-vsync", "vfr",
            "-q:v", "1",
            "-update", "1",
            "-frames:v", "1",
            "-vf", "reverse",
            str(out_png),
        ]
        res2 = subprocess.run(cmd2, env=env)
        if res2.returncode != 0 or not out_png.exists():
            raise RuntimeError(
                f"failed to extract last frame from {clip} (ffmpeg exit "
                f"{res.returncode}/{res2.returncode})"
            )


# --------------------------------------------------------------------------- #
# gen_video.py i2v call for one scene.
# --------------------------------------------------------------------------- #
def gen_scene(
    *,
    image: Path,
    out_mp4: Path,
    prompt: str,
    negative_prompt: str,
    model: str,
    num_frames: int | None,
    fps: int | None,
    backend: str | None,
    env: dict,
) -> None:
    cmd = [
        UV, "run", str(GEN_VIDEO_PY),
        "--task", "i2v",
        "--image", str(image),
        "--out", str(out_mp4),
        "--model", model,
        "--prompt", prompt,
    ]
    if negative_prompt:
        cmd += ["--negative-prompt", negative_prompt]
    if num_frames is not None:
        cmd += ["--num-frames", str(num_frames)]
    if fps is not None:
        cmd += ["--fps", str(fps)]
    if backend:
        cmd += ["--backend", backend]

    log("gen_video.py i2v: " + " ".join(
        (f'"{c}"' if " " in c else c) for c in cmd[2:]
    ))
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        raise RuntimeError(
            f"gen_video.py failed for {out_mp4.name} (exit {res.returncode})"
        )
    if not out_mp4.exists():
        raise RuntimeError(
            f"gen_video.py returned 0 but {out_mp4} was not written "
            "(possibly a cloud/grok backend was selected — see its stderr "
            "above and follow the printed delegation instructions)"
        )


# --------------------------------------------------------------------------- #
def load_scenes(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"[chain_video] cannot parse {path}: {exc}")
    if not isinstance(data, list):
        raise SystemExit(
            f"[chain_video] {path} must be a JSON array of scene objects "
            "(see --help for the shape)"
        )
    scenes = []
    for i, s in enumerate(data):
        if not isinstance(s, dict) or "prompt" not in s or not str(s["prompt"]).strip():
            raise SystemExit(
                f"[chain_video] scene index {i} is missing a non-empty 'prompt'"
            )
        scenes.append(s)
    return scenes


def main() -> int:
    p = argparse.ArgumentParser(
        prog="chain_video.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__ or ""),
    )
    p.add_argument("--scenes-dir", required=True,
                   help="output directory for the per-scene clips and the "
                        "extracted seam frames")
    p.add_argument("--prompts-file", required=True,
                   help="scenes.json: a JSON ARRAY of {prompt, "
                        "[negative_prompt], [model], [num_frames]} (see --help)")
    seed = p.add_mutually_exclusive_group()
    seed.add_argument("--first-clip",
                      help="path to an existing clip 0; its LAST frame seeds "
                           "scene 1 (the chain continues from this video)")
    seed.add_argument("--first-image",
                      help="path to a starting STILL image; it seeds scene 1 "
                           "directly (use this to start a chain from scratch)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"chain-wide i2v model passed to gen_video.py "
                        f"(default: {DEFAULT_MODEL}). Keep this STABLE across "
                        "the whole chain to limit style drift; a scene may "
                        "override it via scenes.json 'model'.")
    p.add_argument("--start", type=int, default=0,
                   help="first scene INDEX to (re)generate (default: 0). "
                        "Earlier scenes must already exist on disk so their "
                        "last frame can seed --start.")
    p.add_argument("--end", type=int, default=None,
                   help="last scene INDEX to generate, INCLUSIVE "
                        "(default: last scene in the file)")
    p.add_argument("--fps", type=int, default=None,
                   help="export fps passed to gen_video.py for every scene "
                        "(default: let the model decide)")
    p.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE,
                   help="FIXED negative prompt applied to EVERY scene that does "
                        "not override it in scenes.json. Pinning this across "
                        "5-10 chained clips is the main anti-drift lever; the "
                        "built-in default targets colour/style shift, blur, "
                        "flicker and warping. Pass '' to disable.")
    p.add_argument("--backend", default=None,
                   choices=["auto", "wan", "ltx", "grok"],
                   help="passed through to gen_video.py --backend for every "
                        "scene (default: gen_video.py's own default = auto)")
    p.add_argument("--concat", action="store_true",
                   help="after all scenes succeed, run edit_video.py concat to "
                        "join them into one mp4 (if edit_video.py is absent, "
                        "the command is printed instead)")
    args = p.parse_args()

    if not GEN_VIDEO_PY.exists():
        raise SystemExit(f"[chain_video] sibling not found: {GEN_VIDEO_PY}")
    if shutil.which(FFMPEG) is None and not Path(FFMPEG).exists():
        raise SystemExit(f"[chain_video] ffmpeg not found ({FFMPEG})")

    scenes = load_scenes(Path(args.prompts_file))
    n = len(scenes)
    if n == 0:
        raise SystemExit("[chain_video] scenes file is empty")

    start = args.start
    end = args.end if args.end is not None else n - 1
    if start < 0 or start >= n:
        raise SystemExit(f"[chain_video] --start {start} out of range 0..{n-1}")
    if end < start or end >= n:
        raise SystemExit(
            f"[chain_video] --end {end} out of range {start}..{n-1}")

    scenes_dir = Path(args.scenes_dir)
    scenes_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = scenes_dir / "_frames"

    env = clean_env()

    def scene_mp4(i: int) -> Path:
        return scenes_dir / f"scene_{i}.mp4"

    # Resolve the seed image for the FIRST scene we will actually generate.
    # For scene index k, the seed is the last frame of scene k-1 (or the
    # provided --first-clip / --first-image when k == 0).
    if args.first_clip:
        first_clip = Path(args.first_clip)
        if not first_clip.exists():
            raise SystemExit(f"[chain_video] --first-clip not found: {first_clip}")
    elif args.first_image:
        first_image = Path(args.first_image)
        if not first_image.exists():
            raise SystemExit(f"[chain_video] --first-image not found: {first_image}")
    else:
        # Allow omission only if scene 0 already exists and we're resuming >0.
        if start == 0:
            raise SystemExit(
                "[chain_video] you must pass --first-clip or --first-image "
                "to seed scene 0")

    log(f"chaining scenes {start}..{end} of {n} into {scenes_dir} "
        f"(model={args.model}, backend={args.backend or 'auto'})")
    log(f"anti-drift: fixed negative prompt {'ON' if args.negative_prompt else 'OFF'}; "
        f"lossless PNG seam frames; stable model across chain")

    generated = 0
    skipped = 0
    for i in range(start, end + 1):
        out_mp4 = scene_mp4(i)

        # RESUME-SAFE: skip scenes already on disk.
        if out_mp4.exists() and out_mp4.stat().st_size > 0:
            log(f"scene {i}: SKIP (exists: {out_mp4.name})")
            skipped += 1
            continue

        # Determine the seed image for this scene.
        if i == 0:
            if args.first_clip:
                seed_png = frames_dir / "seed_from_first_clip.png"
                extract_last_frame(Path(args.first_clip), seed_png, env)
                seed_image = seed_png
            else:  # first_image
                seed_image = Path(args.first_image)
        else:
            prev = scene_mp4(i - 1)
            if not prev.exists() or prev.stat().st_size == 0:
                raise SystemExit(
                    f"[chain_video] cannot generate scene {i}: previous clip "
                    f"{prev} is missing. Generate it first (or lower --start).")
            seed_png = frames_dir / f"last_of_scene_{i-1}.png"
            extract_last_frame(prev, seed_png, env)
            seed_image = seed_png

        scene = scenes[i]
        prompt = str(scene["prompt"]).strip()
        neg = scene.get("negative_prompt", args.negative_prompt)
        model = scene.get("model", args.model)
        num_frames = scene.get("num_frames", None)
        if num_frames is not None:
            num_frames = int(num_frames)

        log(f"scene {i}/{end}: GENERATE  seed={seed_image.name}  "
            f"model={model}  frames={num_frames if num_frames is not None else 'default'}")
        gen_scene(
            image=seed_image,
            out_mp4=out_mp4,
            prompt=prompt,
            negative_prompt=neg,
            model=model,
            num_frames=num_frames,
            fps=args.fps,
            backend=args.backend,
            env=env,
        )
        log(f"scene {i}: DONE -> {out_mp4}")
        generated += 1

    log(f"finished: {generated} generated, {skipped} skipped "
        f"(scenes {start}..{end})")

    # Concat / final-join.
    clips = [scene_mp4(i) for i in range(0, end + 1) if scene_mp4(i).exists()]
    concat_out = scenes_dir / "chained_full.mp4"
    concat_cmd = [
        UV, "run", str(EDIT_VIDEO_PY), "concat",
        "--out", str(concat_out),
        "--inputs", *[str(c) for c in clips],
    ]
    pretty = " ".join((f'"{c}"' if " " in c else c) for c in concat_cmd)

    if args.concat:
        if EDIT_VIDEO_PY.exists():
            log(f"concatenating {len(clips)} clips -> {concat_out}")
            res = subprocess.run(concat_cmd, env=env)
            if res.returncode != 0:
                log("edit_video.py concat failed; run it manually:")
                print(pretty)
                return 1
            log(f"final video: {concat_out}")
        else:
            log("edit_video.py not present yet; run this to concat once it is:")
            print(pretty)
    else:
        log("to join the clips into one continuous video, run:")
        print(pretty)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        log("interrupted")
        raise SystemExit(130)
