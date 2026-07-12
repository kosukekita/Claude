#!/usr/bin/env python3
"""Validate video-media-studio storyboard one-shot invariants.

1 storyboard txt = 1 continuous shot = 1 i2v clip.
Usage: check_storyboards.py <dir-or-txt> [...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_KEYS = {
    "storyboard_id",
    "shot_id",
    "clip_id",
    "model",
    "duration_sec",
    "start_keyframe",
    "end_keyframe",
    "continuity",
    "cut_count",
    "scene_changes",
    "time_jumps",
    "camera",
    "content",
}

NAME_RE = re.compile(r"^storyboard_[a-z0-9][a-z0-9_]*_\d{3}$")
MULTI_MARKER_RE = re.compile(
    r"\b(C[1-9]\d*|cut\s*[1-9]\d*|shot\s*[1-9]\d*|clip\s*[1-9]\d*)\b",
    re.IGNORECASE,
)
BOUNDARY_WORD_RE = re.compile(
    r"(scene\s*change|time\s*jump|montage|hard\s*cut|smash\s*cut|jump\s*cut|"
    r"別カット|場面転換|時間ジャンプ|カット切替|カットが入る|複数カット|3行|三行)",
    re.IGNORECASE,
)


def parse_kv(text: str) -> tuple[dict[str, str], dict[str, int]]:
    values: dict[str, str] = {}
    counts: dict[str, int] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        counts[key] = counts.get(key, 0) + 1
        values.setdefault(key, value)
    return values, counts


def duration_range(model: str) -> tuple[float, float] | None:
    normalized = model.lower().replace("-", "_")
    if "kling" in normalized:
        return 3.0, 15.0
    if "seedance" in normalized:
        return 4.0, 15.0
    return None


def resolve_relative(txt_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (txt_path.parent / path).resolve()


def validate_file(txt_path: Path) -> list[str]:
    errors: list[str] = []
    text = txt_path.read_text(encoding="utf-8")
    values, counts = parse_kv(text)
    stem = txt_path.stem

    if not NAME_RE.match(stem):
        errors.append(f"filename must match storyboard_<shot>_NNN: {txt_path.name}")

    missing = sorted(REQUIRED_KEYS - values.keys())
    if missing:
        errors.append(f"missing required keys: {', '.join(missing)}")

    for key in ("storyboard_id", "shot_id", "clip_id", "duration_sec", "start_keyframe", "end_keyframe"):
        if counts.get(key, 0) > 1:
            errors.append(f"{key} appears {counts[key]} times; only one clip per txt is allowed")

    if values.get("storyboard_id") and values["storyboard_id"] != stem:
        errors.append(f"storyboard_id must equal filename stem ({stem})")

    if not txt_path.with_suffix(".png").exists():
        errors.append(f"matching PNG not found: {txt_path.with_suffix('.png').name}")

    if values.get("continuity") and values["continuity"] != "single_continuous_shot":
        errors.append("continuity must be single_continuous_shot")

    if values.get("cut_count") and values["cut_count"] != "0":
        errors.append("cut_count must be 0")

    for key in ("scene_changes", "time_jumps"):
        if values.get(key) and values[key].lower() != "none":
            errors.append(f"{key} must be none")

    if values.get("duration_sec"):
        try:
            duration = float(values["duration_sec"])
        except ValueError:
            errors.append("duration_sec must be a number")
        else:
            rng = duration_range(values.get("model", ""))
            if rng and not (rng[0] <= duration <= rng[1]):
                errors.append(f"duration_sec {duration:g} outside {values.get('model')} range {rng[0]:g}-{rng[1]:g}s")

    start = values.get("start_keyframe")
    end = values.get("end_keyframe")
    if start and end and start == end:
        errors.append("start_keyframe and end_keyframe must be different files")
    for key in ("start_keyframe", "end_keyframe"):
        if values.get(key) and not resolve_relative(txt_path, values[key]).exists():
            errors.append(f"{key} does not exist: {values[key]}")

    marker_count = len(MULTI_MARKER_RE.findall(text))
    if marker_count > 1:
        errors.append("multiple cut/shot/clip markers found; split into separate storyboard txt files")

    if BOUNDARY_WORD_RE.search(text):
        errors.append("shot-boundary wording found; split this storyboard before approval")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check storyboard txt files enforce 1 board = 1 continuous i2v clip.")
    parser.add_argument("paths", nargs="+", help="Storyboard txt files or directories containing storyboard_*.txt")
    args = parser.parse_args()

    txt_files: list[Path] = []
    for raw in args.paths:
        path = Path(raw)
        if path.is_dir():
            txt_files.extend(sorted(path.rglob("storyboard_*.txt")))
        elif path.is_file():
            txt_files.append(path)
        else:
            print(f"ERROR: path not found: {path}", file=sys.stderr)
            return 2

    if not txt_files:
        print("ERROR: no storyboard_*.txt files found", file=sys.stderr)
        return 2

    failed = False
    for txt_path in txt_files:
        errors = validate_file(txt_path)
        if errors:
            failed = True
            print(f"FAIL {txt_path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {txt_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
