#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless", "numpy"]
# ///
"""Detect faces with YuNet and blur ONLY the face region (elliptical, feathered).
Falls back to a lowered score threshold if no face is found at the strict one
(useful for profile / partially-cropped faces). Prints how many faces blurred."""
from __future__ import annotations
import argparse
import os
import sys
import cv2
import numpy as np

MODEL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models", "face_detection_yunet_2023mar.onnx",
)
# face_blur.py lives in scratchpad; the model is in the skill dir. Allow override.
DEFAULT_MODEL = "/home/kita/.claude/skills/video-media-studio/scripts/models/face_detection_yunet_2023mar.onnx"


def log(m):
    print(m, file=sys.stderr, flush=True)


def detect(detector, bgr, score_min):
    h, w = bgr.shape[:2]
    detector.setInputSize((w, h))
    detector.setScoreThreshold(float(score_min))
    _, faces = detector.detect(bgr)
    return faces if faces is not None else np.empty((0, 15), np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mode", choices=["blur", "pixelate"], default="blur")
    ap.add_argument("--strength", type=float, default=0.4,
                    help="blur strength multiplier (bigger = stronger); "
                         "user default 0.4 = 'very weak' (face hinted but anonymized)")
    ap.add_argument("--expand", type=float, default=0.35,
                    help="grow the detected box by this fraction on each side")
    ap.add_argument("--score", type=float, default=0.6)
    ap.add_argument("--debug-box", action="store_true",
                    help="also draw the detection box (for verification)")
    a = ap.parse_args()

    img = cv2.imread(a.inp)
    if img is None:
        log(f"ERROR: cannot read {a.inp}")
        return 2
    H, W = img.shape[:2]

    det = cv2.FaceDetectorYN.create(a.model, "", (W, H))
    faces = detect(det, img, a.score)
    if len(faces) == 0:
        for s in (0.5, 0.4, 0.3):
            faces = detect(det, img, s)
            if len(faces):
                log(f"found at lowered score {s}")
                break
    if len(faces) == 0:
        log("WARNING: no face detected; writing copy unchanged")
        cv2.imwrite(a.out, img)
        return 3

    out = img.copy()
    n = 0
    for f in faces:
        x, y, fw, fh = f[0], f[1], f[2], f[3]
        # expand box
        ex, ey = fw * a.expand, fh * a.expand
        x0 = max(0, int(x - ex)); y0 = max(0, int(y - ey))
        x1 = min(W, int(x + fw + ex)); y1 = min(H, int(y + fh + ey))
        bw, bh = x1 - x0, y1 - y0
        if bw < 8 or bh < 8:
            continue
        roi = out[y0:y1, x0:x1]

        if a.mode == "pixelate":
            blocks = max(6, int(12 / max(a.strength, 0.1)))
            small = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)
            proc = cv2.resize(small, (bw, bh), interpolation=cv2.INTER_NEAREST)
        else:
            k = int(max(bw, bh) * 0.6 * a.strength)
            k = max(11, k | 1)  # odd
            proc = cv2.GaussianBlur(roi, (k, k), 0)

        # feathered elliptical mask matching the bbox shape (no hard rectangle).
        mask = np.zeros((bh, bw), np.float32)
        cv2.ellipse(mask, (bw // 2, bh // 2), (int(bw * 0.5), int(bh * 0.5)),
                    0, 0, 360, 1.0, -1)
        feather = int(max(bw, bh) * 0.12) | 1
        mask = cv2.GaussianBlur(mask, (feather, feather), 0)
        mask3 = mask[:, :, None]
        out[y0:y1, x0:x1] = (proc * mask3 + roi * (1 - mask3)).astype(np.uint8)
        if a.debug_box:
            cv2.rectangle(out, (x0, y0), (x1, y1), (0, 255, 0), 2)
        n += 1

    cv2.imwrite(a.out, out)
    log(f"blurred {n} face(s) -> {a.out}")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
