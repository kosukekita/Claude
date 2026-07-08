#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "pillow",
# ]
# ///
"""gen_hunyuan_custom.py — reference image + text -> arbitrary-scene video
(HunyuanCustom subject customization / r2v) via a headless ComfyUI server
running the Kijai HunyuanVideoWrapper. NSFW-capable (fully local, no safety
checker).

Unlike gen_wan_vace.py (which needs a driving motion video to transfer a pose),
HunyuanCustom takes ONE reference image + a text prompt and generates the person
in an entirely new scene (e.g. "taking a shower in a bathroom") — the identity is
carried by the CLIP-Vision (llava_llama3_vision) encoder into every frame.

This is a THIN wrapper (the LTX-2.3 gen_video_ltx2.py delegation pattern): the
heavy runtime lives in ComfyUI's own venv; here we just patch an API-format
workflow template, upload the ref image, POST /prompt, poll /history, and pull
the mp4. torch is NOT a dependency of this script.

Output contract: WHY logs to stderr; final mp4 abs path to stdout; return 0.
Idempotent: if --out already exists and is non-empty, skip and print it.

Usage:
  source scripts/env.sh
  gen_hunyuan_custom.py --ref ref_body.png \
    --prompt "A woman taking a shower in a bright bathroom, steam, wet skin" \
    --out shower.mp4 [--width 512 --height 896 --num-frames 129 --steps 30 \
    --guidance 7.5 --flow-shift 13.0 --seed 42 --fps 24 --offload 20 --gpu 1]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import requests

PREFIX = "[gen_hunyuan_custom]"

# no-tattoo固定ルール(SKILL.md 人物生成規約) + HunyuanCustom向け英語ネガ
DEFAULT_NEG = (
    "low quality, blurry, distorted, deformed hands, extra fingers, watermark, "
    "text, static, jpeg artifacts, bad anatomy, tattoo, tattoos, body ink, "
    "lettering on skin"
)

# Template patch map. Node ids are stable within our saved template
# (reference/hunyuan_custom_api_template.json); if the template is regenerated,
# re-verify these against the new ids. We locate by id (fast) and sanity-check
# class_type.
DEFAULT_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "reference", "hunyuan_custom_api_template.json",
)
COMFYUI_ROOT_DEFAULT = "/data/kita/ComfyUI"


def log(msg: str) -> None:
    print(f"{PREFIX} {msg}", file=sys.stderr, flush=True)


def find_by_class(wf: dict, class_type: str):
    """Return the (id, node) of the first node with this class_type, or (None, None)."""
    for nid, node in wf.items():
        if node.get("class_type") == class_type:
            return nid, node
    return None, None


def find_all_by_class(wf: dict, class_type: str):
    return [(nid, node) for nid, node in wf.items() if node.get("class_type") == class_type]


def patch_template(wf: dict, args, ref_filename: str, out_prefix: str) -> dict:
    # Reference image (LoadImage) -> uploaded server-side filename
    nid, node = find_by_class(wf, "LoadImage")
    if node is None:
        raise RuntimeError("template has no LoadImage node")
    node["inputs"]["image"] = ref_filename

    # ImageResizeKJv2 -> target dims (the sampler reads width/height from here)
    nid, node = find_by_class(wf, "ImageResizeKJv2")
    if node is not None:
        node["inputs"]["width"] = args.width
        node["inputs"]["height"] = args.height

    # Prompts: there are two TextEncodeHunyuanVideo_ImageToVideo nodes. The one
    # feeding the bridge's 'positive' is positive; the other is negative. We
    # resolve which is which via HyVideoTextEmbedBridge links.
    bnid, bridge = find_by_class(wf, "HyVideoTextEmbedBridge")
    pos_id = neg_id = None
    if bridge is not None:
        pos_ref = bridge["inputs"].get("positive")
        neg_ref = bridge["inputs"].get("negative")
        if isinstance(pos_ref, list):
            pos_id = str(pos_ref[0])
        if isinstance(neg_ref, list):
            neg_id = str(neg_ref[0])
        bridge["inputs"]["cfg"] = args.guidance
    if pos_id and pos_id in wf:
        wf[pos_id]["inputs"]["prompt"] = args.prompt
    if neg_id and neg_id in wf:
        wf[neg_id]["inputs"]["prompt"] = args.negative_prompt
    if pos_id is None:
        # Fallback: patch the first text node as positive.
        tnodes = find_all_by_class(wf, "TextEncodeHunyuanVideo_ImageToVideo")
        if tnodes:
            tnodes[0][1]["inputs"]["prompt"] = args.prompt
            if len(tnodes) > 1:
                tnodes[1][1]["inputs"]["prompt"] = args.negative_prompt

    # Sampler
    nid, node = find_by_class(wf, "HyVideoSampler")
    if node is not None:
        node["inputs"]["num_frames"] = args.num_frames
        node["inputs"]["steps"] = args.steps
        node["inputs"]["flow_shift"] = args.flow_shift
        node["inputs"]["seed"] = args.seed

    # Block swap (VRAM control)
    if args.offload is not None:
        nid, node = find_by_class(wf, "HyVideoBlockSwap")
        if node is not None:
            node["inputs"]["double_blocks_to_swap"] = args.offload

    # VHS_VideoCombine: unique filename prefix + fps + save to output/
    nid, node = find_by_class(wf, "VHS_VideoCombine")
    if node is not None:
        node["inputs"]["filename_prefix"] = out_prefix
        node["inputs"]["frame_rate"] = args.fps
        node["inputs"]["save_output"] = True
    return wf


def wait_until_ready(server: str, deadline_s: float, proc=None) -> bool:
    start = time.time()
    while time.time() - start < deadline_s:
        try:
            r = requests.get(f"{server}/system_stats", timeout=5)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        if proc is not None and proc.poll() is not None:
            log(f"ComfyUI process exited early with code {proc.returncode}")
            return False
        time.sleep(2)
    return False


def upload_image(server: str, path: str) -> str:
    from PIL import Image  # noqa: PLC0415  (validate + normalize EXIF)
    import io
    im = Image.open(path)
    try:
        from PIL import ImageOps
        im = ImageOps.exif_transpose(im)
    except Exception:  # noqa: BLE001
        pass
    im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    fname = os.path.basename(path)
    if not fname.lower().endswith(".png"):
        fname += ".png"
    files = {"image": (fname, buf, "image/png")}
    r = requests.post(f"{server}/upload/image", files=files,
                      data={"overwrite": "true"}, timeout=60)
    r.raise_for_status()
    j = r.json()
    # server returns {"name": ..., "subfolder": ..., "type": "input"}
    name = j.get("name", fname)
    sub = j.get("subfolder", "")
    return f"{sub}/{name}" if sub else name


def submit(server: str, wf: dict) -> str:
    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"/prompt rejected ({r.status_code}): {r.text[:800]}")
    return r.json()["prompt_id"]


def poll_history(server: str, prompt_id: str, timeout_s: float):
    """Poll /history until the prompt completes. Dual guard: wall-clock deadline
    and a max attempt count (cloud_openrouter.py pattern)."""
    deadline = time.time() + timeout_s
    attempts = 0
    max_attempts = int(timeout_s / 3) + 20
    while time.time() < deadline and attempts < max_attempts:
        attempts += 1
        try:
            r = requests.get(f"{server}/history/{prompt_id}", timeout=15)
            if r.status_code == 200:
                hist = r.json()
                if prompt_id in hist:
                    entry = hist[prompt_id]
                    status = entry.get("status", {})
                    if status.get("completed") or status.get("status_str") == "success":
                        return entry
                    # error status
                    if status.get("status_str") == "error":
                        raise RuntimeError(f"generation errored: {json.dumps(status)[:600]}")
        except requests.RequestException as e:  # noqa: BLE001
            log(f"poll transient error: {e}")
        time.sleep(3)
    raise TimeoutError(f"generation did not finish within {timeout_s}s")


def collect_output(server: str, entry: dict, out_path: str) -> None:
    """Find the VHS_VideoCombine mp4 in history outputs and download it."""
    outputs = entry.get("outputs", {})
    target = None
    for nid, out in outputs.items():
        # VHS stores under 'gifs' (mp4s included) with filename/subfolder/type
        for key in ("gifs", "videos", "images"):
            for item in out.get(key, []) or []:
                fn = item.get("filename", "")
                if fn.lower().endswith((".mp4", ".webm", ".mkv")):
                    target = item
                    break
            if target:
                break
        if target:
            break
    if target is None:
        raise RuntimeError(f"no video output found in history: {json.dumps(outputs)[:600]}")
    params = {
        "filename": target["filename"],
        "subfolder": target.get("subfolder", ""),
        "type": target.get("type", "output"),
    }
    r = requests.get(f"{server}/view", params=params, timeout=120)
    r.raise_for_status()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)


def spawn_comfyui(comfyui_root: str, port: int, gpu, use_sage: bool):
    serve = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comfyui_serve.sh")
    cmd = ["bash", serve, "--port", str(port)]
    if gpu is not None:
        cmd += ["--gpu", str(gpu)]
    if not use_sage:
        cmd += ["--no-sage"]
    log(f"spawning ComfyUI: {' '.join(cmd)}")
    env = os.environ.copy()
    env.pop("_GEV_CLEANED", None)
    return subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="reference person image (identity source)")
    ap.add_argument("--prompt", required=True, help="target scene/action (e.g. shower)")
    ap.add_argument("--out", required=True, help="output mp4 path")
    ap.add_argument("--negative-prompt", default=DEFAULT_NEG)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=896)
    ap.add_argument("--num-frames", type=int, default=129, help="HunyuanVideo 4k+1 (129≈5s@24fps)")
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--guidance", type=float, default=7.5, help="cfg (Tencent recommends 7.5)")
    ap.add_argument("--flow-shift", type=float, default=13.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--offload", type=int, default=20,
                    help="block-swap count (higher=less VRAM/slower). None to leave template default")
    ap.add_argument("--gpu", default=None, help="physical GPU index for the ComfyUI server")
    ap.add_argument("--server", default=None, help="use an already-running ComfyUI at this URL")
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--comfyui-root", default=COMFYUI_ROOT_DEFAULT)
    ap.add_argument("--keep-server", action="store_true", help="don't stop a server we spawned")
    ap.add_argument("--no-sage", action="store_true", help="run ComfyUI without sage-attention")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE)
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--print-workflow", action="store_true",
                    help="print the patched API workflow and exit (no generation)")
    args = ap.parse_args()

    # 1) idempotent skip
    if os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        log(f"output exists, skipping: {args.out}")
        print(os.path.abspath(args.out))
        return 0

    # load + patch template (ref filename filled after upload; use placeholder for --print)
    with open(args.template) as f:
        template = json.load(f)
    out_prefix = f"hunyuancustom_{args.seed}_{args.num_frames}f"

    if args.print_workflow:
        wf = patch_template(dict(template), args, "__REF_IMAGE__", out_prefix)
        print(json.dumps(wf, indent=2, ensure_ascii=False))
        return 0

    server = args.server
    proc = None
    use_sage = not args.no_sage
    try:
        # 2) ensure a server
        if server is None:
            server = f"http://127.0.0.1:{args.port}"
            if not wait_until_ready(server, 3):
                proc = spawn_comfyui(args.comfyui_root, args.port, args.gpu, use_sage)
                if not wait_until_ready(server, 180, proc=proc):
                    # sage build may have failed; retry once without it
                    if use_sage:
                        log("startup failed; retrying ComfyUI without sage-attention")
                        proc.terminate()
                        proc = spawn_comfyui(args.comfyui_root, args.port, args.gpu, False)
                        if not wait_until_ready(server, 180, proc=proc):
                            raise RuntimeError("ComfyUI failed to start")
                    else:
                        raise RuntimeError("ComfyUI failed to start")
        else:
            if not wait_until_ready(server, 10):
                raise RuntimeError(f"--server {server} not responding")
        log(f"server ready: {server}")

        # 3) upload ref + patch
        ref_name = upload_image(server, args.ref)
        log(f"uploaded ref -> {ref_name}")
        wf = patch_template(dict(template), args, ref_name, out_prefix)

        # 4) submit + poll + collect
        pid = submit(server, wf)
        log(f"submitted prompt_id={pid}; polling (timeout={args.timeout}s)")
        t0 = time.time()
        entry = poll_history(server, pid, args.timeout)
        log(f"generation done in {time.time()-t0:.0f}s; collecting mp4")
        collect_output(server, entry, args.out)

        if not (os.path.exists(args.out) and os.path.getsize(args.out) > 0):
            raise RuntimeError(f"output not written: {args.out}")
        log(f"saved -> {args.out} ({os.path.getsize(args.out)} bytes)")
    finally:
        if proc is not None and not args.keep_server:
            log("stopping spawned ComfyUI")
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()

    print(os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
