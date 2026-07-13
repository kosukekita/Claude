#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
# ]
# ///
"""
cloud_atlascloud.py — AtlasCloud API backend for the `video-media-studio` skill.

WHEN TO USE THIS
================
AtlasCloud is an EXPLICIT, user-named backend — NOT part of the local-first auto
ladder and NOT consulted by probe_backend.py. It is the same "use it only when
named" seam as cloud_openrouter.py / grok-media: the user asks for it and the
skill routes here. It is useful as a second cloud vendor (independent billing +
a different model roster, including some NSFW-capable video models).

It does the same THREE generation tasks plus TWO discovery helpers:
  llm     chat/completion against any AtlasCloud text model (OpenAI-compatible)
  image   text-to-image, async submit -> poll -> download
  video   text/image/reference-to-video, async submit -> poll -> download
  models  list model ids from the full catalog (filter by type / grep)
  schema  print a model's request fields (each model's fields differ)

--------------------------------------------------------------------------------
API KEY SETUP (one time)  —  dedicated file, mirroring ~/.config/openrouter.key
--------------------------------------------------------------------------------
  1. Get a key from the AtlasCloud dashboard.
  2. Save it to ~/.config/atlascloud.key (one line, NO trailing newline):
         umask 077 && printf '%s' '<key>' > ~/.config/atlascloud.key
         chmod 600 ~/.config/atlascloud.key
  3. (Alternative) export ATLASCLOUD_API_KEY=<key> in the environment.

  Key resolution order (first hit wins):
     ~/.config/atlascloud.key   ->   $ATLASCLOUD_API_KEY
  The key is always .strip()'d (a stray newline otherwise breaks auth) and is
  never printed to stdout / logs / error messages.

--------------------------------------------------------------------------------
ENDPOINTS  —  ★LLM and media live under DIFFERENT bases (mixing them 404s)
--------------------------------------------------------------------------------
  LLM base   : https://api.atlascloud.ai/v1
      POST /chat/completions   (OpenAI-compatible; choices[0].message.content)
      GET  /models             (text models only; output_modalities is unreliable)
  Media base : https://api.atlascloud.ai/api/v1
      GET  /models             (full 408-model catalog; use `type` for modality)
      POST /model/generateImage
      POST /model/generateVideo
      GET  /model/prediction/{id}   (shared poll endpoint for image AND video)
      POST /model/uploadMedia       (multipart; UNVERIFIED — see _upload_media)

--------------------------------------------------------------------------------
API QUIRKS THAT BURN YOU (verified live 2026-07-09 — trust these over the docs)
--------------------------------------------------------------------------------
  * Error envelope is NOT OpenAI's {"error":{...}} — it is {"code":N,"msg":"..."}.
  * ★An INVALID API KEY returns HTTP 404 (body {"code":404,"msg":"not found"}),
    NOT 401. An invalid MODEL returns HTTP 400. So a 404 here almost always means
    "bad/missing key", not "endpoint gone" — this script says so on 404.
  * Full catalog envelope has code as the STRING "200"; each item is
    {uuid, model, type, displayName, price, schema, ...}. `type` is
    "Text"/"Image"/"Video" and is the reliable modality signal.
  * `schema` on a catalog item is a URL (string) to an OpenAPI doc, not JSON.
    `components.schemas.Input.properties` there lists that model's real fields —
    per-model, so `schema --model <id>` is how you learn field names.
  * image `size` is "W*H" with an ASTERISK ("1024*1024"), not "1024x1024".
  * Prediction terminal states are ONLY "completed" and "failed"; any other
    string means "still processing" (poll loop is double-guarded regardless).
  * Video task is chosen by the MODEL ID suffix (.../text-to-video,
    .../image-to-video, .../reference-to-video), not by a parameter. i2v input is
    `image` (single URL/base64 string); reference is `images` (1-3 array).
  * There is NO documented AtlasCloud "out of credits" HTTP status. Do not assume
    402. Any non-2xx is surfaced verbatim ({code,msg}) and the run stops.

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
  # LLM (prints the reply to stdout; long prompt via --stdin)
  ./cloud_atlascloud.py llm --model deepseek-ai/DeepSeek-V3.1 --prompt "..."
  echo "long prompt" | ./cloud_atlascloud.py llm --model xai/grok-4.5 --stdin

  # text-to-image
  ./cloud_atlascloud.py image --model z-image/turbo --prompt "..." \
      --size 1024*1024 --seed 7 --out a.png

  # text-to-video / image-to-video / reference-to-video (task = model id suffix)
  ./cloud_atlascloud.py video --model alibaba/wan-2.7/text-to-video \
      --prompt "..." --out a.mp4
  ./cloud_atlascloud.py video --model alibaba/wan-2.7/image-to-video \
      --prompt "she turns to camera" --image https://.../frame.png --out a.mp4

  # model-specific fields (aspect_ratio / duration / negative_prompt / ...):
  #   look them up first, then pass them through --extra-json.
  ./cloud_atlascloud.py schema --model alibaba/wan-2.7/text-to-video
  ./cloud_atlascloud.py video --model alibaba/wan-2.7/text-to-video --prompt "..." \
      --out a.mp4 --extra-json '{"aspect_ratio":"9:16","duration":5}'

  # discovery
  ./cloud_atlascloud.py models --type Video --grep spicy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import time
from pathlib import Path

import requests

LLM_BASE = "https://api.atlascloud.ai/v1"
MEDIA_BASE = "https://api.atlascloud.ai/api/v1"
KEY_FILE = Path.home() / ".config" / "atlascloud.key"

# Network defaults. Image/video renders are async; the poll loop is bounded by
# BOTH a wall-clock deadline AND a max attempt count (see _poll_prediction).
HTTP_TIMEOUT = 120           # per-request seconds
IMAGE_POLL_INTERVAL = 2      # seconds between image status polls
VIDEO_POLL_INTERVAL = 5      # seconds between video status polls
IMAGE_POLL_MAX_SECONDS = 600  # hard wall-clock deadline for an image job
VIDEO_POLL_MAX_SECONDS = 900  # hard wall-clock deadline for a video job (15 min)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    log(msg)
    raise SystemExit(1)


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
def resolve_api_key() -> str:
    """File first (~/.config/atlascloud.key), then env. Always stripped."""
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
        log(f"WARNING: {KEY_FILE} exists but is empty; trying $ATLASCLOUD_API_KEY")
    env = os.environ.get("ATLASCLOUD_API_KEY", "").strip()
    if env:
        return env
    die(
        textwrap.dedent(
            f"""\
            ERROR: no AtlasCloud API key found.

            Looked in (in order):
              1. {KEY_FILE}
              2. $ATLASCLOUD_API_KEY

            Save your key to the dedicated file (one line, no trailing newline):

                umask 077 && printf '%s' '<key>' > {KEY_FILE}
                chmod 600 {KEY_FILE}

            (or: export ATLASCLOUD_API_KEY=<key>)"""
        )
    )


def auth_headers(key: str) -> dict:
    """For POSTs that carry a JSON body."""
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _get_headers(key: str) -> dict:
    """For bodyless GETs. AtlasCloud only wants Content-Type when a body is sent,
    so plain GETs send Authorization only."""
    return {"Authorization": f"Bearer {key}"}


# --------------------------------------------------------------------------- #
# Error handling — AtlasCloud speaks {code,msg}, and 404 usually means bad key
# --------------------------------------------------------------------------- #
def _atlas_error_fields(resp: requests.Response) -> tuple:
    """Best-effort (code, msg) out of AtlasCloud's {"code":N,"msg":"..."} body."""
    try:
        body = resp.json()
    except ValueError:
        return None, resp.text[:300]
    if isinstance(body, dict):
        return body.get("code"), (body.get("msg") or body.get("message"))
    return None, str(body)[:300]


def _atlas_error_text(resp: requests.Response) -> str:
    code, msg = _atlas_error_fields(resp)
    return f"{{code={code!r}, msg={msg!r}}}"


def _raise_for_atlas(resp: requests.Response) -> None:
    if resp.status_code < 400:
        return
    envelope = _atlas_error_text(resp)
    hint = ""
    if resp.status_code == 404:
        # ★AtlasCloud returns 404 for a BAD/MISSING KEY, not just a missing route.
        hint = (
            " — ★404 is AtlasCloud's response to an INVALID/MISSING API KEY as well "
            "as to a genuinely missing endpoint. Check ~/.config/atlascloud.key "
            "(or $ATLASCLOUD_API_KEY) before assuming the URL is wrong. A bad "
            "MODEL name usually returns 400 instead."
        )
    elif resp.status_code == 400:
        hint = " — likely a bad/nonexistent model id (try `models`)."
    elif resp.status_code == 429:
        hint = " — rate limited."
    die(f"ERROR: AtlasCloud HTTP {resp.status_code} {envelope}{hint}")


# --------------------------------------------------------------------------- #
# LLM (synchronous, OpenAI-compatible, under /v1)
# --------------------------------------------------------------------------- #
def cmd_llm(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    prompt = sys.stdin.read() if args.stdin else args.prompt
    if not prompt:
        die("ERROR: empty prompt (pass --prompt TEXT or pipe text with --stdin)")
    messages: list = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": prompt})
    body: dict = {"model": args.model, "messages": messages}
    if args.max_tokens is not None:
        body["max_tokens"] = args.max_tokens
    if args.temperature is not None:
        body["temperature"] = args.temperature

    log(f"llm -> {args.model}")
    resp = requests.post(
        f"{LLM_BASE}/chat/completions",
        headers=auth_headers(key),
        json=body,
        timeout=HTTP_TIMEOUT,
    )
    _raise_for_atlas(resp)
    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        die(f"ERROR: unexpected LLM response shape ({exc}): {json.dumps(data)[:500]}")
    print(text)
    return 0


# --------------------------------------------------------------------------- #
# Image / Video — async submit -> shared poll -> download
# --------------------------------------------------------------------------- #
def _submit_and_poll(key: str, verb: str, body: dict, interval: int, timeout: int) -> dict:
    """Submit a generation job (verb = generateImage | generateVideo) and poll
    the SHARED prediction endpoint until it terminates. Only the submit verb
    differs between image and video; the poll is identical. Returns the completed
    prediction `data` dict (whose `outputs[0]` is the result URL)."""
    submit_url = f"{MEDIA_BASE}/model/{verb}"
    log(f"submit -> {verb}: model={body.get('model')}")
    resp = requests.post(submit_url, headers=auth_headers(key), json=body, timeout=HTTP_TIMEOUT)
    _raise_for_atlas(resp)
    payload = resp.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict) or not data.get("id"):
        die(f"ERROR: submit response had no data.id: {json.dumps(payload)[:500]}")
    pred_id = data["id"]
    # Prefer the server-supplied poll URL; only synthesise it if absent.
    poll_url = (data.get("urls") or {}).get("get") or f"{MEDIA_BASE}/model/prediction/{pred_id}"
    log(f"prediction id={pred_id}; polling ...")
    return _poll_prediction(key, poll_url, data, interval, timeout)


def _poll_prediction(key: str, poll_url: str, first: dict, interval: int, timeout: int) -> dict:
    """Poll until completed/failed. Double-guarded by a wall-clock deadline AND a
    max attempt count. ★Only 'completed'/'failed' are terminal; every other
    status string is treated as "still processing" so an unknown intermediate
    state can never spin forever."""
    max_attempts = int(timeout / max(interval, 1)) + 10
    waited = 0
    attempts = 0
    status = first
    while True:
        state = (status.get("status") or "").lower()
        if state == "completed":
            return status
        if state == "failed":
            # `error` is a string on failure (empty string, not null, on success).
            err = status.get("error") or ""
            die(f"ERROR: prediction failed: {err or json.dumps(status)[:400]}")
        attempts += 1
        if attempts > max_attempts:
            die(f"ERROR: prediction still '{state or 'processing'}' after {attempts} polls; giving up")
        if waited >= timeout:
            die(f"ERROR: prediction still '{state or 'processing'}' after {waited}s deadline; giving up")
        time.sleep(interval)
        waited += interval
        log(f"  status={state or 'processing'} ({waited}s elapsed)")
        r = requests.get(poll_url, headers=_get_headers(key), timeout=HTTP_TIMEOUT)
        _raise_for_atlas(r)
        payload = r.json()
        status = payload.get("data") if isinstance(payload, dict) else {}
        if not isinstance(status, dict):
            status = {}


def _first_output(data: dict) -> str:
    outs = data.get("outputs")
    if not outs:
        die(f"ERROR: completed prediction had no outputs: {json.dumps(data)[:500]}")
    return outs[0]


def cmd_image(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    body: dict = {"model": args.model, "prompt": args.prompt}
    if args.size:
        body["size"] = args.size  # ★"W*H" with an asterisk, not "WxH".
    if args.seed is not None:
        body["seed"] = args.seed
    if getattr(args, "image", None):
        body["images"] = [_resolve_media_input(key, x) for x in args.image]  # seedream .../edit reference images (up to 10)
    if args.sync:
        body["enable_sync_mode"] = True
    _merge_extra_json(body, args.extra_json)

    data = _submit_and_poll(key, "generateImage", body, IMAGE_POLL_INTERVAL, IMAGE_POLL_MAX_SECONDS)
    out = Path(args.out).expanduser()
    _download(_first_output(data), out)
    log(f"saved -> {out.resolve()}")
    print(str(out.resolve()))
    return 0


def cmd_video(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    body: dict = {"model": args.model, "prompt": args.prompt}
    # Task (t2v / i2v / r2v) is picked by the MODEL ID suffix, not a flag.
    if args.image:
        body["image"] = _resolve_media_input(key, args.image)  # single URL/base64
    if getattr(args, "end_image", None):
        body["end_image"] = _resolve_media_input(key, args.end_image)  # Kling i2v ending frame
    if getattr(args, "last_image", None):
        body["last_image"] = _resolve_media_input(key, args.last_image)  # Seedance i2v ending frame
    if args.images:
        refs = [_resolve_media_input(key, x) for x in _split_csv(args.images)]
        if refs:
            body["images"] = refs  # 1-3 reference images
    if getattr(args, "reference_image", None):
        rimgs = [_resolve_media_input(key, x) for x in args.reference_image]
        if rimgs:
            body["reference_images"] = rimgs  # seedance-2.0 reference-to-video (up to 9; "image 1..N" in prompt)
    if args.sync:
        body["enable_sync_mode"] = True
    _merge_extra_json(body, args.extra_json)

    data = _submit_and_poll(key, "generateVideo", body, VIDEO_POLL_INTERVAL, VIDEO_POLL_MAX_SECONDS)
    out = Path(args.out).expanduser()
    _download(_first_output(data), out)
    log(f"saved -> {out.resolve()}")
    print(str(out.resolve()))
    return 0


# --------------------------------------------------------------------------- #
# Discovery — full catalog listing + per-model input schema
# --------------------------------------------------------------------------- #
def cmd_models(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    items = _fetch_catalog(key)
    pat = re.compile(args.grep, re.IGNORECASE) if args.grep else None
    for m in items:
        if args.type and m.get("type") != args.type:
            continue
        mid = m.get("model")
        if not mid:
            continue
        if pat and not (pat.search(mid) or pat.search(m.get("displayName") or "")):
            continue
        print(mid)
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    key = resolve_api_key()
    entry = next((m for m in _fetch_catalog(key) if m.get("model") == args.model), None)
    if not entry:
        die(f"ERROR: model '{args.model}' not in catalog; find it with `models --grep ...`")
    schema_url = entry.get("schema")
    if not schema_url:
        die(f"ERROR: model '{args.model}' has no schema url in the catalog entry")
    # The schema URL is a public static OpenAPI doc — no auth needed.
    sr = requests.get(schema_url, timeout=HTTP_TIMEOUT)
    if sr.status_code >= 400:
        die(f"ERROR: schema fetch HTTP {sr.status_code} from {schema_url}: {sr.text[:200]}")
    doc = sr.json()
    inp = (((doc.get("components") or {}).get("schemas") or {}).get("Input") or {})
    props = inp.get("properties") or {}
    if not props:
        die(f"ERROR: no components.schemas.Input.properties in {schema_url}: {json.dumps(doc)[:400]}")
    required = set(inp.get("required") or [])
    print(f"# {args.model} — request fields (Input.properties from {schema_url})")
    for name, spec in props.items():
        spec = spec if isinstance(spec, dict) else {}
        typ = spec.get("type", "?")
        line = f"  {name}: {typ}"
        if name in required:
            line += " (required)"
        if "default" in spec:
            line += f"  [default={spec['default']!r}]"
        if spec.get("description"):
            line += f"  — {spec['description']}"
        print(line)
    return 0


def _fetch_catalog(key: str) -> list:
    """The full 408-model catalog under the media base. Its envelope has code as
    the string "200"; only `data` matters here."""
    resp = requests.get(f"{MEDIA_BASE}/models", headers=_get_headers(key), timeout=HTTP_TIMEOUT)
    _raise_for_atlas(resp)
    data = resp.json()
    items = data.get("data") if isinstance(data, dict) else data
    return items if isinstance(items, list) else []


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _merge_extra_json(body: dict, extra_json: str | None) -> None:
    """Overlay model-specific fields (aspect_ratio / duration / negative_prompt /
    prompt_extend / ...). Fields differ per model, so this is the escape hatch for
    anything not surfaced as a flag — discover names with `schema --model <id>`."""
    if not extra_json:
        return
    try:
        extra = json.loads(extra_json)
    except json.JSONDecodeError as exc:
        die(f"ERROR: --extra-json is not valid JSON ({exc}): {extra_json[:200]}")
    if not isinstance(extra, dict):
        die("ERROR: --extra-json must be a JSON object, e.g. '{\"aspect_ratio\":\"9:16\"}'")
    body.update(extra)


def _split_csv(s: str) -> list:
    return [x.strip() for x in s.split(",") if x.strip()]


def _resolve_media_input(key: str, ref: str) -> str:
    """Turn a media argument into something the API accepts. Public URLs, data:
    URLs and (assumed) base64 strings pass through untouched. A LOCAL FILE is
    base64-encoded into a data: URL — the API accepts base64 image refs directly
    (see schema: "provided via URLs or Base64 encode"), which is the reliable
    path and avoids the UNVERIFIED uploadMedia endpoint."""
    if ref.startswith(("http://", "https://", "data:")):
        return ref
    p = Path(ref).expanduser()
    if p.exists():
        return _file_to_data_url(p)
    # Not a URL and not an existing file: assume it is already base64/pass-through.
    return ref


def _file_to_data_url(path: Path) -> str:
    """Read a local image and return a data: URL. The AtlasCloud schema requires
    the base64 ref to carry a content type, and accepts PNG/JPEG/JPG/WebP only."""
    import base64
    import mimetypes
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    if mime not in ("image/png", "image/jpeg", "image/webp"):
        mime = "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _upload_media(key: str, path: Path) -> str:
    """★UNVERIFIED: uploadMedia has NOT been exercised against the live API. The
    multipart field name (`file`) and the `url` response key are taken from the
    docs only. On ANY failure we stop with a clear instruction, because passing a
    public URL or base64 is the reliable path."""
    url = f"{MEDIA_BASE}/model/uploadMedia"
    log(f"uploadMedia (UNVERIFIED) -> {path.name}")
    try:
        with path.open("rb") as fh:
            r = requests.post(
                url,
                headers=_get_headers(key),  # multipart: let requests set Content-Type
                files={"file": (path.name, fh)},
                timeout=HTTP_TIMEOUT,
            )
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code} {_atlas_error_text(r)}")
        data = r.json()
        media_url = data.get("url") or (data.get("data") or {}).get("url")
        if not media_url:
            raise RuntimeError(f"no `url` in uploadMedia response: {json.dumps(data)[:300]}")
        return media_url
    except Exception as exc:  # noqa: BLE001 — any failure funnels to the same advice
        die(
            f"ERROR: uploadMedia でローカルファイルのアップロードに失敗しました"
            f"（uploadMedia は未検証です）: {exc}\n"
            f"→ 画像は公開 URL か base64 で渡してください。"
        )


def _download(url: str, out: Path) -> None:
    """Result URLs point at public OSS (aliyuncs) and need no auth."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=HTTP_TIMEOUT) as r:
        if r.status_code >= 400:
            die(f"ERROR: download HTTP {r.status_code} from {url[:120]}: {r.text[:200]}")
        with out.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 16):
                if chunk:
                    fh.write(chunk)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cloud_atlascloud.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="AtlasCloud backend (LLM / image / video) for video-media-studio. "
                    "EXPLICIT backend only — not part of the local-first auto ladder.",
        epilog=textwrap.dedent(
            """\
            key: ~/.config/atlascloud.key  (else $ATLASCLOUD_API_KEY)
            examples:
              %(prog)s llm    --model deepseek-ai/DeepSeek-V3.1 --prompt "..."
              %(prog)s image  --model z-image/turbo --prompt "..." --size 1024*1024 --out a.png
              %(prog)s video  --model alibaba/wan-2.7/text-to-video --prompt "..." --out a.mp4
              %(prog)s schema --model alibaba/wan-2.7/text-to-video
              %(prog)s models --type Video --grep spicy
            """
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("llm", help="text chat/completion (OpenAI-compatible, /v1)")
    pl.add_argument("--model", required=True, help="e.g. deepseek-ai/DeepSeek-V3.1, xai/grok-4.5")
    pl.add_argument("--prompt", default="", help="prompt text (or use --stdin)")
    pl.add_argument("--stdin", action="store_true", help="read the prompt from stdin instead")
    pl.add_argument("--system", default=None, help="optional system prompt")
    pl.add_argument("--temperature", type=float, default=None)
    pl.add_argument("--max-tokens", type=int, default=None, dest="max_tokens")
    pl.set_defaults(func=cmd_llm)

    pi = sub.add_parser("image", help="text-to-image (async submit/poll/download)")
    pi.add_argument("--model", required=True, help="e.g. z-image/turbo, google/nano-banana-2/text-to-image")
    pi.add_argument("--prompt", required=True)
    pi.add_argument("--out", default="image.png", help="output image path")
    pi.add_argument("--size", default=None, help='"W*H" with an asterisk, e.g. 1024*1024 (512-2048)')
    pi.add_argument("--seed", type=int, default=None, help="-1 = random")
    pi.add_argument("--image", action="append", default=None,
                    help="reference image for edit models (e.g. seedream .../edit); repeatable; local path/URL/base64")
    pi.add_argument("--extra-json", default=None, dest="extra_json",
                    help='model-specific fields as a JSON object, e.g. \'{"prompt_extend":true}\'')
    pi.add_argument("--sync", action="store_true",
                    help="set enable_sync_mode (default off = poll)")
    pi.set_defaults(func=cmd_image)

    pv = sub.add_parser("video", help="text/image/reference-to-video (async submit/poll/download)")
    pv.add_argument("--model", required=True,
                    help="task is the id SUFFIX, e.g. alibaba/wan-2.7/{text,image,reference}-to-video")
    pv.add_argument("--prompt", required=True)
    pv.add_argument("--out", default="out.mp4", help="output mp4 path")
    pv.add_argument("--image", default=None,
                    help="i2v input image: public URL / base64 / local path (local -> uploadMedia, UNVERIFIED)")
    pv.add_argument("--end-image", default=None, dest="end_image",
                    help="Kling i2v ENDING frame: URL / base64 / local path")
    pv.add_argument("--last-image", default=None, dest="last_image",
                    help="Seedance i2v ENDING frame (last_image): URL / base64 / local path")
    pv.add_argument("--images", default=None,
                    help="reference images (1-3), comma-separated URLs/base64/paths")
    pv.add_argument("--reference-image", action="append", default=None, dest="reference_image",
                    help="reference_images for reference-to-video (repeatable, up to 9; local path/URL/base64; refer as 'image 1..N' in prompt)")
    pv.add_argument("--extra-json", default=None, dest="extra_json",
                    help='model-specific fields as JSON, e.g. \'{"aspect_ratio":"9:16","duration":5}\'')
    pv.add_argument("--sync", action="store_true",
                    help="set enable_sync_mode (default off = poll)")
    pv.set_defaults(func=cmd_video)

    pm = sub.add_parser("models", help="list model ids from the full catalog")
    pm.add_argument("--type", choices=["Text", "Image", "Video"], default=None,
                    help="filter by modality (the reliable signal; NOT output_modalities)")
    pm.add_argument("--grep", default=None, help="regex filter over id + displayName (case-insensitive)")
    pm.set_defaults(func=cmd_models)

    ps = sub.add_parser("schema", help="print a model's request fields (per-model Input schema)")
    ps.add_argument("--model", required=True, help="catalog model id")
    ps.set_defaults(func=cmd_schema)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
