#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless", "numpy"]
# ///
"""Per-frame face blur for a video, robust to CLOSE-UP faces.

Two-pass, temporally-smoothed pipeline (fixes "face too big -> not blurred /
not fully covered" on near frames):

  Pass 1  detect on every frame; keep the LARGEST plausible face per frame
          (ignores small spurious boxes - ears, neck, background faces).
  Fill    interpolate the box across frames where the main face dropped or the
          detection jittered to an implausibly small box (size outlier vs the
          temporal median) -> the "borrow from neighbouring frames" the user
          asked for.
  Smooth  moving-average the box center+size to kill per-frame jitter.
  Grow    expand the box more when the face is large (close-up): YuNet's box
          only covers the inner face, so near the camera the hair/jaw/forehead
          would otherwise stick out. expand scales with face size.
  Pass 2  blur each frame at the resolved box (bbox-shaped feathered ellipse,
          strength 0.4 default), then mux original audio back with ffmpeg.

If a face is bigger than --maxcover of the frame it is treated as "fills the
frame" and the blur is clamped to the whole frame area so nothing leaks.
"""
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


def detect_largest(detector, bgr, W, H):
    """Return (cx, cy, w, h, score) of the largest face, trying descending
    thresholds; None if nothing at all."""
    for s in (0.6, 0.5, 0.4, 0.3, 0.2):
        detector.setInputSize((W, H))
        detector.setScoreThreshold(float(s))
        _, faces = detector.detect(bgr)
        if faces is not None and len(faces):
            f = max(faces, key=lambda r: r[2] * r[3])
            x, y, w, h = float(f[0]), float(f[1]), float(f[2]), float(f[3])
            return np.array([x + w / 2, y + h / 2, w, h, float(f[14])])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mode", choices=["blur", "pixelate"], default="blur")
    ap.add_argument("--strength", type=float, default=0.4)
    ap.add_argument("--expand", type=float, default=0.35,
                    help="base box expansion each side; grows with face size")
    ap.add_argument("--smooth", type=int, default=5,
                    help="moving-average window (frames) for box center+size")
    ap.add_argument("--maxcover", type=float, default=0.55,
                    help="if face area-fraction exceeds this, clamp blur to full frame")
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.inp)
    if not cap.isOpened():
        log(f"ERROR: cannot open {a.inp}")
        return 2
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    det = cv2.FaceDetectorYN.create(a.model, "", (W, H))

    # ---- Pass 1: read all frames + detect largest face -------------------
    frames = []
    raw = []   # per-frame [cx,cy,w,h,score] or None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
        raw.append(detect_largest(det, f, W, H))
    cap.release()
    n = len(frames)
    if n == 0:
        log("ERROR: no frames")
        return 2

    # ---- Reject size outliers (spurious tiny box on close-up frames) -----
    sizes = np.array([(r[2] + r[3]) if r is not None else np.nan for r in raw])
    valid = sizes[~np.isnan(sizes)]
    med = float(np.median(valid)) if len(valid) else 0.0
    # a detection whose size is < 40% of the local median is likely the
    # small-spurious-box jitter -> drop it so interpolation fills from neighbours
    for i, r in enumerate(raw):
        if r is None:
            continue
        lo = max(0, i - 7); hi = min(n, i + 8)
        local = [sizes[j] for j in range(lo, hi) if not np.isnan(sizes[j])]
        if local:
            lmed = float(np.median(local))
            if (r[2] + r[3]) < 0.45 * lmed:
                raw[i] = None  # treat as miss; will be interpolated

    # ---- Interpolate boxes over missing frames (borrow from neighbours) --
    idx = [i for i, r in enumerate(raw) if r is not None]
    if not idx:
        log("ERROR: no usable face detections in any frame")
        return 3
    boxes = np.zeros((n, 4))  # cx,cy,w,h
    arr = np.array([raw[i][:4] for i in idx])
    for c in range(4):
        boxes[:, c] = np.interp(np.arange(n), idx, arr[:, c])

    # ---- Temporal smoothing (moving average) -----------------------------
    if a.smooth > 1:
        k = a.smooth
        pad = k // 2
        sm = np.zeros_like(boxes)
        for c in range(4):
            padded = np.pad(boxes[:, c], (pad, pad), mode="edge")
            sm[:, c] = np.convolve(padded, np.ones(k) / k, mode="valid")[:n]
        boxes = sm

    # ---- Pass 2: blur each frame -----------------------------------------
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    for i in range(n):
        f = frames[i]
        cx, cy, w, h = boxes[i]
        # dynamic expand: bigger faces need more (cover hair/jaw/forehead)
        frac = (w * h) / (W * H)
        grow = a.expand + min(0.6, frac * 1.2)   # up to ~+0.6 on big faces
        ex, ey = w * grow, h * grow
        x0 = int(cx - w / 2 - ex); y0 = int(cy - h / 2 - ey)
        x1 = int(cx + w / 2 + ex); y1 = int(cy + h / 2 + ey)
        # if the face essentially fills the frame, blur the whole frame
        if frac >= a.maxcover:
            x0, y0, x1, y1 = 0, 0, W, H
        x0 = max(0, x0); y0 = max(0, y0); x1 = min(W, x1); y1 = min(H, y1)
        bw, bh = x1 - x0, y1 - y0
        if bw < 8 or bh < 8:
            vw.write(f); continue
        roi = f[y0:y1, x0:x1]
        if a.mode == "pixelate":
            blocks = max(6, int(12 / max(a.strength, 0.1)))
            small = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)
            proc = cv2.resize(small, (bw, bh), interpolation=cv2.INTER_NEAREST)
        else:
            kk = int(max(bw, bh) * 0.6 * a.strength)
            kk = max(11, kk | 1)
            proc = cv2.GaussianBlur(roi, (kk, kk), 0)
        if x0 == 0 and y0 == 0 and x1 == W and y1 == H:
            f[:] = proc  # full-frame, no feather needed
        else:
            mask = np.zeros((bh, bw), np.float32)
            cv2.ellipse(mask, (bw // 2, bh // 2), (int(bw * 0.5), int(bh * 0.5)),
                        0, 0, 360, 1.0, -1)
            feather = int(max(bw, bh) * 0.12) | 1
            mask = cv2.GaussianBlur(mask, (feather, feather), 0)
            m3 = mask[:, :, None]
            f[y0:y1, x0:x1] = (proc * m3 + roi * (1 - m3)).astype(np.uint8)
        vw.write(f)
    vw.release()
    nmiss = sum(1 for r in raw if r is None)
    log(f"resolved boxes for all {n} frames "
        f"({nmiss} interpolated from neighbours); muxing audio ...")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", a.inp,
           "-map", "0:v:0", "-map", "1:a:0?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-c:a", "copy", "-shortest", a.out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log("ffmpeg mux failed; video-only re-encode")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", a.out],
                       check=True)
    os.unlink(tmp)
    log(f"saved -> {a.out}")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
