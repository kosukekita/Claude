#!/usr/bin/env python3
"""Validate video-media-studio KEYFRAME-FILE invariants (per generation unit).

SCOPE: this validates the per-shot KEYFRAME FILES (storyboard_<shot>_NN.txt),
each of which is ONE continuous shot = 1 generation unit (no cut/scene-change/
time-jump; cut_count=0). It does NOT validate the whole-video TEXT storyboard,
which is a separate higher-level artifact and MAY contain multiple shots/cuts
(those are generated separately and ffmpeg-concatenated). See
reference/storyboard-shot-boundary.md (2026-07-12 header) for the two levels.

A continuous shot = 1+ CHAINED i2v clips. Keyframes are the clip boundaries:
adjacent keyframes = one i2v clip, so their time gap must be within the model's
generatable range (Kling 3-15s, Seedance 4-15s).
N keyframes = N-1 clips = min (N-1)*min_duration seconds.
(Finished video length is NOT capped at 15s: concatenate shots/clips, or use a
model's native long/extend feature.)

Usage: check_storyboards.py <dir-or-txt> [...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SCALAR_KEYS = {
    "storyboard_id",
    "shot_id",
    "model",
    "continuity",
    "cut_count",
    "scene_changes",
    "time_jumps",
    "camera",
    "content",
}

NAME_RE = re.compile(r"^storyboard_[a-z0-9][a-z0-9_]*_\d{3}$")
KF_RE = re.compile(r"^keyframe_(\d+)\s*:\s*(.*)$")
MULTI_MARKER_RE = re.compile(
    r"\b(C[1-9]\d*|cut\s*[1-9]\d*|shot\s*[1-9]\d*)\b", re.IGNORECASE
)
BOUNDARY_WORD_RE = re.compile(
    r"(scene\s*change|time\s*jump|montage|hard\s*cut|smash\s*cut|jump\s*cut|"
    r"別カット|場面転換|時間ジャンプ|カット切替|カットが入る|複数カット|3行|三行)",
    re.IGNORECASE,
)
MODEL_MIN_MAX = {"kling": (3.0, 15.0), "seedance": (4.0, 15.0)}


def model_range(model: str):
    m = model.lower().replace("-", "_")
    for name, rng in MODEL_MIN_MAX.items():
        if name in m:
            return rng
    return None


def parse(text: str):
    scalars: dict[str, str] = {}
    keyframes: dict[int, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        km = KF_RE.match(s)
        if km:
            keyframes[int(km.group(1))] = km.group(2).strip()
            continue
        if ":" in s:
            k, v = s.split(":", 1)
            scalars.setdefault(k.strip(), v.strip())
    return scalars, keyframes


def kv_pairs(rest: str) -> dict[str, str]:
    out = {}
    for tok in rest.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def validate_file(txt: Path) -> list[str]:
    errs: list[str] = []
    text = txt.read_text(encoding="utf-8")
    scalars, keyframes = parse(text)
    stem = txt.stem

    if not NAME_RE.match(stem):
        errs.append(f"filename must match storyboard_<shot>_NNN: {txt.name}")
    missing = sorted(SCALAR_KEYS - scalars.keys())
    if missing:
        errs.append(f"missing keys: {', '.join(missing)}")
    if scalars.get("storyboard_id") and scalars["storyboard_id"] != stem:
        errs.append(f"storyboard_id must equal filename stem ({stem})")
    if not txt.with_suffix(".png").exists():
        errs.append(f"matching PNG not found: {txt.with_suffix('.png').name}")
    if scalars.get("continuity") and scalars["continuity"] != "single_continuous_shot":
        errs.append("continuity must be single_continuous_shot")
    if scalars.get("cut_count") and scalars["cut_count"] != "0":
        errs.append("cut_count must be 0 (a cut/scene-change means a separate storyboard)")
    for k in ("scene_changes", "time_jumps"):
        if scalars.get(k) and scalars[k].lower() != "none":
            errs.append(f"{k} must be none")

    # keyframes: contiguous 0..N-1, >=2, each t_sec + img
    idxs = sorted(keyframes)
    if len(idxs) < 2:
        errs.append("need >=2 keyframes (at least start + end)")
    elif idxs != list(range(len(idxs))):
        errs.append(f"keyframe indices must be contiguous from 0; got {idxs}")

    rng = model_range(scalars.get("model", ""))
    times: list[float] = []
    imgs: list[str] = []
    for i in idxs:
        kv = kv_pairs(keyframes[i])
        if "t_sec" not in kv or "img" not in kv:
            errs.append(f"keyframe_{i} needs 't_sec=' and 'img='")
            continue
        try:
            times.append(float(kv["t_sec"]))
        except ValueError:
            errs.append(f"keyframe_{i} t_sec must be a number")
            times.append(float("nan"))
        img = kv["img"]
        imgs.append(img)
        p = Path(img) if Path(img).is_absolute() else (txt.parent / img)
        if not p.resolve().exists():
            errs.append(f"keyframe_{i} img missing: {img}")

    if len(imgs) != len(set(imgs)):
        errs.append("keyframe images must all be different files")

    # consecutive gaps = one i2v clip; must be within model range
    if len(times) >= 2 and all(t == t for t in times):  # no NaN
        if times[0] != 0:
            errs.append(f"keyframe_0 t_sec should be 0 (got {times[0]:g})")
        for i in range(len(times) - 1):
            gap = times[i + 1] - times[i]
            if gap <= 0:
                errs.append(f"keyframe times must strictly increase (clip {i}: {times[i]:g}->{times[i+1]:g})")
            elif rng and not (rng[0] <= gap <= rng[1]):
                errs.append(
                    f"clip {i} duration {gap:g}s (kf{i}->kf{i+1}) outside {scalars.get('model')} range {rng[0]:g}-{rng[1]:g}s"
                )

    if len(MULTI_MARKER_RE.findall(text)) > 1:
        errs.append("multiple cut/shot markers; a cut means a separate storyboard")
    if BOUNDARY_WORD_RE.search(text):
        errs.append("shot-boundary wording found; split this storyboard before approval")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description="Check storyboard = 1 continuous shot of chained i2v clips.")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.rglob("storyboard_*.txt")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"ERROR: not found: {p}", file=sys.stderr)
            return 2
    if not files:
        print("ERROR: no storyboard_*.txt found", file=sys.stderr)
        return 2
    failed = False
    for f in files:
        errs = validate_file(f)
        if errs:
            failed = True
            print(f"FAIL {f}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK   {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
