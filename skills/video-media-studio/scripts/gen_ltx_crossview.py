#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
# ]
# ///
"""gen_ltx_crossview.py — reference VIDEO + camera-angle prompt -> same scene from
a NEW virtual camera angle, via a headless ComfyUI server running the LTX-Video
2.3 (22B) CrossView IC-LoRA (Cseti/LTX2.3-22B_IC-LoRA-CrossView-Prompt).

"Virtual second camera": feed one reference video and a discrete camera-angle
prompt (fixed 63-word vocabulary) and it re-renders the same take from the
requested viewpoint. v2v, no start image. See
reference/ltx-crossview-multicam.md and reference/crossview_captions_all_63.txt.

THIN wrapper (gen_hunyuan_custom.py pattern): the heavy runtime lives in
ComfyUI's own venv. Here we: start ComfyUI, fetch object_info, convert the saved
UI workflow -> API format (ui_to_api.convert), patch the reference video / prompt
/ LoRA scales / model paths, POST /prompt, poll /history, pull the mp4. torch is
NOT a dependency of this script.

★★ 要テスト調整（基盤モデルDL完了後の初回実行で確認・微修正が要る箇所）:
  1. プロンプト注入ノード: TextBox1(id 5084) にcrossviewトリガを入れているが、実際に
     サンプラを条件付けるのが TextBox1 経由か CLIPTextEncode(正 id 2483) 経由かは
     リンクを追って確認する（2483 にはサンプルのシーン記述が残っている）。
  2. 出力回収: VHS_VideoCombine が4つある（base / 2x upscaled / preview 等）。
     最終＝2xアップスケール済みの save_output ノードを1つに絞って回収する
     （現状は save_output=true の全ノードに一意prefixを付け、collectは最初のmp4を拾う）。
  3. ローダのパス: workflow は `LTX2/...` サブフォルダ表記だが、DLは各 models 直下(flat)。
     _flatten_loader_paths で .safetensors を basename 化して合わせている。全ローダが
     ComfyUI 側で解決できるか初回で確認（未解決なら該当ファイルをサブフォルダへ配置 or
     widget を実パスへ）。
  4. VHS_LoadVideo の frame_load_cap（既定89）と force_rate=24。長い/短い参照に応じて調整。

Usage:
  source scripts/env.sh
  gen_ltx_crossview.py --ref take.mp4 \
    --azimuth "slightly to the left" --elevation "higher" --distance "closer" \
    --out newangle.mp4 [--ic-lora-scale 1.5 --speed-lora-scale 0.6 --gpu 1]

Output contract: WHY logs to stderr; final mp4 abs path to stdout; return 0.
Idempotent: if --out exists non-empty, skip and print it.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import requests

# import the UI->API converter that lives next to us
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_to_api  # noqa: E402  (fetch_object_info, convert)

PREFIX = "[gen_ltx_crossview]"
COMFYUI_ROOT_DEFAULT = "/data/kita/ComfyUI"
DEFAULT_UI_WORKFLOW = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "reference", "crossview-workflow", "ltx2.3-ic-lora-crossview.json",
)

# Actual on-disk (flat) filenames of the base stack, downloaded into the matching
# ComfyUI models/<subdir>/ root. Used to normalise loader widget paths.
IC_LORA_FILE = "LTX2.3-22B_IC-LoRA-CrossView-Prompt_v0.9_13700.safetensors"
SPEED_LORA_FILE = "ltx-2.3-22b-distilled-1.1_lora-dynamic_fro09_avg_rank_111_bf16.safetensors"

# CrossView fixed vocabulary (must match reference/crossview_captions_all_63.txt)
AZIMUTH = ["far to the left", "to the left", "slightly to the left", "same angle",
           "slightly to the right", "to the right", "far to the right"]
ELEVATION = ["lower", "same height", "higher"]
DISTANCE = ["closer", "same distance", "further"]


def log(msg: str) -> None:
    print(f"{PREFIX} {msg}", file=sys.stderr, flush=True)


def build_prompt(azimuth: str, elevation: str, distance: str) -> str:
    for val, allowed, name in ((azimuth, AZIMUTH, "azimuth"),
                               (elevation, ELEVATION, "elevation"),
                               (distance, DISTANCE, "distance")):
        if val not in allowed:
            raise SystemExit(f"{PREFIX} invalid {name} '{val}'. allowed: {allowed}")
    return f"crossview. new camera angle: {azimuth}, {elevation}, {distance}."


# ---------- headless ComfyUI helpers (gen_hunyuan_custom.py pattern) ----------
def wait_until_ready(server: str, deadline_s: float, proc=None) -> bool:
    start = time.time()
    while time.time() - start < deadline_s:
        try:
            if requests.get(f"{server}/system_stats", timeout=5).status_code == 200:
                return True
        except requests.RequestException:
            pass
        if proc is not None and proc.poll() is not None:
            log(f"ComfyUI exited early code={proc.returncode}")
            return False
        time.sleep(2)
    return False


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
    return subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def place_ref_video(comfyui_root: str, ref_path: str) -> str:
    """Copy the reference video into ComfyUI/input/ so VHS_LoadVideo can read it.
    Returns the basename to set on the loader."""
    indir = os.path.join(comfyui_root, "input")
    os.makedirs(indir, exist_ok=True)
    base = os.path.basename(ref_path)
    dst = os.path.join(indir, base)
    if os.path.abspath(ref_path) != os.path.abspath(dst):
        shutil.copy2(ref_path, dst)
    return base


def submit(server: str, wf: dict) -> str:
    r = requests.post(f"{server}/prompt", json={"prompt": wf}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"/prompt rejected ({r.status_code}): {r.text[:800]}")
    return r.json()["prompt_id"]


def poll_history(server: str, prompt_id: str, timeout_s: float):
    deadline = time.time() + timeout_s
    attempts, max_attempts = 0, int(timeout_s / 3) + 20
    while time.time() < deadline and attempts < max_attempts:
        attempts += 1
        try:
            r = requests.get(f"{server}/history/{prompt_id}", timeout=15)
            if r.status_code == 200 and prompt_id in r.json():
                entry = r.json()[prompt_id]
                status = entry.get("status", {})
                if status.get("completed") or status.get("status_str") == "success":
                    return entry
                if status.get("status_str") == "error":
                    raise RuntimeError(f"generation errored: {json.dumps(status)[:600]}")
        except requests.RequestException as e:  # noqa: BLE001
            log(f"poll transient error: {e}")
        time.sleep(3)
    raise TimeoutError(f"generation did not finish within {timeout_s}s")


def collect_output(server: str, entry: dict, out_path: str, want_prefix: str) -> None:
    outputs = entry.get("outputs", {})
    target = None
    # prefer an mp4 whose filename carries our unique prefix (the final save node)
    for nid, out in outputs.items():
        for key in ("gifs", "videos", "images"):
            for item in out.get(key, []) or []:
                fn = item.get("filename", "")
                if fn.lower().endswith((".mp4", ".webm", ".mkv")):
                    if want_prefix in fn:
                        target = item
                        break
                    target = target or item  # fallback: first video seen
            if target and want_prefix in target.get("filename", ""):
                break
    if target is None:
        raise RuntimeError(f"no video output in history: {json.dumps(outputs)[:600]}")
    r = requests.get(f"{server}/view", params={
        "filename": target["filename"],
        "subfolder": target.get("subfolder", ""),
        "type": target.get("type", "output"),
    }, timeout=180)
    r.raise_for_status()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)


# ---------- API-workflow patching ----------
def _set_str_input(node: dict, match_pred, new_val) -> bool:
    """Set the first input whose current value satisfies match_pred. Returns True if set."""
    for k, v in node.get("inputs", {}).items():
        if isinstance(v, list):
            continue  # link, not a widget value
        if match_pred(v):
            node["inputs"][k] = new_val
            return True
    return False


def _flatten_loader_paths(api: dict) -> None:
    """workflow references LoRA/model files with `LTX2/...` subfolders; our download
    layout is flat (basename at models/<dir>/ root). Rewrite any .safetensors widget
    value on *Loader* nodes to its basename so ComfyUI resolves it. (要テスト調整 #3)"""
    for node in api.values():
        ct = node.get("class_type", "")
        if "Loader" not in ct and "Load" not in ct:
            continue
        for k, v in node.get("inputs", {}).items():
            if isinstance(v, str) and v.lower().endswith(".safetensors") and "/" in v:
                node["inputs"][k] = os.path.basename(v)


def patch(api: dict, prompt: str, ref_basename: str, ic_scale: float,
          speed_scale: float, out_prefix: str) -> dict:
    def nodes_of(ct):
        return [(nid, n) for nid, n in api.items() if n.get("class_type") == ct]

    # 1) reference video (VHS_LoadVideo.video)
    for nid, n in nodes_of("VHS_LoadVideo"):
        if not _set_str_input(n, lambda v: isinstance(v, str) and v.lower().endswith(
                (".mp4", ".mov", ".webm", ".mkv", ".avi")), ref_basename):
            n["inputs"]["video"] = ref_basename

    # 2) crossview prompt: TextBox1 holds the trigger (要テスト調整 #1)
    patched_prompt = False
    for nid, n in nodes_of("TextBox1"):
        if _set_str_input(n, lambda v: isinstance(v, str) and "crossview" in v.lower(), prompt):
            patched_prompt = True
    if not patched_prompt:
        # fallback: put the crossview trigger on the positive CLIPTextEncode
        for nid, n in nodes_of("CLIPTextEncode"):
            _set_str_input(n, lambda v: isinstance(v, str) and "crossview" in v.lower(), prompt)

    # 3) IC-LoRA loader: filename -> our flat file, strength -> ic_scale
    for nid, n in nodes_of("LTXICLoRALoaderModelOnly"):
        _set_str_input(n, lambda v: isinstance(v, str) and v.lower().endswith(".safetensors"),
                       IC_LORA_FILE)
        for k, v in n.get("inputs", {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                n["inputs"][k] = ic_scale

    # 4) distilled speed LoRA: strength -> speed_scale (filename normalised by flatten)
    for nid, n in nodes_of("LoraLoaderModelOnly"):
        for k, v in n.get("inputs", {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                n["inputs"][k] = speed_scale

    # 5) outputs: unique prefix on every saved VHS_VideoCombine (要テスト調整 #2)
    for nid, n in nodes_of("VHS_VideoCombine"):
        ins = n.setdefault("inputs", {})
        if ins.get("save_output") is True or ins.get("save_output") is None:
            ins["filename_prefix"] = out_prefix

    _flatten_loader_paths(api)
    return api


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="reference video (the take to re-shoot)")
    ap.add_argument("--azimuth", required=True, help=f"one of {AZIMUTH}")
    ap.add_argument("--elevation", required=True, help=f"one of {ELEVATION}")
    ap.add_argument("--distance", required=True, help=f"one of {DISTANCE}")
    ap.add_argument("--out", required=True, help="output mp4 path")
    ap.add_argument("--ic-lora-scale", type=float, default=1.5)
    ap.add_argument("--speed-lora-scale", type=float, default=0.6)
    ap.add_argument("--gpu", default=None, help="physical GPU index for ComfyUI")
    ap.add_argument("--server", default=None, help="use an already-running ComfyUI URL")
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--comfyui-root", default=COMFYUI_ROOT_DEFAULT)
    ap.add_argument("--ui-workflow", default=DEFAULT_UI_WORKFLOW)
    ap.add_argument("--keep-server", action="store_true")
    ap.add_argument("--no-sage", action="store_true")
    ap.add_argument("--timeout", type=float, default=2400)
    ap.add_argument("--print-workflow", action="store_true",
                    help="convert+patch and print the API workflow, then exit (needs a running server for object_info)")
    args = ap.parse_args()

    prompt = build_prompt(args.azimuth, args.elevation, args.distance)
    log(f"prompt: {prompt}")

    if os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        log(f"output exists, skipping: {args.out}")
        print(os.path.abspath(args.out))
        return 0

    with open(args.ui_workflow) as f:
        ui = json.load(f)
    out_prefix = f"crossview_{abs(hash(prompt)) % 100000}"

    server = args.server
    proc = None
    use_sage = not args.no_sage
    try:
        if server is None:
            server = f"http://127.0.0.1:{args.port}"
            if not wait_until_ready(server, 3):
                proc = spawn_comfyui(args.comfyui_root, args.port, args.gpu, use_sage)
                if not wait_until_ready(server, 240, proc=proc):
                    if use_sage:
                        log("startup failed; retry without sage-attention")
                        proc.terminate()
                        proc = spawn_comfyui(args.comfyui_root, args.port, args.gpu, False)
                        if not wait_until_ready(server, 240, proc=proc):
                            raise RuntimeError("ComfyUI failed to start")
                    else:
                        raise RuntimeError("ComfyUI failed to start")
        else:
            if not wait_until_ready(server, 10):
                raise RuntimeError(f"--server {server} not responding")
        log(f"server ready: {server}")

        # UI -> API (needs the running server's object_info)
        obj_info = ui_to_api.fetch_object_info(server)
        api = ui_to_api.convert(ui, obj_info)

        ref_base = place_ref_video(args.comfyui_root, args.ref)
        log(f"reference video placed in ComfyUI/input as {ref_base}")
        api = patch(api, prompt, ref_base, args.ic_lora_scale, args.speed_lora_scale, out_prefix)

        if args.print_workflow:
            print(json.dumps(api, indent=2, ensure_ascii=False))
            return 0

        pid = submit(server, api)
        log(f"submitted prompt_id={pid}; polling (timeout={args.timeout}s)")
        t0 = time.time()
        entry = poll_history(server, pid, args.timeout)
        log(f"done in {time.time()-t0:.0f}s; collecting mp4")
        collect_output(server, entry, args.out, out_prefix)
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
