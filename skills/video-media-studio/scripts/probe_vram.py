#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
probe_vram.py — query per-GPU VRAM and recommend a backend tier.

This is the heart of backend auto-selection for the video-media-studio skill.
It shells out to `nvidia-smi` (no Python GPU libraries needed), reads free/total
VRAM for every visible GPU, prints a JSON summary, and — given --required-mb —
picks a backend tier and the GPU index to use.

Decision ladder (simple, auditable, LOCAL-FIRST):

    required_mb * margin  <=  max single-GPU free        -> local-single
    required_mb * margin  <=  total free across all GPUs  -> local-offload
                                                  otherwise -> cloud

  * local-single : the whole job fits on ONE card with the safety margin.
                   We pick the GPU with the MOST free VRAM and print its index.
  * local-offload: it does not fit one card, but the rig has enough aggregate
                   free VRAM that CPU/sequential offload (or splitting across
                   cards) is plausible. The "chosen GPU" is still the single
                   freest card (the primary device offload pins to).
  * cloud        : not enough local VRAM anywhere -> fall back to a hosted/Grok
                   backend. chosen GPU is null.

If --required-mb is omitted the script only prints the VRAM summary (exit 0)
and does NOT recommend a tier — useful for "just tell me what's free".

ROBUSTNESS: if nvidia-smi is missing, not executable, times out, or returns
no parseable GPUs, the script does NOT crash. The summary reports zero GPUs,
and (when --required-mb is given) the recommended tier is `cloud` with a clear
reason — because no usable local VRAM was detected. Exit code is 0 in every
normal path so callers can rely on parsing stdout JSON; genuine usage errors
(bad arguments) exit 2 via argparse.

OUTPUT CONTRACT (stdout = machine-readable JSON, stderr = human log):
  {
    "gpus": [ {"index": 0, "name": "...", "free_mb": N, "total_mb": N,
               "used_mb": N, "utilization_pct": N|null}, ... ],
    "gpu_count": N,
    "max_free_mb": N,            # largest single-GPU free VRAM (0 if none)
    "total_free_mb": N,         # sum of free across all GPUs
    "total_total_mb": N,        # sum of total across all GPUs
    "nvidia_smi_available": true|false,
    "error": null|"<reason>",   # populated when nvidia-smi unusable

    # the following keys appear ONLY when --required-mb was provided:
    "required_mb": N,
    "margin": F,
    "effective_required_mb": N, # required_mb * margin, rounded up
    "task": "<str>"|null,
    "backend": "local-single"|"local-offload"|"cloud",
    "gpu_index": N|null,        # chosen GPU for local tiers, null for cloud
    "reason": "<why this tier>"
  }
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys


# nvidia-smi fields we request, in order. utilization is optional/best-effort.
_QUERY_FIELDS = ["index", "memory.free", "memory.total", "memory.used", "name", "utilization.gpu"]


def _eprint(*args: object) -> None:
    """Human-readable log goes to stderr so stdout stays pure JSON."""
    print(*args, file=sys.stderr)


def query_gpus(timeout: float = 8.0):
    """Return (gpus, error). gpus is a list of dicts; error is None on success.

    Never raises for environmental problems (missing binary, non-zero exit,
    timeout, garbage output) — those become a non-None error string with an
    empty gpu list, so callers degrade gracefully to the cloud tier.
    """
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return [], "nvidia-smi not found on PATH"

    cmd = [
        exe,
        "--query-gpu=" + ",".join(_QUERY_FIELDS),
        "--format=csv,noheader,nounits",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return [], f"nvidia-smi timed out after {timeout}s"
    except OSError as exc:  # e.g. not executable, driver mismatch
        return [], f"nvidia-smi could not be executed: {exc}"

    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip().splitlines()
        detail = msg[0] if msg else f"exit code {proc.returncode}"
        return [], f"nvidia-smi failed ({detail})"

    gpus = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 5:  # need at least index,free,total,used,name
            continue
        try:
            idx = int(parts[0])
            free_mb = int(float(parts[1]))
            total_mb = int(float(parts[2]))
            used_mb = int(float(parts[3]))
        except (ValueError, IndexError):
            continue  # skip unparseable row, keep the rest
        name = parts[4] if len(parts) > 4 else "unknown"
        util = None
        if len(parts) > 5:
            try:
                util = int(float(parts[5]))
            except ValueError:
                util = None  # e.g. "[N/A]" on some virtual GPUs
        gpus.append(
            {
                "index": idx,
                "name": name,
                "free_mb": free_mb,
                "total_mb": total_mb,
                "used_mb": used_mb,
                "utilization_pct": util,
            }
        )

    if not gpus:
        return [], "nvidia-smi returned no parseable GPUs"
    return gpus, None


def build_summary(gpus, error):
    free_vals = [g["free_mb"] for g in gpus]
    total_vals = [g["total_mb"] for g in gpus]
    return {
        "gpus": gpus,
        "gpu_count": len(gpus),
        "max_free_mb": max(free_vals) if free_vals else 0,
        "total_free_mb": sum(free_vals),
        "total_total_mb": sum(total_vals),
        "nvidia_smi_available": error is None,
        "error": error,
    }


def freest_gpu_index(gpus):
    """Index of the GPU with the most free VRAM (None if no GPUs)."""
    if not gpus:
        return None
    # max by free_mb; tie-break on lowest index for determinism
    best = max(gpus, key=lambda g: (g["free_mb"], -g["index"]))
    return best["index"]


def recommend(summary, gpus, required_mb, margin, task):
    """Return (backend, gpu_index, reason)."""
    effective = math.ceil(required_mb * margin)
    summary["required_mb"] = required_mb
    summary["margin"] = margin
    summary["effective_required_mb"] = effective
    summary["task"] = task

    max_free = summary["max_free_mb"]
    total_free = summary["total_free_mb"]
    chosen = freest_gpu_index(gpus)

    if summary["error"] is not None or not gpus:
        backend = "cloud"
        gpu_index = None
        reason = (
            f"No usable local GPU detected ({summary['error']}); "
            f"need {effective} MB -> cloud."
        )
    elif effective <= max_free:
        backend = "local-single"
        gpu_index = chosen
        reason = (
            f"GPU {gpu_index} has {max_free} MB free >= {effective} MB "
            f"(required {required_mb} x margin {margin}); fits one card."
        )
    elif effective <= total_free:
        backend = "local-offload"
        gpu_index = chosen
        reason = (
            f"No single card fits {effective} MB (max free {max_free} MB), "
            f"but total free {total_free} MB across {len(gpus)} GPU(s) does; "
            f"use CPU/sequential offload on GPU {gpu_index}."
        )
    else:
        backend = "cloud"
        gpu_index = None
        reason = (
            f"Need {effective} MB but only {total_free} MB free total "
            f"(max single {max_free} MB); fall back to cloud."
        )

    summary["backend"] = backend
    summary["gpu_index"] = gpu_index
    summary["reason"] = reason
    return backend, gpu_index, reason


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="probe_vram.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Query per-GPU free/total VRAM via nvidia-smi and (optionally) "
            "recommend a backend tier for a job of a given VRAM size.\n\n"
            "Backend tiers (LOCAL-FIRST ladder):\n"
            "  local-single   job fits one GPU with the safety margin\n"
            "  local-offload  fits only across all GPUs' aggregate free VRAM\n"
            "                 (CPU/sequential offload on the freest card)\n"
            "  cloud          not enough local VRAM -> hosted/Grok fallback\n\n"
            "Robust to nvidia-smi being missing: reports 0 GPUs and, when a\n"
            "requirement is given, recommends the 'cloud' tier. Always exits 0\n"
            "on normal runs so callers can parse the stdout JSON."
        ),
        epilog=(
            "Examples:\n"
            "  # Just show what's free (no recommendation):\n"
            "  probe_vram.py\n\n"
            "  # Recommend a tier for a 40 GB (40960 MB) model:\n"
            "  probe_vram.py --required-mb 40960 --task i2v\n\n"
            "  # Tighter safety margin and a custom timeout:\n"
            "  probe_vram.py --required-mb 24000 --margin 1.05 --timeout 5\n\n"
            "  # Pipe the chosen GPU index into a generator:\n"
            "  IDX=$(probe_vram.py --required-mb 16000 | "
            "python3 -c 'import sys,json;print(json.load(sys.stdin)[\"gpu_index\"])')\n"
        ),
    )
    parser.add_argument(
        "--required-mb",
        type=int,
        default=None,
        metavar="MB",
        help=(
            "Peak VRAM the job needs, in MB. If given, the script recommends a "
            "backend tier and a GPU index. If omitted, only the VRAM summary is "
            "printed."
        ),
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        metavar="NAME",
        help=(
            "Optional free-form task label (e.g. t2v / i2v / t2i / edit) echoed "
            "into the JSON and the human log for traceability. Does not change "
            "the math."
        ),
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=1.1,
        metavar="F",
        help=(
            "Safety multiplier applied to --required-mb to guard against "
            "text-encoder / activation VRAM spikes (default: 1.1 = +10%%)."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=8.0,
        metavar="SEC",
        help="Seconds to wait for nvidia-smi before giving up (default: 8).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON (indented) instead of one compact line.",
    )
    args = parser.parse_args(argv)

    if args.required_mb is not None and args.required_mb <= 0:
        parser.error("--required-mb must be a positive integer (MB)")
    if args.margin <= 0:
        parser.error("--margin must be > 0")

    gpus, error = query_gpus(timeout=args.timeout)
    summary = build_summary(gpus, error)

    # Human log to stderr (the WHY), JSON to stdout (the WHAT).
    if error is not None:
        _eprint(f"[probe_vram] WARNING: {error}")
    else:
        _eprint(
            f"[probe_vram] {summary['gpu_count']} GPU(s); "
            f"max free {summary['max_free_mb']} MB, "
            f"total free {summary['total_free_mb']} MB"
        )
        for g in gpus:
            util = "n/a" if g["utilization_pct"] is None else f"{g['utilization_pct']}%"
            _eprint(
                f"  GPU {g['index']}: {g['name']} — "
                f"{g['free_mb']}/{g['total_mb']} MB free (util {util})"
            )

    if args.required_mb is not None:
        backend, gpu_index, reason = recommend(
            summary, gpus, args.required_mb, args.margin, args.task
        )
        tag = f" [task={args.task}]" if args.task else ""
        _eprint(f"[probe_vram] DECISION{tag}: backend={backend} "
                f"gpu={gpu_index} — {reason}")

    indent = 2 if args.pretty else None
    print(json.dumps(summary, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
