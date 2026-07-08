#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "insightface",
#   "onnxruntime-gpu",
#   "opencv-python-headless",
#   "numpy",
#   "pillow",
#   "imageio-ffmpeg",
# ]
# ///
"""compare_face_sim.py — face-identity A/B between a reference image and one or
more generated videos, using ArcFace embeddings (InsightFace buffalo_l).

Face-Sim (cosine similarity of ArcFace embeddings) is the standard identity
metric; SSIM is NOT (it collapses under lighting/pose changes). We sample N
frames from each video, detect+embed the largest face per frame, and report the
mean±SD cosine similarity to the reference face embedding, plus a side-by-side
tile for human eyeballing.

Use to decide whether HunyuanCustom actually beats the existing VACE r2v on face
identity for a given persona.

Output contract: WHY logs to stderr; JSON summary to stdout; tile PNG to --tile.

Usage:
  compare_face_sim.py --ref ref_face.png \
    --video hunyuan_shower.mp4 --video r2v_ayaka_nude.mp4 \
    --frames 5 --gpu 1 --tile compare_tile.png
"""
import argparse
import json
import os
import sys

PREFIX = "[compare_face_sim]"


def log(msg: str) -> None:
    print(f"{PREFIX} {msg}", file=sys.stderr, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="reference face/person image")
    ap.add_argument("--video", action="append", required=True, help="video(s) to score")
    ap.add_argument("--frames", type=int, default=5, help="frames sampled per video")
    ap.add_argument("--gpu", default=None, help="physical GPU index")
    ap.add_argument("--tile", default=None, help="write a comparison tile PNG here")
    args = ap.parse_args()

    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    import cv2
    import numpy as np
    from insightface.app import FaceAnalysis

    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    app = FaceAnalysis(name="buffalo_l", providers=providers)
    app.prepare(ctx_id=0, det_size=(640, 640))

    def largest_face_embedding(bgr):
        faces = app.get(bgr)
        if not faces:
            return None, None
        faces.sort(key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
                   reverse=True)
        f = faces[0]
        emb = f.normed_embedding  # already L2-normalized
        return emb, f.bbox.astype(int)

    # reference embedding
    ref_bgr = cv2.imread(args.ref)
    if ref_bgr is None:
        log(f"cannot read ref image: {args.ref}")
        return 1
    ref_emb, _ = largest_face_embedding(ref_bgr)
    if ref_emb is None:
        log(f"no face detected in reference: {args.ref}")
        return 1

    def sample_frames(path, n):
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        idxs = [int(round(i * (total - 1) / max(1, n - 1))) for i in range(n)] if n > 1 else [total // 2]
        out = []
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok:
                out.append((idx, frame))
        cap.release()
        return out

    results = {}
    tile_cols = []  # for the comparison tile: [ref] + per-video sampled faces
    # reference column (single face crop)
    for path in args.video:
        frames = sample_frames(path, args.frames)
        sims = []
        face_crops = []
        for idx, frame in frames:
            emb, bbox = largest_face_embedding(frame)
            if emb is None:
                continue
            sim = float(np.dot(ref_emb, emb))  # both L2-normalized => cosine
            sims.append(sim)
            if bbox is not None:
                x1, y1, x2, y2 = [max(0, v) for v in bbox]
                crop = frame[y1:y2, x1:x2]
                if crop.size:
                    face_crops.append(cv2.resize(crop, (128, 128)))
        name = os.path.basename(path)
        if sims:
            results[name] = {
                "path": path,
                "frames_with_face": len(sims),
                "frames_sampled": len(frames),
                "face_sim_mean": round(float(np.mean(sims)), 4),
                "face_sim_std": round(float(np.std(sims)), 4),
                "face_sim_min": round(float(np.min(sims)), 4),
                "face_sim_max": round(float(np.max(sims)), 4),
                "per_frame": [round(s, 4) for s in sims],
            }
        else:
            results[name] = {"path": path, "frames_with_face": 0,
                             "frames_sampled": len(frames), "note": "no face detected"}
        if face_crops:
            tile_cols.append((name, face_crops))

    # comparison tile
    if args.tile and tile_cols:
        ref_face_bgr = ref_bgr
        _, rbbox = largest_face_embedding(ref_bgr)
        if rbbox is not None:
            x1, y1, x2, y2 = [max(0, v) for v in rbbox]
            ref_face_bgr = ref_bgr[y1:y2, x1:x2]
        ref_tile = cv2.resize(ref_face_bgr, (128, 128))
        rows = []
        maxn = max(len(c) for _, c in tile_cols)
        for name, crops in tile_cols:
            row = [ref_tile] + crops + [np.zeros((128, 128, 3), np.uint8)] * (maxn - len(crops))
            rows.append(np.hstack(row))
        tile = np.vstack(rows)
        cv2.imwrite(args.tile, tile)
        log(f"wrote comparison tile: {args.tile} (col0=ref, then sampled frames)")

    print(json.dumps(results, indent=2, ensure_ascii=False))
    # verdict hint
    if len(results) == 2:
        vals = [(n, r.get("face_sim_mean")) for n, r in results.items() if r.get("face_sim_mean") is not None]
        if len(vals) == 2:
            vals.sort(key=lambda x: x[1], reverse=True)
            log(f"HIGHER Face-Sim: {vals[0][0]} ({vals[0][1]}) vs {vals[1][0]} ({vals[1][1]})")
            log("★ numbers are a guide; confirm with the tile + full video by eye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
