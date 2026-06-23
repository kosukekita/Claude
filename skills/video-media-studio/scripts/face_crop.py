#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python", "numpy", "pillow"]
# ///
"""
face_crop.py — detect faces with OpenCV YuNet and crop the image HORIZONTALLY so
everything ABOVE the cut line is removed and the body BELOW is kept. Default cut
sits just above the mouth (`--mode chin`): eyes + nose are removed, mouth / chin /
neck / body retained. Built for the `video-media-studio` skill — e.g. turning a
mirror-selfie portrait into a "neck-down only" frame to feed an i2v pipeline.

Detector: YuNet (cv2.FaceDetectorYN) — gives 5 landmarks (eyes, nose, mouth
corners) which the crop formula needs. Model onnx is auto-downloaded (Git-LFS
media host) and integrity-checked (size + sha256 + LFS-pointer guard).

stdout = machine (only with --json); stderr = human decision log. See --help.
"""

import argparse
import glob as globmod
import hashlib
import os
import sys
import tempfile
import urllib.request

import numpy as np

try:
    import cv2
except Exception as e:  # pragma: no cover
    print(f"[face_crop] FATAL: opencv-python import failed: {e}", file=sys.stderr)
    sys.exit(3)

from PIL import Image, ImageOps

# ----------------------------------------------------------------------------- defaults
SCORE_MIN = 0.9          # YuNet scoreThreshold (rejects mirror-ghost / poster FPs)
NMS_THRESHOLD = 0.3
TOP_K = 5000
MARGIN_FRAC = 0.25       # chin mode: cut = mouth_y - 0.25*(mouth_y - nose_y)
ROLL_FRAC = 0.15         # rolled head -> use lowest mouth corner if |rmy-lmy| > 0.15*bbox_h
MIN_KEEP_PX = 64         # never leave fewer than this many rows after crop
SNAP = 8                 # even / x8 snap (LTX/Wan latent stride); round DOWN
MIN_FACE_PX = 40         # drop faces with bbox side < this

MODEL_URL = (
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
MODEL_NAME = "face_detection_yunet_2023mar.onnx"
MODEL_SIZE = 232589
MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
CACHE_PATH = os.path.expanduser("~/.cache/face_yunet/" + MODEL_NAME)
# the skill ships a verified copy next to this script; prefer it over a download
BUNDLED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", MODEL_NAME)


def log(msg: str) -> None:
    print(f"[face_crop] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 2) -> "None":
    log("ERROR: " + msg)
    sys.exit(code)


# ----------------------------------------------------------------------------- model
def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify(path: str) -> bool:
    """Size + sha256 + LFS-pointer guard. True if the file is the real model."""
    try:
        if os.path.getsize(path) != MODEL_SIZE:
            return False
        with open(path, "rb") as f:
            head = f.read(64)
        if len(head) < 1024 and head.startswith(b"version https://git-lfs"):
            return False
        if head.startswith(b"version https://git-lfs"):
            return False
        return _sha256(path) == MODEL_SHA256
    except OSError:
        return False


def resolve_model(user_model: str | None, no_verify: bool) -> str:
    """Return a path to a usable YuNet onnx, downloading+verifying as needed."""
    if user_model:
        if not os.path.isfile(user_model):
            die(f"--model not found: {user_model}", 4)
        if not no_verify and not _verify(user_model):
            die(f"--model failed integrity check (size/sha/pointer): {user_model}", 4)
        return user_model
    # bundled copy (verified)
    if os.path.isfile(BUNDLED_PATH) and _verify(BUNDLED_PATH):
        return BUNDLED_PATH
    # cache
    if os.path.isfile(CACHE_PATH) and _verify(CACHE_PATH):
        return CACHE_PATH
    # download -> temp -> verify -> atomic replace
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    log(f"downloading YuNet model -> {CACHE_PATH}")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CACHE_PATH), suffix=".part")
    os.close(fd)
    try:
        urllib.request.urlretrieve(MODEL_URL, tmp)
    except Exception as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        die(f"model download failed: {e}", 4)
    if not _verify(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass
        die("downloaded an LFS pointer or corrupt file, not the model "
            "(size/sha mismatch)", 4)
    os.replace(tmp, CACHE_PATH)
    return CACHE_PATH


# ----------------------------------------------------------------------------- io
def load_bgr(path: str) -> np.ndarray:
    """EXIF-transpose -> RGB (flatten alpha on white, 16->8bit, gray->RGB) -> BGR."""
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
    except Exception as e:
        die(f"cannot decode image {path}: {e}", 3)
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    rgb = np.asarray(im, dtype=np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


# ----------------------------------------------------------------------------- detection
def detect(detector, bgr: np.ndarray, score_min: float):
    h, w = bgr.shape[:2]
    detector.setInputSize((w, h))
    detector.setScoreThreshold(float(score_min))
    _, faces = detector.detect(bgr)
    return faces if faces is not None else np.empty((0, 15), dtype=np.float32)


def _anchors(f, H):
    """Return (eye_y, nose_y, mouth_y, face_unit, unreliable_flag)."""
    x, y, bw, bh = f[0], f[1], f[2], f[3]
    rey, ley = f[5], f[7]
    nose_y = f[9]
    rmy, lmy = f[11], f[13]
    eye_y = (rey + ley) / 2.0
    roll = abs(rmy - lmy)
    mouth_y = max(rmy, lmy) if roll > ROLL_FRAC * bh else (rmy + lmy) / 2.0
    face_unit = max(nose_y - eye_y, 1.0)
    # partial-out-of-frame / off-image landmark -> unreliable
    pts = [(f[4], f[5]), (f[6], f[7]), (f[8], f[9]), (f[10], f[11]), (f[12], f[13])]
    bad = (y <= 0) or any(
        (not np.isfinite(px)) or (not np.isfinite(py)) or px < 0 or py < 0 or px > 1e6 or py > 1e6
        for px, py in pts
    )
    return eye_y, nose_y, mouth_y, face_unit, bad


def _passes_filter(f, W, H, min_face):
    if f[14] < 0:  # score stored at index 14 (already >= threshold from detect, but guard)
        pass
    bw, bh = f[2], f[3]
    if bw < min_face or bh < min_face:
        return False
    eye_y = (f[5] + f[7]) / 2.0
    nose_y = f[9]
    mouth_y = (f[11] + f[13]) / 2.0
    if not (eye_y < nose_y < mouth_y):  # vertical landmark ordering kills pattern FPs
        return False
    pts = [f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13]]
    if any(not np.isfinite(v) for v in pts):
        return False
    # landmarks roughly inside the image
    xs = [f[4], f[6], f[8], f[10], f[12]]
    ys = [f[5], f[7], f[9], f[11], f[13]]
    if min(xs) < -bw or max(xs) > W + bw or min(ys) < -bh or max(ys) > H + bh:
        return False
    return True


def cut_for_face(f, mode, margin, H):
    eye_y, nose_y, mouth_y, face_unit, unreliable = _anchors(f, H)
    if unreliable:
        cut = f[1] + 0.85 * f[3]  # bbox-relative ~ mouth height
    elif mode == "chin":
        cut = mouth_y - MARGIN_FRAC * (mouth_y - nose_y)   # 0.75*mouth + 0.25*nose
    elif mode == "jaw":
        cut = mouth_y + 0.5 * face_unit
    elif mode == "nose":
        cut = nose_y
    elif mode == "eyes":
        cut = eye_y
    elif mode in ("hairline", "keep-face"):
        cut = f[1] - 0.6 * face_unit
    else:
        cut = mouth_y - MARGIN_FRAC * (mouth_y - nose_y)
    cut += margin * f[3]
    return cut, unreliable


def reduce_multi(cuts, faces, multi, W):
    if multi == "all":
        return max(cuts)
    if multi == "highest":
        return min(cuts)
    if multi == "largest":
        areas = [f[2] * f[3] for f in faces]
        # tie-break: closest bbox-center to image center
        cx = W / 2.0
        best = max(
            range(len(faces)),
            key=lambda i: (areas[i], -abs((faces[i][0] + faces[i][2] / 2.0) - cx)),
        )
        return cuts[best]
    return max(cuts)


# ----------------------------------------------------------------------------- crop math
def snap_box(crop_y, W, H):
    crop_y = int(round(crop_y))
    crop_y = max(0, min(crop_y, H - MIN_KEEP_PX))
    kept_h = H - crop_y
    kept_h -= kept_h % SNAP            # round DOWN; never grows the box
    if kept_h < MIN_KEEP_PX:
        kept_h = (MIN_KEEP_PX // SNAP + 1) * SNAP
        kept_h = min(kept_h, H - (H % SNAP))
    crop_y = H - kept_h
    W_even = W - (W % SNAP)
    return crop_y, kept_h, W_even


def letterbox(img, tw, th):
    """Pad (never over-crop) img to exactly tw x th, centered, black bars."""
    h, w = img.shape[:2]
    scale = min(tw / w, th / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((th, tw, 3), dtype=img.dtype)
    ox, oy = (tw - nw) // 2, (th - nh) // 2
    canvas[oy:oy + nh, ox:ox + nw] = resized
    return canvas


def draw_debug(bgr, faces, crop_y):
    dbg = bgr.copy()
    for f in faces:
        x, y, w, h = map(int, f[:4])
        cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 2)
        for j in range(4, 14, 2):
            cv2.circle(dbg, (int(f[j]), int(f[j + 1])), 3, (0, 0, 255), -1)
    cv2.line(dbg, (0, int(crop_y)), (dbg.shape[1], int(crop_y)), (255, 0, 255), 3)
    return dbg


# ----------------------------------------------------------------------------- per-file
def process_one(detector, in_path, out_path, args):
    bgr = load_bgr(in_path)
    H, W = bgr.shape[:2]
    if args.target is None and W < H * 0.5 is False:
        pass  # no strict portrait assert unless target given
    faces_raw = detect(detector, bgr, args.score_min)
    n_raw = len(faces_raw)
    faces = [f for f in faces_raw if _passes_filter(f, W, H, args.min_face)]

    # single-detection rescan at lower threshold (2-person photo likely missed one)
    single_warn = False
    if len(faces) == 1:
        rescan = detect(detector, bgr, 0.6)
        faces2 = [f for f in rescan if _passes_filter(f, W, H, args.min_face)]
        if len(faces2) >= 2:
            faces = faces2
        else:
            single_warn = True

    if len(faces) == 0:
        mode = args.on_no_face
        if mode == "skip":
            log(f"in={os.path.basename(in_path)} WxH={W}x{H} faces=0 on-no-face=skip -> SKIPPED")
            return ("skip", None)
        if mode == "fail":
            log(f"in={os.path.basename(in_path)} WxH={W}x{H} faces=0 on-no-face=fail")
            return ("nofacefail", None)
        if mode == "copy":
            cv2.imwrite(out_path, bgr)
            log(f"in={os.path.basename(in_path)} faces=0 on-no-face=copy -> out={os.path.basename(out_path)} (UNCHANGED)")
            return ("ok", out_path)
        if mode == "full":
            cy, kh, we = snap_box(0, W, H)
            out = bgr[cy:cy + kh, 0:we]
            if args.target:
                out = letterbox(out, *args.target)
            cv2.imwrite(out_path, out)
            log(f"in={os.path.basename(in_path)} faces=0 on-no-face=full -> out={os.path.basename(out_path)} size={out.shape[1]}x{out.shape[0]}")
            return ("ok", out_path)
        if mode == "center" and args.target:
            out = letterbox(bgr, *args.target)
            cv2.imwrite(out_path, out)
            log(f"in={os.path.basename(in_path)} faces=0 on-no-face=center -> out={os.path.basename(out_path)} size={out.shape[1]}x{out.shape[0]}")
            return ("ok", out_path)
        log(f"in={os.path.basename(in_path)} faces=0 on-no-face={mode} -> SKIPPED")
        return ("skip", None)

    cuts = []
    any_unreliable = False
    for f in faces:
        c, unrel = cut_for_face(f, args.mode, args.margin, H)
        cuts.append(c)
        any_unreliable = any_unreliable or unrel

    crop_y_raw = reduce_multi(cuts, faces, args.multi, W)
    crop_y, kept_h, W_even = snap_box(crop_y_raw, W, H)

    if args.dry_run:
        log(f"in={os.path.basename(in_path)} WxH={W}x{H} faces={len(faces)} (filtered from {n_raw}) "
            f"mode={args.mode} multi={args.multi} cut_y={crop_y} DRY-RUN (no write)")
        return ("ok", None)

    out = bgr[crop_y:crop_y + kept_h, 0:W_even]
    if args.target:
        out = letterbox(out, *args.target)
    cv2.imwrite(out_path, out)

    if args.debug:
        ddir = args.debug_dir or os.path.dirname(os.path.abspath(out_path))
        os.makedirs(ddir, exist_ok=True)
        base = os.path.splitext(os.path.basename(out_path))[0]
        dpath = os.path.join(ddir, base + "_debug.jpg")
        cv2.imwrite(dpath, draw_debug(bgr, faces, crop_y))

    flags = []
    if single_warn:
        flags.append("WARN single-detection (rescan@0.6 still 1)")
    if any_unreliable:
        flags.append("landmarks_unreliable")
    fstr = (" " + " ".join(flags)) if flags else ""
    eu = _anchors(faces[0], H)[3]
    log(f"in={os.path.basename(in_path)} WxH={W}x{H} faces={len(faces)} (filtered from {n_raw}){fstr} "
        f"mode={args.mode} multi={args.multi} score-min={args.score_min} cut_y={crop_y} "
        f"face_unit={eu:.0f} margin={args.margin} -> out={os.path.basename(out_path)} "
        f"size={out.shape[1]}x{out.shape[0]} snap={SNAP}")
    return ("ok", out_path)


# ----------------------------------------------------------------------------- main
def parse_target(s):
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        die(f"--target must be WxH, got {s!r}", 2)


def main():
    p = argparse.ArgumentParser(
        prog="face_crop.py",
        description="Crop above the chin/nose line (YuNet) to remove faces, keeping the body below.",
    )
    p.add_argument("--in", dest="input", help="source image")
    p.add_argument("--out", dest="output", help="cropped output path")
    p.add_argument("--mode", choices=["chin", "jaw", "nose", "eyes", "hairline", "keep-face"],
                   default="chin", help="landmark anchor for the cut (default chin: removes eyes+nose, keeps mouth)")
    p.add_argument("--margin", type=float, default=0.0,
                   help="shift cut down(+)/up(-) as fraction of bbox height")
    p.add_argument("--multi", choices=["all", "largest", "highest"], default="all",
                   help="multi-face rule: cut below all / biggest / topmost face")
    p.add_argument("--on-no-face", dest="on_no_face",
                   choices=["skip", "fail", "copy", "full", "center"], default="skip")
    p.add_argument("--target", type=str, default=None, help="letterbox-pad to exact WxH after crop")
    p.add_argument("--score-min", dest="score_min", type=float, default=SCORE_MIN)
    p.add_argument("--min-face", dest="min_face", type=int, default=MIN_FACE_PX)
    p.add_argument("--model", type=str, default=None, help="use a local onnx, skip download")
    p.add_argument("--no-verify", dest="no_verify", action="store_true")
    p.add_argument("--batch", nargs="+", default=None, help="globs/files; mutually exclusive with --in/--out")
    p.add_argument("--out-dir", dest="output_dir", default=None)
    p.add_argument("--suffix", default="_cropped")
    p.add_argument("--debug", action="store_true", help="also write *_debug.jpg overlay")
    p.add_argument("--debug-dir", dest="debug_dir", default=None)
    p.add_argument("--dry-run", dest="dry_run", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", dest="json_out", action="store_true")
    args = p.parse_args()

    if args.target:
        args.target = parse_target(args.target)

    # arg validation
    if args.batch:
        if args.input or args.output:
            die("--batch is mutually exclusive with --in/--out", 2)
        if not args.output_dir:
            die("--batch requires --out-dir", 2)
    else:
        if not args.input or not args.output:
            die("provide --in and --out (or use --batch with --out-dir)", 2)

    model_path = resolve_model(args.model, args.no_verify)
    try:
        detector = cv2.FaceDetectorYN_create(model_path, "", (320, 320), args.score_min,
                                             NMS_THRESHOLD, TOP_K)
    except Exception as e:
        die(f"failed to create YuNet detector: {e}", 3)

    if args.quiet:
        global log
        def log(_m):  # noqa
            pass

    if not args.batch:
        status, _ = process_one(detector, args.input, args.output, args)
        if status == "ok":
            sys.exit(0)
        if status == "skip":
            sys.exit(5)
        if status == "nofacefail":
            sys.exit(5)
        sys.exit(1)

    # batch
    files = []
    for pat in args.batch:
        m = sorted(globmod.glob(pat))
        files.extend(m if m else ([pat] if os.path.isfile(pat) else []))
    if not files:
        die("no input files matched --batch", 2)
    os.makedirs(args.output_dir, exist_ok=True)
    ok = skip = fail = 0
    for fp in files:
        base, ext = os.path.splitext(os.path.basename(fp))
        out = os.path.join(args.output_dir, base + args.suffix + ext)
        try:
            status, _ = process_one(detector, fp, out, args)
        except SystemExit:
            raise
        except Exception as e:
            log(f"in={os.path.basename(fp)} FAILED: {e}")
            status = "fail"
        if status == "ok":
            ok += 1
        elif status == "skip":
            skip += 1
        else:
            fail += 1
    log(f"batch: {ok} ok, {skip} skipped, {fail} failed")
    sys.exit(0 if ok >= 1 else 1)


if __name__ == "__main__":
    main()
