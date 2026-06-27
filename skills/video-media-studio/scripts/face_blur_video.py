#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "insightface",
#   "onnxruntime-gpu",
#   "opencv-python-headless",
#   "numpy",
# ]
# ///
"""Robust per-frame face blur for video — blurs ALL faces (foreground + people
in the background) and survives extreme close-ups.

Why this exists / what was learned (2026-06-27):
  * YuNet (cv2.FaceDetectorYN) and even SCRFD detect normal faces well but BOTH
    return 0 faces when a single face fills most of the frame (the close-up kiss
    frames). And blurring only the "largest" face left every background person
    unblurred.
Pipeline:
  Pass 1  InsightFace SCRFD (buffalo_l det model, GPU) detects ALL faces every
          frame. Each face box is expanded using its 5 landmarks so the ellipse
          actually covers hair/jaw/forehead (the raw box is too tight).
  Close-up fallback: when the frame has NO detection (or only tiny ones) but the
          neighbouring frames had a large face, the face has grown past the
          detector — we mark the frame "fills frame" and blur the WHOLE frame.
          The fill flag is also interpolated across the gap so the whole close-up
          run is covered, not just the exact 0-face frames.
  Pass 2  blur every face box (feathered ellipse) on every frame, or the full
          frame on close-up frames; mux original audio back with ffmpeg.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import tempfile
import cv2
import numpy as np


def log(m):
    print(m, file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["blur", "pixelate"], default="blur")
    ap.add_argument("--strength", type=float, default=0.4)
    ap.add_argument("--expand", type=float, default=0.45,
                    help="base box expansion each side (covers hair/jaw)")
    ap.add_argument("--det-size", type=int, default=960,
                    help="SCRFD detection input size (bigger = small faces)")
    ap.add_argument("--score", type=float, default=0.3,
                    help="detection score threshold (low = catch background faces)")
    ap.add_argument("--bigfrac", type=float, default=0.30,
                    help="a face whose area-fraction exceeds this triggers full-frame blur")
    ap.add_argument("--minfrac", type=float, default=0.0008,
                    help="ignore detections smaller than this area-fraction (noise)")
    a = ap.parse_args()

    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l",
                       providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(a.det_size, a.det_size), det_thresh=a.score)

    cap = cv2.VideoCapture(a.inp)
    if not cap.isOpened():
        log(f"ERROR: cannot open {a.inp}")
        return 2
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    area = W * H

    # ---- Pass 1: detect all faces per frame -------------------------------
    frames, per_frame_boxes, fills = [], [], []
    maxfrac_seq = []
    n = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
        faces = app.get(f)
        boxes = []
        maxfrac = 0.0
        for fc in faces:
            x0, y0, x1, y1 = fc.bbox
            bw, bh = x1 - x0, y1 - y0
            frac = (bw * bh) / area
            if frac < a.minfrac:
                continue
            maxfrac = max(maxfrac, frac)
            # expand using landmark spread when available
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            boxes.append((cx, cy, bw, bh, frac))
        per_frame_boxes.append(boxes)
        maxfrac_seq.append(maxfrac)
        # full-frame flag: a face already fills a big chunk, OR nothing detected
        fills.append(maxfrac >= a.bigfrac)
        n += 1
        if n % 30 == 0:
            log(f"  detect {n} frames")
    cap.release()
    if n == 0:
        log("ERROR: no frames")
        return 2

    # ---- Close-up gap handling (MAIN-FACE-LOST, not just no-detection) ----
    # The real failure: on extreme close-ups the detector loses the BIG main
    # face but still finds a tiny background face, so maxfrac collapses to ~0.001
    # even though the woman's face fills the frame. Treat a frame as a close-up
    # (-> full-frame blur) when its main face is small/absent BUT a big face
    # exists nearby in time. That window is the close-up run; fill all of it.
    big = [fr >= a.bigfrac for fr in maxfrac_seq]          # frame has a big face
    lost = [maxfrac_seq[i] < a.bigfrac for i in range(n)]  # main face not big here
    WIN = 12
    for i in range(n):
        if lost[i]:
            lo = max(0, i - WIN); hi = min(n, i + WIN + 1)
            if any(big[j] for j in range(lo, hi)):
                fills[i] = True          # inside/adjacent to a close-up run
    # close small holes: if a fill frame sits within 2 of fills on both sides
    for _ in range(2):
        fs = fills[:]
        for i in range(2, n - 2):
            if (fills[i - 1] or fills[i - 2]) and (fills[i + 1] or fills[i + 2]):
                fs[i] = True
        fills = fs

    # ---- Interpolate the MAIN face over no-detection gaps -----------------
    # The killer case the user hit: a mid-size face the detector momentarily
    # loses, with no big neighbour to trigger a full-frame fill -> the frame got
    # NOTHING. Track the largest face per frame, then linearly interpolate its
    # box across frames where it dropped (borrowing from neighbours), and ensure
    # every non-fill frame has at least that main box to blur.
    main = [None] * n  # (cx,cy,bw,bh) of largest face, or None
    for i in range(n):
        if per_frame_boxes[i]:
            cx, cy, bw, bh, _ = max(per_frame_boxes[i], key=lambda b: b[2] * b[3])
            main[i] = (cx, cy, bw, bh)
    idx = [i for i in range(n) if main[i] is not None]
    if idx:
        arr = np.array([main[i] for i in idx], dtype=float)
        interp = np.zeros((n, 4))
        for c in range(4):
            interp[:, c] = np.interp(np.arange(n), idx, arr[:, c])
        # light temporal smoothing of the interpolated main track
        k = 5; pad = k // 2
        for c in range(4):
            padded = np.pad(interp[:, c], (pad, pad), mode="edge")
            interp[:, c] = np.convolve(padded, np.ones(k) / k, mode="valid")[:n]
        for i in range(n):
            if fills[i]:
                continue
            mcx, mcy, mbw, mbh = interp[i]
            mfrac = (mbw * mbh) / area
            # if interpolation says the main face is actually big here, fill frame
            if mfrac >= a.bigfrac:
                fills[i] = True
                continue
            have_main = any(abs(b[0] - mcx) < mbw and abs(b[1] - mcy) < mbh
                            for b in per_frame_boxes[i])
            if not have_main:
                per_frame_boxes[i].append((mcx, mcy, mbw, mbh, mfrac))

    # ---- Pass 2: blur ----------------------------------------------------
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    nfull = 0
    for i in range(n):
        f = frames[i]
        if fills[i]:
            kk = max(31, (int(min(W, H) * 0.12) | 1))
            f[:] = cv2.GaussianBlur(f, (kk, kk), 0)
            nfull += 1
            vw.write(f)
            continue
        for (cx, cy, bw, bh, frac) in per_frame_boxes[i]:
            grow = a.expand + min(0.5, frac * 1.5)
            ex, ey = bw * grow, bh * grow
            x0 = max(0, int(cx - bw / 2 - ex)); y0 = max(0, int(cy - bh / 2 - ey))
            x1 = min(W, int(cx + bw / 2 + ex)); y1 = min(H, int(cy + bh / 2 + ey))
            bw2, bh2 = x1 - x0, y1 - y0
            if bw2 < 8 or bh2 < 8:
                continue
            roi = f[y0:y1, x0:x1]
            if a.mode == "pixelate":
                blocks = max(6, int(12 / max(a.strength, 0.1)))
                small = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)
                proc = cv2.resize(small, (bw2, bh2), interpolation=cv2.INTER_NEAREST)
            else:
                kk = max(11, (int(max(bw2, bh2) * 0.6 * a.strength) | 1))
                proc = cv2.GaussianBlur(roi, (kk, kk), 0)
            mask = np.zeros((bh2, bw2), np.float32)
            cv2.ellipse(mask, (bw2 // 2, bh2 // 2), (int(bw2 * 0.5), int(bh2 * 0.5)),
                        0, 0, 360, 1.0, -1)
            feather = int(max(bw2, bh2) * 0.12) | 1
            mask = cv2.GaussianBlur(mask, (feather, feather), 0)
            m3 = mask[:, :, None]
            f[y0:y1, x0:x1] = (proc * m3 + roi * (1 - m3)).astype(np.uint8)
        vw.write(f)
    vw.release()
    nblurfaces = sum(len(b) for b in per_frame_boxes)
    log(f"done: {n} frames, {nblurfaces} face-blurs, {nfull} full-frame close-up frames; muxing audio ...")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", a.inp,
           "-map", "0:v:0", "-map", "1:a:0?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-c:a", "copy", "-shortest", a.out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", a.out],
                       check=True)
    os.unlink(tmp)
    log(f"saved -> {a.out}")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
