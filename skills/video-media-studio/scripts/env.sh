# shellcheck shell=sh
# env.sh — source this before running any video-media-studio skill script.
#   . "$(dirname "$0")/env.sh"   (or with an absolute path)
#
# Goals:
#   1. Scrub anaconda/miniconda/conda dirs out of LD_LIBRARY_PATH
#      (their libtinfo.so.6 pollutes subprocesses, e.g. soffice, and torch).
#   2. Point UV at the real uv binary.
#   3. Put the HuggingFace cache on the big disk via HF_HOME.
#   4. Set PYTORCH_CUDA_ALLOC_CONF for less fragmentation.
# POSIX sh only (works under bash and dash). Idempotent; safe to re-source.

# --- 1. scrub conda paths out of LD_LIBRARY_PATH ---------------------------
# Keep every ':'-separated entry that does NOT look like a conda/anaconda/
# miniconda/miniforge/mambaforge path. Done with a plain sh loop (no arrays,
# no bashisms). If the result is empty, unset the var entirely.
if [ -n "${LD_LIBRARY_PATH:-}" ]; then
    _gev_new=
    # Reset IFS to ':' inside a subshell-free loop; restore afterwards.
    _gev_oldifs=$IFS
    IFS=:
    for _gev_p in $LD_LIBRARY_PATH; do
        # skip empty fragments
        [ -n "$_gev_p" ] || continue
        case $_gev_p in
            *anaconda*|*miniconda*|*miniforge*|*mambaforge*|*/conda/*|*/conda|*conda3*)
                ;;  # drop conda-flavoured entry
            *)
                if [ -z "$_gev_new" ]; then
                    _gev_new=$_gev_p
                else
                    _gev_new=$_gev_new:$_gev_p
                fi
                ;;
        esac
    done
    IFS=$_gev_oldifs
    if [ -n "$_gev_new" ]; then
        LD_LIBRARY_PATH=$_gev_new
        export LD_LIBRARY_PATH
    else
        unset LD_LIBRARY_PATH
    fi
    unset _gev_new _gev_oldifs _gev_p
fi

# --- 2. UV --------------------------------------------------------------------
# Prefer the known absolute path; fall back to whatever is on PATH.
if [ -x /home/kita/.local/bin/uv ]; then
    UV=/home/kita/.local/bin/uv
else
    UV=$(command -v uv 2>/dev/null || true)
fi
export UV

# --- 3. HuggingFace cache on the big disk -------------------------------------
HF_HOME=${HF_HOME:-/home/kita/.cache/huggingface}
export HF_HOME
# Best-effort: ensure it exists (ignore failure; do not abort sourcing).
[ -d "$HF_HOME" ] || mkdir -p "$HF_HOME" 2>/dev/null || true

# --- 4. PyTorch allocator -----------------------------------------------------
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# --- 5. one-line confirmation to stderr --------------------------------------
printf 'env.sh: LD_LIBRARY_PATH=%s UV=%s HF_HOME=%s PYTORCH_CUDA_ALLOC_CONF=%s\n' \
    "${LD_LIBRARY_PATH:-<unset>}" "${UV:-<none>}" "$HF_HOME" "$PYTORCH_CUDA_ALLOC_CONF" >&2
