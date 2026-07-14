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

FALLBACK ON HTTP 402 (out of credits)
=====================================
When OpenRouter answers a generate request with HTTP 402 (its "insufficient
credits" signal), all three routes retry the SAME request against AtlasCloud —
a second cloud vendor with independent billing — by DELEGATING to the sibling
cloud_atlascloud.py (its image/video APIs are shaped completely differently, so
this is not a base-URL swap). Model ids do NOT map 1:1 across the two vendors; a
small explicit table handles the known renames and an unmapped image/video model
is a hard stop (never a silent substitution) unless you name the AtlasCloud model
with --or-model. Disable the whole behaviour with --no-fallback. Which provider
actually served the request is always announced on stderr.

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


def _get_headers(key: str) -> dict:
    """Headers for bodyless GETs (video polling / download). Crucially OMITS
    Content-Type: application/json — sending it on an empty-body GET makes
    OpenRouter's gateway fall through to cookie auth and return 401."""
    return {
        "Authorization": f"Bearer {key}",
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

    log(f"[OpenRouter] llm -> {args.model}")
    resp = requests.post(
        f"{API_BASE}/chat/completions",
        headers=auth_headers(key),
        json=body,
        timeout=HTTP_TIMEOUT,
    )
    if resp.status_code == 402 and not args.no_fallback:
        return _fallback_llm(args)
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


def _image_via_images_endpoint(args: argparse.Namespace, key: str) -> int:
    """Dedicated POST /images route — the ONLY way to control output dimensions
    (aspect_ratio / resolution / size). chat/completions ignores textual aspect
    requests entirely (verified 2026-07-14: seedream-4.5 returns 2048x2048 square
    no matter what the prompt or reference canvas says). Reference images go in
    input_references; the result comes back as data[0].b64_json."""
    body: dict = {"model": args.model, "prompt": args.prompt}
    if args.aspect_ratio:
        body["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        body["resolution"] = args.resolution
    for img in args.image or []:
        body.setdefault("input_references", []).append(
            {"type": "image_url", "image_url": {"url": _to_image_url(img)}}
        )
    log(f"[OpenRouter] image (/images) -> {args.model} "
        f"(aspect_ratio={args.aspect_ratio or '-'} resolution={args.resolution or '-'})")

    def _post() -> requests.Response:
        return requests.post(
            f"{API_BASE}/images",
            headers=auth_headers(key),
            json=body,
            timeout=HTTP_TIMEOUT,
        )

    resp = _post()
    for attempt in range(1, 5):
        transient = resp.status_code in (429, 500, 502, 503) or (
            resp.status_code == 400 and "Provider returned error" in resp.text
        )
        if not transient:
            break
        wait = 4 * attempt
        log(f"  transient HTTP {resp.status_code}; retry {attempt}/4 after {wait}s")
        time.sleep(wait)
        resp = _post()
    if resp.status_code == 402 and not args.no_fallback:
        return _fallback_image(args)
    _raise_for_openrouter(resp)
    data = resp.json()
    try:
        item = data["data"][0]
    except (KeyError, IndexError, TypeError) as exc:
        die(f"ERROR: unexpected /images response shape ({exc}): {json.dumps(data)[:500]}")
    out = Path(args.out).expanduser()
    b64 = item.get("b64_json")
    if b64:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.b64decode(b64))
    elif item.get("url"):
        _download(item["url"], out, key=key)
    else:
        die(f"ERROR: /images item has neither b64_json nor url: {json.dumps(item)[:300]}")
    log(f"saved -> {out.resolve()}")
    print(str(out.resolve()))
    return 0


def cmd_image(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    # Dimension control requested -> must use the dedicated /images endpoint
    # (chat/completions has no size/aspect params and ignores prompt-level ones).
    if getattr(args, "aspect_ratio", None) or getattr(args, "resolution", None):
        return _image_via_images_endpoint(args, key)
    content: list = [{"type": "text", "text": args.prompt}]
    # Optional input images for image-edit style prompts (data URL or http).
    for img in args.image or []:
        content.append(
            {"type": "image_url", "image_url": {"url": _to_image_url(img)}}
        )
    log(f"[OpenRouter] image -> {args.model}")
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
    if resp.status_code == 402 and not args.no_fallback:
        return _fallback_image(args)
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

    log(f"[OpenRouter] video -> {args.model} ({args.task}); submitting job ...")
    resp = requests.post(
        f"{API_BASE}/videos",
        headers=auth_headers(key),
        json=body,
        timeout=HTTP_TIMEOUT,
    )
    if resp.status_code == 402 and not args.no_fallback:
        return _fallback_video(args)
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
        # GET must NOT carry Content-Type: application/json — with an empty body
        # OpenRouter's gateway then ignores the Bearer and demands cookie auth
        # ("No cookie auth credentials found", 401). Send Authorization only.
        r = requests.get(poll_url, headers=_get_headers(key), timeout=HTTP_TIMEOUT)
        _raise_for_openrouter(r)
        status = r.json()


def _retrieve_video(key: str, job_id: str, status: dict, out: Path) -> None:
    urls = status.get("unsigned_urls") or status.get("urls") or []
    if urls:
        # Despite the name, unsigned_urls point at .../videos/{id}/content?index=0
        # under api/v1 — they STILL require the Bearer (without key -> 401
        # "No cookie auth credentials found"). Always pass the key.
        _download(urls[0], out, key=key)
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
    # Bodyless GET: omit Content-Type (see _get_headers) so Bearer is honored.
    headers = _get_headers(key) if key else {}
    with requests.get(url, headers=headers, stream=True, timeout=HTTP_TIMEOUT) as r:
        _raise_for_openrouter(r)
        with out.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 16):
                if chunk:
                    fh.write(chunk)


# --------------------------------------------------------------------------- #
# AtlasCloud fallback (fires only on OpenRouter HTTP 402 = out of credits)
# --------------------------------------------------------------------------- #
# Ids do NOT map 1:1 across vendors. TEXT follows a general rule (same id;
# OpenRouter's "x-ai/" is AtlasCloud's "xai/"), so text ids fall through
# _atlas_llm_model(). IMAGE/VIDEO ids are structurally different (the task lives
# in the id suffix), so an unmapped one is a hard stop rather than a guess.
_ATLAS_TEXT_MODEL_MAP = {
    "x-ai/grok-4.3": "xai/grok-4.3",
}
_ATLAS_IMAGE_MODEL_MAP = {
    "google/gemini-2.5-flash-image-preview": "google/nano-banana-2/text-to-image",
}
_ATLAS_VIDEO_MODEL_MAP = {
    ("t2v", "alibaba/wan-2.7"): "alibaba/wan-2.7/text-to-video",
    ("i2v", "alibaba/wan-2.7"): "alibaba/wan-2.7/image-to-video",
}


def _load_atlas_module():
    """Load the sibling cloud_atlascloud.py by path. It is a PEP723 script, not an
    installed package, so a plain import would not find it."""
    import importlib.util

    path = Path(__file__).resolve().with_name("cloud_atlascloud.py")
    if not path.exists():
        die(f"OpenRouter 402（残高切れ）。フォールバック先 {path} が見つかりません。")
    spec = importlib.util.spec_from_file_location("cloud_atlascloud", path)
    if spec is None or spec.loader is None:
        die(f"OpenRouter 402（残高切れ）。{path} をロードできませんでした。")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _atlas_key_present(atlas) -> bool:
    """Presence check only — the key value is never returned or logged here."""
    try:
        if atlas.KEY_FILE.exists() and atlas.KEY_FILE.read_text(encoding="utf-8").strip():
            return True
    except OSError:
        pass
    return bool(os.environ.get("ATLASCLOUD_API_KEY", "").strip())


def _load_atlas_or_die():
    """Load AtlasCloud and confirm a key exists, or die with fallback-specific
    guidance. Callers log the concrete [AtlasCloud] line once the model resolves."""
    atlas = _load_atlas_module()
    if not _atlas_key_present(atlas):
        die(
            "OpenRouter 402（残高切れ）。AtlasCloud にフォールバックしようとしましたが、"
            "AtlasCloud の API キーがありません（~/.config/atlascloud.key か "
            "$ATLASCLOUD_API_KEY）。キーを設定するか --no-fallback で無効化してください。"
        )
    return atlas


def _die_no_atlas_mapping(or_model: str) -> "NoReturn":  # type: ignore[name-defined]
    die(
        f"OpenRouter 402。AtlasCloud に {or_model} の対応が無いので "
        f"--or-model で指定し直してください"
    )


def _atlas_llm_model(or_model: str) -> str:
    if or_model in _ATLAS_TEXT_MODEL_MAP:
        return _ATLAS_TEXT_MODEL_MAP[or_model]
    if or_model.startswith("x-ai/"):
        return "xai/" + or_model[len("x-ai/"):]
    return or_model


def _fallback_llm(args: argparse.Namespace) -> int:
    atlas = _load_atlas_or_die()
    atlas_model = args.or_model or _atlas_llm_model(args.model)
    log("OpenRouter 402（残高切れ）→ AtlasCloud にフォールバックします")
    log(f"[AtlasCloud] llm -> {atlas_model}")
    ns = argparse.Namespace(
        model=atlas_model,
        prompt=args.prompt,
        stdin=False,
        system=args.system,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    return atlas.cmd_llm(ns)


def _fallback_image(args: argparse.Namespace) -> int:
    atlas = _load_atlas_or_die()
    atlas_model = args.or_model or _ATLAS_IMAGE_MODEL_MAP.get(args.model)
    if not atlas_model:
        _die_no_atlas_mapping(args.model)
    log("OpenRouter 402（残高切れ）→ AtlasCloud にフォールバックします")
    if args.image:
        log("  注意: AtlasCloud フォールバックは text-to-image のため --image（入力画像）は無視されます")
    log(f"[AtlasCloud] image -> {atlas_model}")
    ns = argparse.Namespace(
        model=atlas_model,
        prompt=args.prompt,
        out=args.out,
        size=None,
        seed=None,
        extra_json=None,
        sync=False,
    )
    return atlas.cmd_image(ns)


def _fallback_video(args: argparse.Namespace) -> int:
    atlas = _load_atlas_or_die()
    atlas_model = args.or_model or _ATLAS_VIDEO_MODEL_MAP.get((args.task, args.model))
    if not atlas_model:
        _die_no_atlas_mapping(args.model)
    # AtlasCloud takes model-specific fields via extra_json; forward only the two
    # that the wan-2.7 schema documents (aspect_ratio, duration). OpenRouter-only
    # option names (resolution/audio) and per-vendor-shaped ones (seed/reference)
    # are announced as dropped rather than guessed onto AtlasCloud's schema.
    extra: dict = {}
    if args.aspect_ratio:
        extra["aspect_ratio"] = args.aspect_ratio
    if args.duration is not None:
        extra["duration"] = args.duration
    dropped = [
        name
        for name, val in (
            ("--resolution", args.resolution),
            ("--seed", args.seed),
            ("--audio", args.audio),
            ("--reference", args.reference),
        )
        if val
    ]
    log("OpenRouter 402（残高切れ）→ AtlasCloud にフォールバックします")
    if dropped:
        log(f"  注意: {', '.join(dropped)} は AtlasCloud フォールバックには引き継がれません")
    log(f"[AtlasCloud] video -> {atlas_model} ({args.task})")
    ns = argparse.Namespace(
        model=atlas_model,
        prompt=args.prompt,
        out=args.out,
        image=args.image if args.task == "i2v" else None,
        images=None,
        extra_json=json.dumps(extra) if extra else None,
        sync=False,
    )
    return atlas.cmd_video(ns)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _add_fallback_flags(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--no-fallback", action="store_true",
                    help="disable the AtlasCloud fallback triggered on HTTP 402 (out of credits)")
    sp.add_argument("--or-model", default=None, dest="or_model",
                    help="explicit AtlasCloud model id for the 402 fallback "
                         "(overrides the built-in OpenRouter->AtlasCloud id map)")


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
    _add_fallback_flags(pl)
    pl.set_defaults(func=cmd_llm)

    pi = sub.add_parser("image", help="text-to-image (chat/completions+modalities)")
    pi.add_argument("--model", required=True,
                    help="image-output model, e.g. google/gemini-2.5-flash-image-preview "
                         "or black-forest-labs/flux.2-pro")
    pi.add_argument("--prompt", required=True)
    pi.add_argument("--image", action="append", default=None,
                    help="input image for edit-style prompts (path/url); repeatable")
    pi.add_argument("--out", default="image.png", help="output image path")
    pi.add_argument("--aspect-ratio", default=None, dest="aspect_ratio",
                    help="output aspect ratio, e.g. 16:9|9:16|1:1 (uses the dedicated "
                         "/images endpoint; chat route cannot control dimensions)")
    pi.add_argument("--resolution", default=None,
                    help="output resolution tier 512|1K|2K|4K (dedicated /images endpoint)")
    _add_fallback_flags(pi)
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
    _add_fallback_flags(pv)
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
