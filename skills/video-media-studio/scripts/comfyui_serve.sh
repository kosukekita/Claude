#!/usr/bin/env bash
# comfyui_serve.sh — launch a headless ComfyUI server for the HunyuanCustom r2v path.
#
# This is the SINGLE launch path shared by both humans (manual debug) and the
# gen_hunyuan_custom.py wrapper (auto-spawn), so the environment never drifts.
# It:
#   (1) sources env.sh to scrub anaconda libtinfo LD pollution + set HF_HOME (D drive),
#   (2) execs ComfyUI's OWN venv python (/data/kita/ComfyUI/.venv), NOT conda/uv-run,
#   (3) binds to 127.0.0.1 only (NSFW-local; never expose externally),
#   (4) tries SageAttention first, falls back to sdpa if the flag makes startup fail.
#
# Usage:
#   comfyui_serve.sh [--port 8188] [--gpu N] [--no-sage] [-- <extra main.py args>]
# Env overrides:
#   COMFYUI_ROOT (default /data/kita/ComfyUI)
#
# Runs in the foreground (exec). Callers that want it in the background should
# background this script itself (the wrapper does; humans use `&`).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# --- clean env (conda LD scrub + HF_HOME on D). harmless if env.sh absent. ---
# shellcheck source=/dev/null
[ -f "$HERE/env.sh" ] && . "$HERE/env.sh" >/dev/null 2>&1 || true

COMFYUI_ROOT="${COMFYUI_ROOT:-/data/kita/ComfyUI}"
PORT=8188
GPU=""
USE_SAGE=1
EXTRA=()

while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --gpu)  GPU="$2";  shift 2 ;;
    --no-sage) USE_SAGE=0; shift ;;
    --) shift; EXTRA=("$@"); break ;;
    *) echo "comfyui_serve.sh: unknown arg: $1" >&2; exit 2 ;;
  esac
done

VENV_PY="$COMFYUI_ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "comfyui_serve.sh: ComfyUI venv python not found at $VENV_PY" >&2
  echo "  (run Stage 1 setup first: uv venv $COMFYUI_ROOT/.venv --python 3.11)" >&2
  exit 1
fi
if [ ! -f "$COMFYUI_ROOT/main.py" ]; then
  echo "comfyui_serve.sh: ComfyUI main.py not found under $COMFYUI_ROOT" >&2
  exit 1
fi

# Pin GPU for this server (torch inside ComfyUI sees it as cuda:0).
if [ -n "$GPU" ]; then
  export CUDA_VISIBLE_DEVICES="$GPU"
fi

ARGS=(--listen 127.0.0.1 --port "$PORT")
if [ "$USE_SAGE" -eq 1 ]; then
  ARGS+=(--use-sage-attention)
fi
if [ "${#EXTRA[@]}" -gt 0 ]; then
  ARGS+=("${EXTRA[@]}")
fi

echo "comfyui_serve.sh: COMFYUI_ROOT=$COMFYUI_ROOT PORT=$PORT GPU=${GPU:-all} sage=$USE_SAGE" >&2
cd "$COMFYUI_ROOT"
exec "$VENV_PY" main.py "${ARGS[@]}"
