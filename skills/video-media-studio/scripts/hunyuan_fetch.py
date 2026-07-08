#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "huggingface-hub",
# ]
# ///
"""hunyuan_fetch.py — idempotently download the 5 model files HunyuanCustom
(Kijai ComfyUI wrapper) needs, into ComfyUI's models/ subfolders.

Files (see reference/models.md / the plan):
  transformer  Kijai/HunyuanVideo_comfy      hunyuan_video_custom_720p_fp8_scaled.safetensors  -> models/diffusion_models/
  clip_l       Comfy-Org/HunyuanVideo_repackaged  split_files/text_encoders/clip_l.safetensors -> models/text_encoders/
  llava        Comfy-Org/HunyuanVideo_repackaged  split_files/text_encoders/llava_llama3_{fp8_scaled,fp16}.safetensors -> models/text_encoders/
  clip_vision  Comfy-Org/HunyuanVideo_repackaged  split_files/clip_vision/llava_llama3_vision.safetensors -> models/clip_vision/
  vae          Kijai/HunyuanVideo_comfy      hunyuan_video_vae_bf16.safetensors -> models/vae/

The 'split_files/' prefix in the source repo is stripped so the file lands
directly under models/<subfolder>/ where ComfyUI's loaders look.

Output contract: WHY logs to stderr; final JSON summary to stdout.
hf_transfer is force-disabled (individual-file DL stability; see project memory).

Usage:
  hunyuan_fetch.py [--comfyui-root /data/kita/ComfyUI] [--text-enc fp8|fp16] [--check]
"""
import argparse
import json
import os
import sys

# hf_transfer OFF for stable individual-file downloads (multi-process transfer
# has hung on this rig before).
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")

PREFIX = "[hunyuan_fetch]"


def log(msg: str) -> None:
    print(f"{PREFIX} {msg}", file=sys.stderr, flush=True)


# (repo_id, repo_path, dest_subfolder). dest filename = basename(repo_path).
def build_manifest(text_enc: str):
    llava = (
        "llava_llama3_fp8_scaled.safetensors"
        if text_enc == "fp8"
        else "llava_llama3_fp16.safetensors"
    )
    return [
        (
            "transformer",
            "Kijai/HunyuanVideo_comfy",
            "hunyuan_video_custom_720p_fp8_scaled.safetensors",
            "diffusion_models",
        ),
        (
            "clip_l",
            "Comfy-Org/HunyuanVideo_repackaged",
            "split_files/text_encoders/clip_l.safetensors",
            "text_encoders",
        ),
        (
            "llava",
            "Comfy-Org/HunyuanVideo_repackaged",
            f"split_files/text_encoders/{llava}",
            "text_encoders",
        ),
        (
            "clip_vision",
            "Comfy-Org/HunyuanVideo_repackaged",
            "split_files/clip_vision/llava_llama3_vision.safetensors",
            "clip_vision",
        ),
        (
            "vae",
            "Kijai/HunyuanVideo_comfy",
            "hunyuan_video_vae_bf16.safetensors",
            "vae",
        ),
    ]


def dest_path(comfyui_root: str, subfolder: str, repo_path: str) -> str:
    return os.path.join(comfyui_root, "models", subfolder, os.path.basename(repo_path))


def check(comfyui_root: str, manifest) -> dict:
    result = {}
    for role, repo, repo_path, sub in manifest:
        p = dest_path(comfyui_root, sub, repo_path)
        ok = os.path.exists(p) and os.path.getsize(p) > 0
        result[role] = {
            "path": p,
            "exists": ok,
            "bytes": os.path.getsize(p) if ok else 0,
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comfyui-root", default="/data/kita/ComfyUI")
    ap.add_argument("--text-enc", choices=["fp8", "fp16"], default="fp8",
                    help="LLaVA text encoder precision (fp8 saves VRAM; fp16 max quality)")
    ap.add_argument("--check", action="store_true",
                    help="only report existence/size of the 5 files as JSON; no download")
    args = ap.parse_args()

    manifest = build_manifest(args.text_enc)

    if args.check:
        print(json.dumps(check(args.comfyui_root, manifest), indent=2, ensure_ascii=False))
        return 0

    from huggingface_hub import hf_hub_download

    summary = {}
    for role, repo, repo_path, sub in manifest:
        dst = dest_path(args.comfyui_root, sub, repo_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            log(f"SKIP {role}: exists {dst} ({os.path.getsize(dst)} bytes)")
            summary[role] = {"path": dst, "downloaded": False, "bytes": os.path.getsize(dst)}
            continue
        log(f"DL {role}: {repo} :: {repo_path}")
        try:
            cached = hf_hub_download(repo_id=repo, filename=repo_path)
        except Exception as e:  # noqa: BLE001
            log(f"ERROR downloading {role} ({repo} :: {repo_path}): {e}")
            log("  if this is 401/403, run `huggingface-cli login` (see reference/setup.md).")
            return 1
        # hf_hub_download returns the cached blob path; symlink/copy to the
        # ComfyUI dest with the stripped basename.
        import shutil
        if os.path.islink(dst) or os.path.exists(dst):
            os.remove(dst)
        # Prefer a symlink (saves disk; both on D drive) with copy fallback.
        try:
            os.symlink(os.path.realpath(cached), dst)
            how = "symlink"
        except OSError:
            shutil.copy2(cached, dst)
            how = "copy"
        log(f"WROTE {role}: {dst} ({how})")
        summary[role] = {"path": dst, "downloaded": True, "how": how,
                         "bytes": os.path.getsize(dst)}

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
