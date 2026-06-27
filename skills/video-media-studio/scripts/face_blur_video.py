#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless", "numpy"]
# ///
"""Per-frame face blur for a video: detect faces with YuNet on every frame and
blur ONLY the face region (bbox-shaped feathered ellipse), matching the still
face_blur.py defaults (strength 0.4). Audio from the source is muxed back with
ffmpeg. To reduce flicker on frames where detection drops, the last good box is
reused for a few frames (--hold)."""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import tempfile
import cv2
import numpy as np

DEFAULT_MODEL = "/home/kita/.claude/skills/video-media-studio/scripts/models/face_detection_yunet_2023mar.onnx"


def log(m):
    print(m, file=sys.stderr, flush=True)


def detect(detector, bgr, score_min):
    h, w = bgr.shape[:2]
    detector.setInputSize((w, h))
    detector.setScoreThreshold(float(score_min))
    _, faces = detector.detect(bgr)
    return faces if faces is not None else np.empty((0, 15), np.float32)


def blur_region(out, box, mode, strength, expand, W, H):
    x, y, fw, fh = box
    ex, ey = fw * expand, fh * expand
    x0 = max(0, int(x - ex)); y0 = max(0, int(y - ey))
    x1 = min(W, int(x + fw + ex)); y1 = min(H, int(y + fh + ey))
    bw, bh = x1 - x0, y1 - y0
    if bw < 8 or bh < 8:
        return
    roi = out[y0:y1, x0:x1]
    if mode == "pixelate":
        blocks = max(6, int(12 / max(strength, 0.1)))
        small = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)
        proc = cv2.resize(small, (bw, bh), interpolation=cv2.INTER_NEAREST)
    else:
        k = int(max(bw, bh) * 0.6 * strength)
        k = max(11, k | 1)
        proc = cv2.GaussianBlur(roi, (k, k), 0)
    mask = np.zeros((bh, bw), np.float32)
    cv2.ellipse(mask, (bw // 2, bh // 2), (int(bw * 0.5), int(bh * 0.5)), 0, 0, 360, 1.0, -1)
    feather = int(max(bw, bh) * 0.12) | 1
    mask = cv2.GaussianBlur(mask, (feather, feather), 0)
    m3 = mask[:, :, None]
    out[y0:y1, x0:x1] = (proc * m3 + roi * (1 - m3)).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mode", choices=["blur", "pixelate"], default="blur")
    ap.add_argument("--strength", type=float, default=0.4)
    ap.add_argument("--expand", type=float, default=0.35)
    ap.add_argument("--score", type=float, default=0.6)
    ap.add_argument("--hold", type=int, default=6,
                    help="reuse last good detection for up to N frames when detection drops")
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.inp)
    if not cap.isOpened():
        log(f"ERROR: cannot open {a.inp}")
        return 2
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    det = cv2.FaceDetectorYN.create(a.model, "", (W, H))

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(tmp, fourcc, fps, (W, H))

    prev_boxes = []           # last good detection(s)
    hold_left = 0
    n = blurred = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        faces = detect(det, frame, a.score)
        if len(faces) == 0:
            for s in (0.5, 0.4, 0.3):
                faces = detect(det, frame, s)
                if len(faces):
                    break
        boxes = [(f[0], f[1], f[2], f[3]) for f in faces]
        if boxes:
            prev_boxes = boxes
            hold_left = a.hold
        elif hold_left > 0 and prev_boxes:
            boxes = prev_boxes      # reuse to avoid flicker
            hold_left -= 1
        for b in boxes:
            blur_region(frame, b, a.mode, a.strength, a.expand, W, H)
        if boxes:
            blurred += 1
        vw.write(frame)
        if n % 30 == 0:
            log(f"  {n}/{total} frames")
    cap.release()
    vw.release()
    log(f"blurred faces in {blurred}/{n} frames; muxing audio ...")

    # mux original audio (if any) back onto the blurred video; re-encode to h264
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", tmp, "-i", a.inp,
        "-map", "0:v:0", "-map", "1:a:0?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-c:a", "copy", "-shortest", a.out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log("ffmpeg mux failed, falling back to video-only re-encode")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", a.out],
                       check=True)
    os.unlink(tmp)
    log(f"saved -> {a.out}")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
