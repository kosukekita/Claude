#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
# ]
# ///
"""
cloud_openrouter.py — OpenRouter API backend for the `video-media-studio` skill.

WHEN TO USE THIS
================
OpenRouter is an EXPLICIT, user-named backend — NOT part of the local-first auto
ladder. The user has to ask for it ("OpenRouterで"); the skill then routes here
via `--backend openrouter` (gen_image.py / gen_video.py) or you call this script
directly. It is the same kind of "use it only when named" seam as grok-media —
it is intentionally NOT consulted by probe_backend.py's auto cloud resolution, so
auto behaviour (local-single > offload > local-multi > cloud-modal > cloud-fal >
grok) is unchanged.

It does THREE things over ONE billing/routing layer:
  llm     chat/completion against any OpenRouter-hosted text model
  image   text-to-image via chat/completions + modalities ["image","text"]
  video   text/image-to-video via the dedicated async /api/v1/videos endpoint

--------------------------------------------------------------------------------
API KEY SETUP (one time)  —  stored in a dedicated file, NOT an env you must export
--------------------------------------------------------------------------------
  1. Create a key at https://openrouter.ai/keys  (format "sk-or-v1-...").
  2. Save it to ~/.config/openrouter.key (one line, no trailing newline):
         umask 077 && printf '%s' 'sk-or-v1-...' > ~/.config/openrouter.key
         chmod 600 ~/.config/openrouter.key
  3. (Alternative) export OPENROUTER_API_KEY=sk-or-v1-... in the environment.

  Key resolution order (first hit wins):
     ~/.config/openrouter.key   ->   $OPENROUTER_API_KEY
  ~/.config/ is OUTSIDE the public ~/.claude git repo, mirroring ~/.config/
  gmail-smtp.pass, so the key never lands in a commit.

--------------------------------------------------------------------------------
ENDPOINTS (base https://openrouter.ai/api/v1)
--------------------------------------------------------------------------------
  llm/image : POST /chat/completions        (OpenAI-compatible; image via
              modalities:["image","text"], result data-URL at
              choices[0].message.images[0].image_url.url)
  video     : POST /videos                  -> {id, polling_url, status}
              GET  /videos/{id}             -> poll until status==completed
              GET  /videos/{id}/content?index=0  -> download the mp4
              (result urls also exposed as unsigned_urls[0])

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
  # LLM (prints the text reply to stdout)
  ./cloud_openrouter.py llm --model anthropic/claude-opus-4-8 \
      --prompt "Summarise this in one sentence: ..."

  # text-to-image
  ./cloud_openrouter.py image --model google/gemini-2.5-flash-image-preview \
      --prompt "neon-lit street, cinematic portrait" --out city.png

  # text-to-video
  ./cloud_openrouter.py video --model google/veo-3.1 --task t2v \
      --prompt "a red fox running through snow, cinematic" --out fox.mp4

  # image-to-video (first frame)
  ./cloud_openrouter.py video --model alibaba/wan-2.7 --task i2v \
      --image still.jpg --prompt "she slowly turns to camera" --out anim.mp4

Run `--help` (or `<subcommand> --help`) for the full option list. Discover live
model ids with:  ./cloud_openrouter.py models [--modality image|video]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import textwrap
import time
from pathlib import Path

import requests

API_BASE = "https://openrouter.ai/api/v1"
KEY_FILE = Path.home() / ".config" / "openrouter.key"

# Network defaults. Video renders are async and can take minutes; the poll loop
# is bounded by both a wall-clock deadline AND a max attempt count (see below).
HTTP_TIMEOUT = 120          # per-request seconds
POLL_INTERVAL = 5           # seconds between status polls
POLL_MAX_SECONDS = 900      # hard wall-clock deadline for a video job (15 min)
POLL_MAX_ATTEMPTS = 240     # hard attempt cap (belt-and-braces with the deadline)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    log(msg)
    raise SystemExit(1)


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
def resolve_api_key() -> str:
    """File first (~/.config/openrouter.key), then env. Clear setup help on miss."""
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
        log(f"WARNING: {KEY_FILE} exists but is empty; trying $OPENROUTER_API_KEY")
    env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env:
        return env
    die(
        textwrap.dedent(
            f"""\
            ERROR: no OpenRouter API key found.

            Looked in (in order):
              1. {KEY_FILE}
              2. $OPENROUTER_API_KEY

            Get a key at https://openrouter.ai/keys (format "sk-or-v1-..."),
            then save it to the dedicated file:

                umask 077 && printf '%s' 'sk-or-v1-...' > {KEY_FILE}
                chmod 600 {KEY_FILE}

            (or: export OPENROUTER_API_KEY=sk-or-v1-...)"""
        )
    )


def auth_headers(key: str) -> dict:
    # Referer/X-Title are optional OpenRouter attribution headers; harmless to send.
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/anthropics/claude-code",
        "X-Title": "video-media-studio",
    }


# --------------------------------------------------------------------------- #
# LLM
# --------------------------------------------------------------------------- #
def cmd_llm(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    body: dict = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
    }
    if args.system:
        body["messages"].insert(0, {"role": "system", "content": args.system})
    if args.temperature is not None:
        body["temperature"] = args.temperature
    if args.max_tokens is not None:
        body["max_tokens"] = args.max_tokens

    log(f"llm -> {args.model}")
    resp = requests.post(
        f"{API_BASE}/chat/completions",
        headers=auth_headers(key),
        json=body,
        timeout=HTTP_TIMEOUT,
    )
    _raise_for_openrouter(resp)
    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        die(f"ERROR: unexpected LLM response shape ({exc}): {json.dumps(data)[:500]}")
    print(text)
    return 0


# --------------------------------------------------------------------------- #
# Image (chat/completions + modalities)
# --------------------------------------------------------------------------- #
def _decode_image_data_url(url: str, out: Path) -> None:
    """Image is returned as a base64 data URL: data:image/png;base64,<...>."""
    m = re.match(r"^data:(?P<mime>[^;]+);base64,(?P<b64>.+)$", url, re.DOTALL)
    if not m:
        # Some providers may hand back a plain https URL instead of a data URL.
        if url.startswith("http"):
            _download(url, out)
            return
        die(f"ERROR: image url is neither a data URL nor http(s): {url[:80]}...")
    raw = base64.b64decode(m.group("b64"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)


def cmd_image(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    content: list = [{"type": "text", "text": args.prompt}]
    # Optional input images for image-edit style prompts (data URL or http).
    for img in args.image or []:
        content.append(
            {"type": "image_url", "image_url": {"url": _to_image_url(img)}}
        )
    log(f"image -> {args.model}")
    # Two model families on OpenRouter:
    #   out=[image,text]  (gemini-*, gpt-5*-image, openrouter/auto) -> need both modalities
    #   out=[image] only  (flux.2-*, gpt-image-*, recraft, riverflow, seedream, mai,
    #                       grok-imagine) -> reject ["image","text"] with a 404
    #                       "No endpoints found that support ... image, text"
    # Try the richer set first, then fall back to image-only on that exact 404.
    def _post(modalities: list[str]) -> requests.Response:
        return requests.post(
            f"{API_BASE}/chat/completions",
            headers=auth_headers(key),
            json={
                "model": args.model,
                "modalities": modalities,
                "messages": [{"role": "user", "content": content}],
            },
            timeout=HTTP_TIMEOUT,
        )

    # Pick the modality set once (image-only models 404 on ["image","text"]).
    modalities = ["image", "text"]
    probe = _post(modalities)
    if probe.status_code == 404 and "output modalities" in probe.text:
        log("  image-only model: using modalities=['image']")
        modalities = ["image"]
        probe = _post(modalities)
    # Transient provider hiccups (500 / "Provider returned error" 400) are common on
    # the image-only family — retry a few times with backoff before giving up.
    resp = probe
    for attempt in range(1, 5):
        transient = resp.status_code in (429, 500, 502, 503) or (
            resp.status_code == 400 and "Provider returned error" in resp.text
        )
        if not transient:
            break
        wait = 4 * attempt
        log(f"  transient HTTP {resp.status_code}; retry {attempt}/4 after {wait}s")
        time.sleep(wait)
        resp = _post(modalities)
    _raise_for_openrouter(resp)
    data = resp.json()
    try:
        images = data["choices"][0]["message"]["images"]
        url = images[0]["image_url"]["url"]
    except (KeyError, IndexError, TypeError) as exc:
        die(
            f"ERROR: no image in response ({exc}). Is '{args.model}' an "
            f"image-output model? Response head: {json.dumps(data)[:500]}"
        )
    out = Path(args.out).expanduser()
    _decode_image_data_url(url, out)
    log(f"saved -> {out.resolve()}")
    print(str(out.resolve()))
    return 0


# --------------------------------------------------------------------------- #
# Video (async /videos)
# --------------------------------------------------------------------------- #
def cmd_video(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    if args.task == "i2v" and not args.image:
        die("ERROR: --task i2v requires --image")

    body: dict = {"model": args.model, "prompt": args.prompt}
    if args.resolution:
        body["resolution"] = args.resolution
    if args.aspect_ratio:
        body["aspect_ratio"] = args.aspect_ratio
    if args.duration is not None:
        body["duration"] = args.duration
    if args.seed is not None:
        body["seed"] = args.seed
    if args.audio:
        body["generate_audio"] = True
    if args.task == "i2v":
        # first-frame image-to-video. OpenRouter's /videos Zod schema requires:
        #   type="image_url" (the part kind), frame_type="first_frame"|"last_frame",
        #   image_url={"url": ...}  (same nesting as chat vision parts).
        body["frame_images"] = [{
            "type": "image_url",
            "frame_type": "first_frame",
            "image_url": {"url": _to_image_url(args.image)},
        }]
    for ref in args.reference or []:
        body.setdefault("input_references", []).append(
            {"type": "image_url", "image_url": {"url": _to_image_url(ref)}}
        )

    log(f"video -> {args.model} ({args.task}); submitting job ...")
    resp = requests.post(
        f"{API_BASE}/videos",
        headers=auth_headers(key),
        json=body,
        timeout=HTTP_TIMEOUT,
    )
    _raise_for_openrouter(resp)
    job = resp.json()
    job_id = job.get("id")
    if not job_id:
        die(f"ERROR: no job id in submit response: {json.dumps(job)[:500]}")
    # NOTE: job["polling_url"] is a browser/cookie-auth URL ("No cookie auth
    # credentials found" on a Bearer GET). Always poll the API endpoint with the
    # same Bearer auth as submit.
    poll_url = f"{API_BASE}/videos/{job_id}"
    log(f"job id={job_id}; polling {poll_url}")

    status = _poll_video(key, poll_url, job)
    out = Path(args.out).expanduser()
    _retrieve_video(key, job_id, status, out)
    log(f"saved -> {out.resolve()}")
    print(str(out.resolve()))
    return 0


def _poll_video(key: str, poll_url: str, first: dict) -> dict:
    """Poll until completed/failed. Bounded by BOTH a wall-clock deadline and a
    max attempt count so a stuck job can never spin forever."""
    deadline = POLL_MAX_SECONDS
    waited = 0
    attempts = 0
    status = first
    while True:
        state = (status.get("status") or "").lower()
        if state == "completed":
            return status
        if state in {"failed", "cancelled", "expired"}:
            die(f"ERROR: video job {state}: {json.dumps(status)[:500]}")
        attempts += 1
        if attempts > POLL_MAX_ATTEMPTS:
            die(f"ERROR: video job still '{state}' after {attempts} polls; giving up")
        if waited >= deadline:
            die(f"ERROR: video job still '{state}' after {waited}s deadline; giving up")
        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL
        log(f"  status={state or 'pending'} ({waited}s elapsed)")
        r = requests.get(poll_url, headers=auth_headers(key), timeout=HTTP_TIMEOUT)
        _raise_for_openrouter(r)
        status = r.json()


def _retrieve_video(key: str, job_id: str, status: dict, out: Path) -> None:
    urls = status.get("unsigned_urls") or status.get("urls") or []
    if urls:
        _download(urls[0], out)
        return
    # Fall back to the content endpoint when the status payload has no direct url.
    content_url = f"{API_BASE}/videos/{job_id}/content?index=0"
    _download(content_url, out, key=key)


# --------------------------------------------------------------------------- #
# Models discovery
# --------------------------------------------------------------------------- #
def cmd_models(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    if args.modality == "video":
        url = f"{API_BASE}/videos/models"
    else:
        url = f"{API_BASE}/models"
        if args.modality:
            url += f"?output_modalities={args.modality}"
    resp = requests.get(url, headers=auth_headers(key), timeout=HTTP_TIMEOUT)
    _raise_for_openrouter(resp)
    data = resp.json()
    items = data.get("data", data) if isinstance(data, dict) else data
    for m in items if isinstance(items, list) else []:
        mid = m.get("id") if isinstance(m, dict) else m
        if mid:
            print(mid)
    return 0


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _raise_for_openrouter(resp: requests.Response) -> None:
    if resp.status_code < 400:
        return
    body = resp.text[:600]
    hint = ""
    if resp.status_code in (401, 403):
        hint = " (check your key in ~/.config/openrouter.key / $OPENROUTER_API_KEY)"
    elif resp.status_code == 402:
        hint = " (insufficient credits — add billing at https://openrouter.ai)"
    elif resp.status_code == 404:
        hint = " (model id not found — try `cloud_openrouter.py models`)"
    die(f"ERROR: OpenRouter HTTP {resp.status_code}{hint}: {body}")


def _to_image_url(path_or_url: str) -> str:
    """Pass through http(s)/data URLs; encode a local file as a base64 data URL."""
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    p = Path(path_or_url).expanduser()
    if not p.exists():
        die(f"ERROR: input image not found: {p}")
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _download(url: str, out: Path, key: str | None = None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    headers = auth_headers(key) if key else {}
    with requests.get(url, headers=headers, stream=True, timeout=HTTP_TIMEOUT) as r:
        _raise_for_openrouter(r)
        with out.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 16):
                if chunk:
                    fh.write(chunk)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cloud_openrouter.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="OpenRouter backend (LLM / image / video) for video-media-studio. "
                    "EXPLICIT backend only — not part of the local-first auto ladder.",
        epilog=textwrap.dedent(
            """\
            key: ~/.config/openrouter.key  (else $OPENROUTER_API_KEY)
            examples:
              %(prog)s llm   --model anthropic/claude-opus-4-8 --prompt "..."
              %(prog)s image --model google/gemini-2.5-flash-image-preview --prompt "..." --out a.png
              %(prog)s video --model google/veo-3.1 --task t2v --prompt "..." --out a.mp4
              %(prog)s models --modality video
            """
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("llm", help="text chat/completion")
    pl.add_argument("--model", required=True, help="e.g. anthropic/claude-opus-4-8")
    pl.add_argument("--prompt", required=True)
    pl.add_argument("--system", default=None, help="optional system prompt")
    pl.add_argument("--temperature", type=float, default=None)
    pl.add_argument("--max-tokens", type=int, default=None, dest="max_tokens")
    pl.set_defaults(func=cmd_llm)

    pi = sub.add_parser("image", help="text-to-image (chat/completions+modalities)")
    pi.add_argument("--model", required=True,
                    help="image-output model, e.g. google/gemini-2.5-flash-image-preview "
                         "or black-forest-labs/flux.2-pro")
    pi.add_argument("--prompt", required=True)
    pi.add_argument("--image", action="append", default=None,
                    help="input image for edit-style prompts (path/url); repeatable")
    pi.add_argument("--out", default="image.png", help="output image path")
    pi.set_defaults(func=cmd_image)

    pv = sub.add_parser("video", help="text/image-to-video (async /videos)")
    pv.add_argument("--model", required=True, help="e.g. google/veo-3.1, alibaba/wan-2.7")
    pv.add_argument("--task", choices=["t2v", "i2v"], default="t2v")
    pv.add_argument("--prompt", default="")
    pv.add_argument("--image", default=None, help="first-frame image for i2v (path/url)")
    pv.add_argument("--reference", action="append", default=None,
                    help="style reference image (path/url); repeatable")
    pv.add_argument("--out", default="out.mp4", help="output mp4 path")
    pv.add_argument("--resolution", default=None,
                    help="480p|720p|1080p|2K|4K (model-dependent)")
    pv.add_argument("--aspect-ratio", default=None, dest="aspect_ratio",
                    help="16:9|9:16|1:1|4:3|3:2")
    pv.add_argument("--duration", type=int, default=None, help="seconds")
    pv.add_argument("--seed", type=int, default=None)
    pv.add_argument("--audio", action="store_true", help="request audio generation")
    pv.set_defaults(func=cmd_video)

    pm = sub.add_parser("models", help="list available model ids")
    pm.add_argument("--modality", choices=["text", "image", "video"], default=None,
                    help="filter by output modality")
    pm.set_defaults(func=cmd_models)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
