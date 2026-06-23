#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "fal-client>=0.5.0",
#   "requests",
# ]
# ///
"""
cloud_fal.py — fal.ai hosted-inference fallback for Wan / LTX / FLUX, used by the
`generate-edit-video` skill when probe_backend.py selects backend `cloud-fal`.

WHEN TO USE THIS (vs cloud_modal.py)
====================================
fal.ai is the FASTEST zero-infra path: a hosted endpoint already serves the model,
so there is no container image to build, no weight Volume to warm, and no pipeline
code to maintain — you just submit a request and download the URL. Billing is
per OUTPUT-second (you pay for successful output only).

PREFER THIS over scripts/cloud_modal.py whenever a hosted fal endpoint already
exists for the requested model (the `fal_id` field in scripts/models.py / the
built-in FAL_MAP below tells you whether one does). Reach for cloud_modal.py only
when you need a CUSTOM diffusers pipeline (specific revision, LoRA, your own
pre/post) or the cheapest raw GPU-seconds and you are willing to maintain code.
Backend ladder: local-single > local-offload > local-multi > cloud-modal >
**cloud-fal** > grok. (Grok is delegated to the grok-media skill, never here.)

--------------------------------------------------------------------------------
FAL_KEY SETUP (one time)
--------------------------------------------------------------------------------
  1. Sign up / log in at https://fal.ai  and add billing.
  2. Create a key at https://fal.ai/dashboard/keys  (format "<key-id>:<secret>").
  3. Export it before running this script:
         export FAL_KEY="xxxxxxxx-xxxx-...:yyyyyyyy..."
     (The fal_client package reads FAL_KEY from the environment automatically.)

--------------------------------------------------------------------------------
ROUGH COST (fal.ai, per OUTPUT-second — pay only for successful output)
--------------------------------------------------------------------------------
  fal-ai/wan/v2.2-a14b/{text,image}-to-video   ~$0.04 - 0.08 / output-second
  fal-ai/wan/v2.2-5b/text-to-video             ~$0.02 - 0.05 / output-second
  fal-ai/ltx-2.3/{text,image}-to-video         ~$0.04 - 0.10 / output-second
  fal-ai/ltx-2.3/{...}/fast                     cheaper, distilled
  fal-ai/flux/dev (image)                       ~$0.025 / megapixel
  A typical 5s 720p clip therefore lands around a few tens of cents. Check the
  live price on each model's page (https://fal.ai/models) before a big batch.

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
  export FAL_KEY="...:..."
  ./cloud_fal.py --model wan2.1-t2v-1.3b --task t2v \
      --prompt "a red fox running through snow, cinematic" --out out.mp4
  ./cloud_fal.py --model wan2.2-i2v-a14b --task i2v --image in.jpg \
      --prompt "she slowly turns to camera" --out out.mp4
  ./cloud_fal.py --model flux.1-dev --task t2i \
      --prompt "neon-lit street, cinematic portrait" --out out.png

Run with --help for the full option list. The local --model id is mapped to the
fal endpoint id via models.py's `fal_id` field (with a built-in fallback map).
PEP723 inline deps (fal-client) are resolved by uv.
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from pathlib import Path

# --------------------------------------------------------------------------- #
# Locations / sibling scripts
# --------------------------------------------------------------------------- #
SCRIPT_DIR = Path(__file__).resolve().parent
MODELS_PY = SCRIPT_DIR / "models.py"


def log(msg: str) -> None:
    print(f"[cloud_fal] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(msg, file=sys.stderr, flush=True)
    raise SystemExit(code)


# --------------------------------------------------------------------------- #
# Clean environment (strip the anaconda libtinfo LD_LIBRARY_PATH pollution).
# This script shells out / imports native deps, so scrub conda paths first —
# anaconda's libtinfo.so.6 has broken subprocesses before (see SKILL contracts).
# --------------------------------------------------------------------------- #
def clean_ld_environment() -> None:
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if not ld:
        return
    kept = [
        p
        for p in ld.split(os.pathsep)
        if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p
    ]
    new = os.pathsep.join(kept)
    if new:
        os.environ["LD_LIBRARY_PATH"] = new
    else:
        os.environ.pop("LD_LIBRARY_PATH", None)
    if new != ld:
        log(f"scrubbed conda paths from LD_LIBRARY_PATH (was {len(ld)} chars)")


# --------------------------------------------------------------------------- #
# Built-in fal endpoint map — fallback mirror of scripts/models.py `fal_id`.
# models.py / gen_video.py FALLBACK_MODELS are the source of truth when present;
# this keeps cloud_fal.py runnable standalone. Keys are the local --model ids.
# For i2v we point at the image-to-video variant of the same family.
# --------------------------------------------------------------------------- #
FAL_MAP: dict[str, str] = {
    # --- Wan (Alibaba) ---
    "wan2.1-t2v-1.3b": "fal-ai/wan/v2.2-5b/text-to-video",
    "wan2.2-ti2v-5b": "fal-ai/wan/v2.2-5b/text-to-video",
    "wan2.2-t2v-a14b": "fal-ai/wan/v2.2-a14b/text-to-video",
    "wan2.2-i2v-a14b": "fal-ai/wan/v2.2-a14b/image-to-video",
    # --- LTX ---
    "ltx-video-0.9.8": "fal-ai/ltx-2.3/text-to-video",
    "ltx-video-0.9.8-i2v": "fal-ai/ltx-2.3/image-to-video",
    "ltx-2.3": "fal-ai/ltx-2.3/text-to-video",
    # --- Image (FLUX) ---
    "flux.1-dev": "fal-ai/flux/dev",
    "flux.1-schnell": "fal-ai/flux/schnell",
    "flux.2-dev": "fal-ai/flux-2/dev",
}

DEFAULT_MODEL_FOR_TASK = {
    "t2v": "wan2.1-t2v-1.3b",
    "i2v": "wan2.2-i2v-a14b",
    "t2i": "flux.1-dev",
}


def resolve_fal_id(model_id: str, task: str) -> str:
    """Map a local --model id to a fal endpoint id.

    Prefer the authoritative scripts/models.py `fal_id`; fall back to FAL_MAP.
    For i2v, if the resolved id looks like a text-to-video endpoint, swap it to
    the image-to-video variant of the same family when possible.
    """
    fal_id: str | None = None

    if MODELS_PY.exists():
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            import importlib

            models = importlib.import_module("models")
            spec = models.get(model_id) if hasattr(models, "get") else None
            if spec:
                fal_id = spec.get("fal_id")
        except Exception as e:  # never let a bad models.py block the cloud path
            log(f"could not read models.py ({e}); using built-in FAL_MAP")

    if not fal_id:
        fal_id = FAL_MAP.get(model_id)

    if not fal_id:
        die(
            textwrap.dedent(
                f"""\
                ERROR: no fal endpoint known for model {model_id!r}.

                Known models with a hosted fal endpoint:
                  {', '.join(sorted(FAL_MAP))}

                Either pick one of those, add a `fal_id` for {model_id!r} in
                scripts/models.py, or pass the endpoint directly with
                --fal-id fal-ai/<owner>/<model>/<route>.
                See available endpoints at https://fal.ai/models"""
            )
        )

    # i2v requested but resolved id is a t2v route -> swap to i2v variant.
    if task == "i2v" and fal_id.endswith("text-to-video"):
        i2v = fal_id[: -len("text-to-video")] + "image-to-video"
        log(f"task=i2v: using image-to-video variant {i2v}")
        fal_id = i2v

    return fal_id


# --------------------------------------------------------------------------- #
# Request payload assembly
# --------------------------------------------------------------------------- #
def build_arguments(args, fal_client) -> dict:
    """Assemble the fal request payload from CLI args.

    fal endpoints accept slightly different keys, but the common ones below are
    widely supported (extra/unknown keys are generally ignored server-side). We
    only send a value when the user explicitly supplied it, letting the hosted
    endpoint apply its own (well-tuned) defaults otherwise.
    """
    payload: dict = {"prompt": args.prompt}

    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.num_frames is not None:
        payload["num_frames"] = args.num_frames
    if args.fps is not None:
        payload["frames_per_second"] = args.fps
        payload["fps"] = args.fps
    if args.steps is not None:
        payload["num_inference_steps"] = args.steps
    if args.guidance is not None:
        payload["guidance_scale"] = args.guidance

    # Size: accept either --size WxH or --width/--height.
    width, height = args.width, args.height
    if args.size:
        try:
            w_str, h_str = args.size.lower().split("x")
            width, height = int(w_str), int(h_str)
        except ValueError:
            die(f"ERROR: --size must be WxH (e.g. 1280x720), got {args.size!r}")
    if width and height:
        # Most fal video models take image_size {width,height}; FLUX too.
        payload["image_size"] = {"width": width, "height": height}

    # i2v: upload the local image and pass its URL.
    if args.task == "i2v":
        if not args.image:
            die("ERROR: --task i2v requires --image <path to a still image>")
        img_path = Path(args.image)
        if not img_path.exists():
            die(f"ERROR: --image not found: {img_path}")
        log(f"uploading input image {img_path} ...")
        image_url = fal_client.upload_file(str(img_path))
        payload["image_url"] = image_url

    return payload


# --------------------------------------------------------------------------- #
# Result -> output URL extraction
# --------------------------------------------------------------------------- #
def extract_output_url(result: dict, task: str) -> str:
    """Pull the output media URL out of a fal result dict.

    fal results vary by endpoint but converge on a few shapes:
      {"video": {"url": ...}}            (video endpoints)
      {"images": [{"url": ...}, ...]}    (image endpoints)
      {"image": {"url": ...}}
    We probe the likely keys in order and fall back to a deep search.
    """
    if not isinstance(result, dict):
        die(f"ERROR: unexpected fal result type {type(result).__name__}: {result!r}")

    # Direct single-media keys.
    for key in ("video", "image", "audio", "file"):
        node = result.get(key)
        if isinstance(node, dict) and node.get("url"):
            return node["url"]
        if isinstance(node, str) and node.startswith("http"):
            return node

    # List-of-media keys.
    for key in ("videos", "images", "files"):
        node = result.get(key)
        if isinstance(node, list) and node:
            first = node[0]
            if isinstance(first, dict) and first.get("url"):
                return first["url"]
            if isinstance(first, str) and first.startswith("http"):
                return first

    # Deep fallback: first "url" anywhere in the structure.
    def _find_url(obj):
        if isinstance(obj, dict):
            if isinstance(obj.get("url"), str) and obj["url"].startswith("http"):
                return obj["url"]
            for v in obj.values():
                u = _find_url(v)
                if u:
                    return u
        elif isinstance(obj, list):
            for v in obj:
                u = _find_url(v)
                if u:
                    return u
        return None

    url = _find_url(result)
    if url:
        return url

    die(
        "ERROR: could not find an output URL in the fal result. Raw result:\n"
        + repr(result)
    )


def download(url: str, out: Path) -> None:
    import requests

    log(f"downloading output -> {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
    size = out.stat().st_size
    print(f"saved {out.resolve()} ({size:,} bytes)")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cloud_fal.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            fal.ai hosted-inference fallback for Wan / LTX / FLUX.

            Submits a generation to a hosted fal endpoint and downloads the
            result. CLI mirrors gen_video.py. Reads FAL_KEY from the env.
            Preferred over cloud_modal.py when a hosted endpoint already exists
            (fastest zero-infra path; billed per output-second)."""
        ),
        epilog=textwrap.dedent(
            """\
            examples:
              export FAL_KEY="...:..."
              cloud_fal.py --model wan2.1-t2v-1.3b --task t2v \\
                  --prompt "a red fox in snow" --out out.mp4
              cloud_fal.py --model wan2.2-i2v-a14b --task i2v --image in.jpg \\
                  --prompt "she turns to camera" --out out.mp4
              cloud_fal.py --model flux.1-dev --task t2i \\
                  --prompt "neon street portrait" --out out.png
            """
        ),
    )
    p.add_argument(
        "--model",
        default=None,
        help="local model id (mapped to a fal endpoint via models.py fal_id). "
        f"known: {', '.join(sorted(FAL_MAP))}. "
        "default: per-task (t2v=wan2.1-t2v-1.3b, i2v=wan2.2-i2v-a14b, "
        "t2i=flux.1-dev)",
    )
    p.add_argument(
        "--task",
        choices=["t2v", "i2v", "t2i"],
        default="t2v",
        help="generation task (default: t2v)",
    )
    p.add_argument("--prompt", default="", help="text prompt")
    p.add_argument(
        "--image", help="input still image path (required & uploaded for i2v)"
    )
    p.add_argument(
        "--out", default=None, help="output path (default: out.mp4 / out.png by task)"
    )
    p.add_argument(
        "--fal-id",
        default=None,
        help="override the fal endpoint id directly "
        "(e.g. fal-ai/wan/v2.2-a14b/text-to-video); skips model->endpoint mapping",
    )
    p.add_argument("--num-frames", type=int, help="number of frames (video)")
    p.add_argument("--fps", type=int, help="frames per second (video)")
    p.add_argument(
        "--size", help="output size as WxH, e.g. 1280x720 (overrides --width/--height)"
    )
    p.add_argument("--width", type=int, help="output width")
    p.add_argument("--height", type=int, help="output height")
    p.add_argument("--steps", type=int, help="inference steps (endpoint default if unset)")
    p.add_argument("--guidance", type=float, help="guidance scale (endpoint default if unset)")
    p.add_argument("--negative-prompt", help="negative prompt")
    p.add_argument("--seed", type=int, help="random seed")
    return p


def require_fal_client():
    """Import fal_client or print clear setup instructions and exit nonzero."""
    try:
        import fal_client  # noqa: F401

        return fal_client
    except Exception:
        die(
            textwrap.dedent(
                """\
                ERROR: the `fal-client` python package is not available.

                This script declares it as a PEP723 inline dependency, so the
                intended way to run it is via uv (which installs deps on the fly):

                    "$UV" run scripts/cloud_fal.py --help
                    # or:  uv run scripts/cloud_fal.py --help

                If you are NOT using uv, install it manually first:

                    uv pip install fal-client      # inside a venv
                    # or:  pip install fal-client

                Then re-run this script."""
            )
        )


def require_fal_key() -> None:
    """Confirm FAL_KEY is set or print clear setup instructions and exit nonzero."""
    if os.environ.get("FAL_KEY"):
        return
    die(
        textwrap.dedent(
            """\
            ERROR: FAL_KEY is not set in the environment.

            Get a key:
              1. Sign up / log in at https://fal.ai and add billing.
              2. Create a key at https://fal.ai/dashboard/keys
                 (format "<key-id>:<secret>").
              3. Export it, then re-run:
                     export FAL_KEY="xxxxxxxx-...:yyyyyyyy..."

            fal billing is per OUTPUT-second; you pay only for successful output."""
        )
    )


def main(argv: list[str] | None = None) -> int:
    clean_ld_environment()
    args = build_parser().parse_args(argv)

    # Resolve task-aware defaults for --model / --out.
    if not args.model:
        args.model = DEFAULT_MODEL_FOR_TASK[args.task]
    if not args.out:
        args.out = "out.png" if args.task == "t2i" else "out.mp4"
    if not args.prompt and args.task != "i2v":
        die("ERROR: --prompt is required (except sometimes for i2v).")

    # Defensive gates: package + key BEFORE doing any work.
    fal_client = require_fal_client()
    require_fal_key()

    # Endpoint resolution: explicit --fal-id wins; else map via models.py/FAL_MAP.
    fal_id = args.fal_id or resolve_fal_id(args.model, args.task)
    log(f"model={args.model} task={args.task} -> fal endpoint {fal_id}")

    payload = build_arguments(args, fal_client)
    log(f"submitting request to {fal_id} ...")

    def _on_queue_update(update):
        # Stream queue/progress logs to stderr so long renders show life.
        try:
            from fal_client import InProgress

            if isinstance(update, InProgress):
                for entry in getattr(update, "logs", None) or []:
                    msg = entry.get("message") if isinstance(entry, dict) else entry
                    if msg:
                        log(f"  {msg}")
        except Exception:
            pass

    try:
        # subscribe() submits, polls to completion, and returns the result dict.
        result = fal_client.subscribe(
            fal_id,
            arguments=payload,
            with_logs=True,
            on_queue_update=_on_queue_update,
        )
    except Exception as e:
        die(
            f"ERROR: fal request failed for {fal_id}: {e}\n"
            "Check that FAL_KEY is valid, the endpoint id exists "
            "(https://fal.ai/models), and your account has billing enabled."
        )

    url = extract_output_url(result, args.task)
    download(url, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
