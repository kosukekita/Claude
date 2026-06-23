#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
edit_video.py — a thin, robust wrapper over ffmpeg for the `generate-edit-video`
skill. Fully LOCAL editing (no GPU, no backend selection). It does NOT generate
media — see gen_video.py / gen_image.py for that. This file wraps the *common*
ffmpeg recipes with SAFE DEFAULTS; heavier / edge recipes live in
reference/ffmpeg-recipes.md.

Subcommands (argparse subparsers; each has its own --help):

    trim          --in --ss --to/--t --out          cut a clip (stream-copy by default)
    concat        --inputs ... --out                join clips (demuxer if codecs match, else filter)
    speed         --in --factor --out               change speed (setpts + atempo)
    subtitle      --in --srt --out [--soft]         burn subtitles (or mux soft subs)
    overlay       --in (--image|--text) --pos --out watermark image / drawtext
    audio-replace --in --audio --out                swap the audio track
    audio-mix     --in --music [--music-volume] [--duck] --out   mix BGM under original (sidechain duck)
    resize        --in (--w --h | --aspect) --out   scale + pad to fit (letterbox)
    fps           --in --fps --out                  change frame rate
    frames        --in --out-dir                    extract frames to PNGs
    frames        --from-dir --fps --out            build a video from a frame dir
    gif           --in [--fps] [--width] --out      make a GIF (palettegen/paletteuse)
    thumb         --in --at --out                   grab a single still
    reencode      --in [--crf] [--preset] [--codec] --out   transcode with safe defaults

SAFE DEFAULTS applied to EVERY re-encode:
    -pix_fmt yuv420p                  (broadly playable)
    even dimensions                  (scale=...:-2, or pad to even) — x264/x265 need even
    setsar=1                         after any scale/pad
    -movflags +faststart             for .mp4/.mov outputs (web streaming)
    -shortest                        whenever multiple input streams are combined
    -c:a aac -b:a 192k               audio default when re-encoding audio

It PRINTS the exact ffmpeg command it runs (so the output doubles as
documentation / a recipe you can copy). ffmpeg is resolved robustly and ALWAYS
invoked with a cleaned environment: anaconda's libtinfo.so.6 pollutes
LD_LIBRARY_PATH and breaks subprocesses, so we scrub conda paths out of
LD_LIBRARY_PATH (and source scripts/env.sh when present) before exec.

stdlib-only (PEP723, no deps) — it just shells out to ffmpeg/ffprobe.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Locations / sibling files
# --------------------------------------------------------------------------- #
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ENV_SH = SCRIPT_DIR / "env.sh"
RECIPES_MD = SKILL_DIR / "reference" / "ffmpeg-recipes.md"


def log(msg: str) -> None:
    print(f"[edit_video] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 2) -> "None":
    log(f"ERROR: {msg}")
    sys.exit(code)


# --------------------------------------------------------------------------- #
# Clean environment (strip the anaconda libtinfo LD_LIBRARY_PATH pollution)
# --------------------------------------------------------------------------- #
def _scrub_ld(env: dict) -> dict:
    """Return a copy of `env` with conda/anaconda/miniconda entries removed from
    LD_LIBRARY_PATH. anaconda ships a libtinfo.so.6 that emits 'no version
    information available' and has broken shelled-out subprocesses before, so we
    hand ffmpeg a cleaned LD_LIBRARY_PATH. (The conda ffmpeg itself still finds
    its own libs via rpath; we only drop the polluting prefix.)
    """
    env = dict(env)
    ld = env.get("LD_LIBRARY_PATH", "")
    if ld:
        kept = [
            p
            for p in ld.split(os.pathsep)
            if p and "anaconda" not in p and "miniconda" not in p and "conda" not in p
        ]
        new = os.pathsep.join(kept)
        if new:
            env["LD_LIBRARY_PATH"] = new
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env


def clean_env() -> dict:
    """Build the environment used for every ffmpeg/ffprobe call.

    If scripts/env.sh exists we source it in a clean shell and capture the
    resulting environment (mirrors what the GPU scripts do); otherwise we just
    scrub LD_LIBRARY_PATH in-process. Either way conda pollution is removed.
    """
    if ENV_SH.exists():
        try:
            cmd = f'source {shlex.quote(str(ENV_SH))} >/dev/null 2>&1; /usr/bin/env -0'
            out = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True,
                check=True,
                env=_scrub_ld(os.environ),
            ).stdout
            env: dict = {}
            for chunk in out.split(b"\0"):
                if not chunk:
                    continue
                k, _, v = chunk.partition(b"=")
                env[k.decode("utf-8", "replace")] = v.decode("utf-8", "replace")
            if env:
                return _scrub_ld(env)
        except Exception as e:  # noqa: BLE001 — env.sh is best-effort
            log(f"could not source env.sh ({e}); falling back to in-process scrub")
    return _scrub_ld(os.environ)


# --------------------------------------------------------------------------- #
# Resolve ffmpeg / ffprobe robustly
# --------------------------------------------------------------------------- #
def _resolve(tool: str) -> str:
    """Locate `ffmpeg`/`ffprobe`, preferring a system (non-conda) build but
    falling back to whatever is on PATH (the conda one works once the env is
    scrubbed). Honors $FFMPEG / $FFPROBE overrides.
    """
    override = os.environ.get(tool.upper())
    if override and Path(override).exists():
        return override
    # Prefer a non-conda binary in the usual system locations.
    for cand in (f"/usr/bin/{tool}", f"/usr/local/bin/{tool}", f"/bin/{tool}"):
        if os.access(cand, os.X_OK):
            return cand
    found = shutil.which(tool)
    if found:
        return found
    # Last resort: a couple of well-known conda layouts.
    for cand in (
        Path.home() / "anaconda3" / "bin" / tool,
        Path.home() / "miniconda3" / "bin" / tool,
    ):
        if cand.exists():
            return str(cand)
    die(f"could not find `{tool}` on PATH. Install ffmpeg or set ${tool.upper()}.")
    raise RuntimeError("unreachable")


FFMPEG = None  # resolved lazily in main()
FFPROBE = None


# --------------------------------------------------------------------------- #
# Run helpers — every ffmpeg call goes through here and is PRINTED first
# --------------------------------------------------------------------------- #
def _quote_cmd(cmd: list[str]) -> str:
    return " ".join(shlex.quote(c) for c in cmd)


def run_ffmpeg(args: list[str], *, dry_run: bool = False, overwrite: bool = True) -> int:
    """Build, PRINT and run an ffmpeg command with the cleaned env.

    `args` is everything AFTER the ffmpeg binary. We prepend `-hide_banner` and
    `-y`/`-n`. The exact command is printed to stdout so it doubles as docs.
    """
    cmd = [FFMPEG, "-hide_banner", "-y" if overwrite else "-n", *args]
    print("\n# exact ffmpeg command:")
    print(_quote_cmd(cmd) + "\n", flush=True)
    if dry_run:
        log("dry-run: not executing")
        return 0
    proc = subprocess.run(cmd, env=clean_env())
    if proc.returncode != 0:
        die(f"ffmpeg exited with code {proc.returncode}", proc.returncode)
    return proc.returncode


def ffprobe_json(path: str) -> dict:
    """Return ffprobe's JSON for streams+format, or {} on failure."""
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        path,
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, check=True, env=clean_env()
        ).stdout
        return json.loads(out or b"{}")
    except Exception as e:  # noqa: BLE001
        log(f"ffprobe failed for {path}: {e}")
        return {}


def video_stream(info: dict) -> dict | None:
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            return s
    return None


def audio_stream(info: dict) -> dict | None:
    for s in info.get("streams", []):
        if s.get("codec_type") == "audio":
            return s
    return None


# --------------------------------------------------------------------------- #
# Safe-default building blocks
# --------------------------------------------------------------------------- #
def is_mp4_like(path: str) -> bool:
    return Path(path).suffix.lower() in (".mp4", ".m4v", ".mov", ".m4a")


def faststart_flags(out: str) -> list[str]:
    """+faststart for mp4/mov so the moov atom is at the front (web streaming)."""
    return ["-movflags", "+faststart"] if is_mp4_like(out) else []


def even_scale_filter(w: int | None = None, h: int | None = None) -> str:
    """A scale filter that forces EVEN output dims (required by x264/x265) and
    resets SAR. If only one of w/h is given the other is -2 (keep aspect, even).
    With neither, just force the current dims even and reset SAR.
    """
    if w and h:
        return f"scale={w}:{h}:force_original_aspect_ratio=decrease,setsar=1"
    if w:
        return f"scale={w}:-2,setsar=1"
    if h:
        return f"scale=-2:{h},setsar=1"
    # No target size: just guarantee even dims for the encoder.
    return "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1"


def codec_video_args(codec: str, crf: int, preset: str) -> list[str]:
    if codec in ("h264", "libx264", "x264"):
        return ["-c:v", "libx264", "-crf", str(crf), "-preset", preset]
    if codec in ("h265", "hevc", "libx265", "x265"):
        # tag hvc1 so Apple/QuickTime plays the .mp4
        return [
            "-c:v",
            "libx265",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-tag:v",
            "hvc1",
        ]
    die(f"unknown --codec {codec!r} (use h264 or h265)")
    raise RuntimeError("unreachable")


AUDIO_DEFAULT = ["-c:a", "aac", "-b:a", "192k"]


# --------------------------------------------------------------------------- #
# Subcommand implementations
# --------------------------------------------------------------------------- #
def cmd_trim(a: argparse.Namespace) -> None:
    """Cut [--ss, --to] or [--ss, +--t]. Stream-copy by default (fast, lossless,
    but cuts land on keyframes); --reencode for frame-accurate cuts."""
    args: list[str] = []
    # -ss before -i = fast seek; for stream-copy this is what we want.
    if a.ss is not None:
        args += ["-ss", a.ss]
    args += ["-i", a.input]
    if a.to is not None:
        args += ["-to", a.to]
    if a.t is not None:
        args += ["-t", a.t]
    if a.reencode:
        args += even_filter_args()
        args += codec_video_args(a.codec, a.crf, a.preset)
        args += AUDIO_DEFAULT
    else:
        # Lossless copy. -avoid_negative_ts keeps timestamps sane after -ss.
        args += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def even_filter_args() -> list[str]:
    return ["-vf", even_scale_filter(), "-pix_fmt", "yuv420p"]


def _codecs_match(infos: list[dict]) -> bool:
    """True iff all inputs share video codec, audio codec, w/h, pix_fmt — i.e.
    the concat *demuxer* (stream-copy) is safe. Otherwise we must re-encode."""
    sigs = []
    for info in infos:
        v = video_stream(info) or {}
        au = audio_stream(info) or {}
        sigs.append(
            (
                v.get("codec_name"),
                v.get("width"),
                v.get("height"),
                v.get("pix_fmt"),
                au.get("codec_name"),
                au.get("sample_rate"),
                au.get("channels"),
            )
        )
    return len(set(sigs)) == 1 and sigs[0][0] is not None


def cmd_concat(a: argparse.Namespace) -> None:
    """Join clips. If all inputs share codec/size/pix_fmt we use the concat
    DEMUXER (instant, lossless stream-copy). Otherwise we fall back to the
    concat FILTER, re-encoding everything to a common, safe format."""
    inputs = a.inputs
    if len(inputs) < 2:
        die("concat needs at least 2 --inputs")
    for p in inputs:
        if not Path(p).exists():
            die(f"input not found: {p}")

    infos = [ffprobe_json(p) for p in inputs]
    same = _codecs_match(infos)
    force_filter = a.reencode
    if same and not force_filter:
        # ---- concat demuxer (stream copy) ----
        listfile = Path(a.out).with_suffix(".concat.txt")
        # ffconcat list: paths must be quoted; use absolute to avoid cwd issues.
        lines = ["ffconcat version 1.0"]
        for p in inputs:
            ap = str(Path(p).resolve()).replace("'", r"'\''")
            lines.append(f"file '{ap}'")
        listfile.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log(f"codecs match -> concat demuxer (stream copy); list = {listfile}")
        args = [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listfile),
            "-c",
            "copy",
        ]
        args += faststart_flags(a.out)
        args += [a.out]
        run_ffmpeg(args, dry_run=a.dry_run)
        if not a.dry_run and not a.keep_list:
            listfile.unlink(missing_ok=True)
        return

    # ---- concat filter (re-encode to a common format) ----
    reason = "forced --reencode" if force_filter else "codecs/sizes differ"
    log(f"{reason} -> concat filter (re-encode). Normalizing to a common format.")
    args: list[str] = []
    for p in inputs:
        args += ["-i", p]
    n = len(inputs)
    # Normalize each input: scale to the first input's even-dim'd size, reset
    # SAR/fps, ensure audio exists (silence if missing handled by filter).
    v0 = video_stream(infos[0]) or {}
    tw = (v0.get("width") or 1280) // 2 * 2
    th = (v0.get("height") or 720) // 2 * 2
    target_fps = a.fps or 30
    parts = []
    labels = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={tw}:{th}:force_original_aspect_ratio=decrease,"
            f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={target_fps},"
            f"format=yuv420p[v{i}]"
        )
        # Pull audio if present, else synthesize silence so streams line up.
        if audio_stream(infos[i]):
            parts.append(f"[{i}:a]aresample=async=1:first_pts=0[a{i}]")
        else:
            # No audio in this input: synthesize silence the length of THIS
            # clip so the audio segment matches its video segment exactly.
            try:
                dur = float((infos[i].get("format") or {}).get("duration") or 0) or 1.0
            except (TypeError, ValueError):
                dur = 1.0
            parts.append(
                f"anullsrc=channel_layout=stereo:sample_rate=48000,"
                f"atrim=0:{dur:.3f}[a{i}]"
            )
        labels.append(f"[v{i}][a{i}]")
    filtergraph = (
        ";".join(parts)
        + ";"
        + "".join(labels)
        + f"concat=n={n}:v=1:a=1[outv][outa]"
    )
    args += ["-filter_complex", filtergraph, "-map", "[outv]", "-map", "[outa]"]
    args += codec_video_args(a.codec, a.crf, a.preset)
    args += ["-pix_fmt", "yuv420p"]
    args += AUDIO_DEFAULT
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_speed(a: argparse.Namespace) -> None:
    """Change playback speed by --factor (2.0 = 2x faster, 0.5 = half speed).
    Video via setpts=PTS/factor; audio via chained atempo (each 0.5..2.0)."""
    f = a.factor
    if f <= 0:
        die("--factor must be > 0")
    vfilter = f"setpts={1.0 / f:.6f}*PTS"
    # atempo only accepts 0.5..2.0 per instance; chain to reach `f`.
    afilters = []
    remaining = f
    if remaining >= 1.0:
        while remaining > 2.0 + 1e-9:
            afilters.append("atempo=2.0")
            remaining /= 2.0
        afilters.append(f"atempo={remaining:.6f}")
    else:
        while remaining < 0.5 - 1e-9:
            afilters.append("atempo=0.5")
            remaining /= 0.5
        afilters.append(f"atempo={remaining:.6f}")
    achain = ",".join(afilters)

    info = ffprobe_json(a.input)
    has_audio = audio_stream(info) is not None
    args = ["-i", a.input]
    if has_audio:
        args += [
            "-filter_complex",
            f"[0:v]{vfilter}[v];[0:a]{achain}[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
        ]
        args += AUDIO_DEFAULT
    else:
        args += ["-filter:v", vfilter, "-an"]
    args += codec_video_args(a.codec, a.crf, a.preset)
    args += ["-pix_fmt", "yuv420p"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_subtitle(a: argparse.Namespace) -> None:
    """Burn an .srt/.ass into the video (default), or --soft to mux it as a
    selectable subtitle track (stream-copy video, instant)."""
    if not Path(a.srt).exists():
        die(f"subtitle file not found: {a.srt}")
    if a.soft:
        # Mux as soft subs. mov_text for mp4, copy otherwise.
        sub_codec = "mov_text" if is_mp4_like(a.out) else "srt"
        args = [
            "-i",
            a.input,
            "-i",
            a.srt,
            "-map",
            "0",
            "-map",
            "1",
            "-c",
            "copy",
            "-c:s",
            sub_codec,
        ]
        args += faststart_flags(a.out)
        args += [a.out]
        run_ffmpeg(args, dry_run=a.dry_run)
        return
    # Burn-in. The subtitles filter wants a path with ':' and '\' escaped.
    srt_escaped = (
        str(a.srt).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    )
    style = ""
    if a.force_style:
        style = f":force_style='{a.force_style}'"
    vf = f"subtitles='{srt_escaped}'{style},setsar=1"
    args = [
        "-i",
        a.input,
        "-vf",
        vf,
        "-pix_fmt",
        "yuv420p",
    ]
    args += codec_video_args(a.codec, a.crf, a.preset)
    # keep audio as-is if possible
    args += ["-c:a", "copy"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


_POS_MAP = {
    "tl": "10:10",
    "tr": "main_w-overlay_w-10:10",
    "bl": "10:main_h-overlay_h-10",
    "br": "main_w-overlay_w-10:main_h-overlay_h-10",
    "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2",
}
_TEXT_POS_MAP = {
    "tl": "x=20:y=20",
    "tr": "x=w-tw-20:y=20",
    "bl": "x=20:y=h-th-20",
    "br": "x=w-tw-20:y=h-th-20",
    "center": "x=(w-tw)/2:y=(h-th)/2",
}


def cmd_overlay(a: argparse.Namespace) -> None:
    """Overlay a watermark image (--image) or draw text (--text) at --pos
    (tl/tr/bl/br/center). Re-encodes video; audio is stream-copied."""
    if not a.image and a.text is None:
        die("overlay needs --image OR --text")
    if a.image and a.text is not None:
        die("overlay takes only one of --image / --text")

    args = ["-i", a.input]
    if a.image:
        if not Path(a.image).exists():
            die(f"overlay image not found: {a.image}")
        args += ["-i", a.image]
        pos = _POS_MAP.get(a.pos, a.pos)  # allow raw "x:y"
        # Optionally scale the watermark to --scale fraction of main width.
        if a.scale:
            fc = (
                f"[1:v]scale=iw*{a.scale}:-1[wm];"
                f"[0:v][wm]overlay={pos}:format=auto,setsar=1[v]"
            )
        else:
            fc = f"[0:v][1:v]overlay={pos}:format=auto,setsar=1[v]"
        args += ["-filter_complex", fc, "-map", "[v]"]
        # map original audio if present
        if audio_stream(ffprobe_json(a.input)):
            args += ["-map", "0:a", "-c:a", "copy"]
    else:
        pos = _TEXT_POS_MAP.get(a.pos, a.pos)
        text = a.text.replace("\\", "\\\\").replace(":", r"\:").replace("'", r"’")
        draw = (
            f"drawtext=text='{text}':{pos}:fontsize={a.fontsize}:"
            f"fontcolor={a.fontcolor}:box=1:boxcolor={a.boxcolor}:boxborderw=8"
        )
        args += ["-vf", f"{draw},setsar=1"]
        if audio_stream(ffprobe_json(a.input)):
            args += ["-c:a", "copy"]
    args += codec_video_args(a.codec, a.crf, a.preset)
    args += ["-pix_fmt", "yuv420p"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_audio_replace(a: argparse.Namespace) -> None:
    """Replace the video's audio with --audio. Video is stream-copied; the new
    audio is encoded to AAC. -shortest stops at whichever stream ends first."""
    if not Path(a.audio).exists():
        die(f"audio file not found: {a.audio}")
    args = [
        "-i",
        a.input,
        "-i",
        a.audio,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        *AUDIO_DEFAULT,
        "-shortest",
    ]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_audio_mix(a: argparse.Namespace) -> None:
    """Mix background --music under the video's ORIGINAL audio. --music-volume
    scales the music; --duck enables sidechaincompress so the music dips when
    the original audio (e.g. voice) is loud. Video stream-copied."""
    if not Path(a.music).exists():
        die(f"music file not found: {a.music}")
    info = ffprobe_json(a.input)
    has_audio = audio_stream(info) is not None
    vol = a.music_volume

    if not has_audio:
        # No original audio: music simply becomes the track.
        log("input has no audio track; using music as the sole audio")
        fc = f"[1:a]volume={vol}[a]"
        args = [
            "-i",
            a.input,
            "-i",
            a.music,
            "-filter_complex",
            fc,
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            *AUDIO_DEFAULT,
            "-shortest",
        ]
        args += faststart_flags(a.out)
        args += [a.out]
        run_ffmpeg(args, dry_run=a.dry_run)
        return

    if a.duck:
        # Sidechain: the original audio (0:a) drives compression of music (1:a).
        # We split the original so it both drives the compressor AND is mixed in.
        fc = (
            f"[0:a]asplit=2[sc][orig];"
            f"[1:a]volume={vol}[music];"
            f"[music][sc]sidechaincompress=threshold={a.duck_threshold}:"
            f"ratio={a.duck_ratio}:attack={a.duck_attack}:release={a.duck_release}[ducked];"
            f"[orig][ducked]amix=inputs=2:duration=first:dropout_transition=2"
            f":normalize=0[a]"
        )
    else:
        fc = (
            f"[1:a]volume={vol}[music];"
            f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2"
            f":normalize=0[a]"
        )
    args = [
        "-i",
        a.input,
        "-i",
        a.music,
        "-filter_complex",
        fc,
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        *AUDIO_DEFAULT,
        "-shortest",
    ]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_resize(a: argparse.Namespace) -> None:
    """Resize to --w x --h, or to an --aspect (16:9 / 9:16 / 1:1 / 4:5 ...).
    Always SCALE to fit then PAD (letterbox/pillarbox) so nothing is cropped,
    keeping even dims + SAR=1. Audio stream-copied."""
    if a.aspect:
        if a.w or a.h:
            die("use either --aspect OR --w/--h, not both")
        info = ffprobe_json(a.input)
        v = video_stream(info) or {}
        sw = int(v.get("width") or 1920)
        sh = int(v.get("height") or 1080)
        try:
            ar_w, ar_h = (int(x) for x in a.aspect.split(":"))
        except Exception:  # noqa: BLE001
            die(f"bad --aspect {a.aspect!r}; expected like 16:9")
            raise
        # Fit the source inside a canvas of the target aspect, longest side
        # preserved roughly at source's larger dimension.
        if a.long is not None:
            long_side = a.long
        else:
            long_side = max(sw, sh)
        if ar_w >= ar_h:
            tw = long_side
            th = round(long_side * ar_h / ar_w)
        else:
            th = long_side
            tw = round(long_side * ar_w / ar_h)
        tw = tw // 2 * 2
        th = th // 2 * 2
    else:
        if not (a.w and a.h):
            die("resize needs --w AND --h (or --aspect)")
        tw = a.w // 2 * 2
        th = a.h // 2 * 2

    vf = (
        f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
        f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color={a.pad_color},setsar=1"
    )
    args = ["-i", a.input, "-vf", vf, "-pix_fmt", "yuv420p"]
    args += codec_video_args(a.codec, a.crf, a.preset)
    if audio_stream(ffprobe_json(a.input)):
        args += ["-c:a", "copy"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_fps(a: argparse.Namespace) -> None:
    """Change frame rate to --fps (re-times via the fps filter). Audio copied."""
    args = [
        "-i",
        a.input,
        "-vf",
        f"fps={a.fps},setsar=1",
        "-pix_fmt",
        "yuv420p",
    ]
    args += codec_video_args(a.codec, a.crf, a.preset)
    if audio_stream(ffprobe_json(a.input)):
        args += ["-c:a", "copy"]
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_frames(a: argparse.Namespace) -> None:
    """Two modes:
      extract:  --in --out-dir [--fps]  -> write PNG frames
      build:    --from-dir --fps --out  -> assemble PNGs into a video
    """
    if a.from_dir:
        # build a video from frames
        if not a.out:
            die("frames build mode needs --out")
        d = Path(a.from_dir)
        if not d.is_dir():
            die(f"--from-dir not a directory: {d}")
        pattern = str(d / a.pattern)
        args = [
            "-framerate",
            str(a.fps),
            "-i",
            pattern,
            "-vf",
            even_scale_filter(),
            "-pix_fmt",
            "yuv420p",
        ]
        args += codec_video_args(a.codec, a.crf, a.preset)
        args += faststart_flags(a.out)
        args += [a.out]
        run_ffmpeg(args, dry_run=a.dry_run)
        return
    # extract mode
    if not a.out_dir:
        die("frames extract mode needs --out-dir")
    od = Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    args = ["-i", a.input]
    if a.fps:
        args += ["-vf", f"fps={a.fps}"]
    args += ["-start_number", "0", str(od / a.pattern)]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_gif(a: argparse.Namespace) -> None:
    """High-quality GIF via the palettegen/paletteuse two-pass filtergraph in a
    single command (split + palettegen + paletteuse). --fps and --width tune
    size/quality."""
    fps = a.fps
    width = a.width
    args = ["-i", a.input]
    if a.ss is not None:
        # put -ss before -i for speed when seeking
        args = ["-ss", a.ss, "-i", a.input]
    if a.t is not None:
        args += ["-t", a.t]
    fc = (
        f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];"
        f"[s0]palettegen=max_colors={a.colors}[p];"
        f"[s1][p]paletteuse=dither={a.dither}"
    )
    args += ["-filter_complex", fc, a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_thumb(a: argparse.Namespace) -> None:
    """Grab a single still at --at (HH:MM:SS or seconds). -ss before -i for a
    fast seek; one frame out."""
    args = [
        "-ss",
        a.at,
        "-i",
        a.input,
        "-frames:v",
        "1",
        "-q:v",
        str(a.quality),
    ]
    if a.width:
        args += ["-vf", f"scale={a.width}:-2"]
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


def cmd_reencode(a: argparse.Namespace) -> None:
    """Transcode with all safe defaults: chosen codec + CRF + preset, yuv420p,
    even dims, SAR=1, +faststart for mp4, AAC audio."""
    args = ["-i", a.input, "-vf", even_scale_filter(), "-pix_fmt", "yuv420p"]
    args += codec_video_args(a.codec, a.crf, a.preset)
    args += AUDIO_DEFAULT
    args += faststart_flags(a.out)
    args += [a.out]
    run_ffmpeg(args, dry_run=a.dry_run)


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def add_common_encode_opts(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--codec",
        default="h264",
        choices=["h264", "h265"],
        help="video codec for re-encodes (default h264 = libx264)",
    )
    p.add_argument(
        "--crf",
        type=int,
        default=20,
        help="x264/x265 quality, lower=better (default 20; ~18 visually lossless)",
    )
    p.add_argument(
        "--preset",
        default="medium",
        help="x264/x265 speed/size preset (ultrafast..veryslow; default medium)",
    )


def add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print the ffmpeg command but do not run it",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="edit_video.py",
        description=(
            "Thin, robust ffmpeg wrapper with safe defaults (yuv420p, even dims, "
            "+faststart, -shortest, setsar=1). Prints the exact ffmpeg command it "
            f"runs. Heavier recipes live in {RECIPES_MD}."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run `edit_video.py <subcommand> --help` for per-command options.",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="SUBCOMMAND")

    # trim
    sp = sub.add_parser("trim", help="cut a clip [--ss .. --to|--t]")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--ss", help="start (HH:MM:SS or seconds)")
    sp.add_argument("--to", help="end timestamp (HH:MM:SS or seconds)")
    sp.add_argument("--t", help="duration from --ss (HH:MM:SS or seconds)")
    sp.add_argument("--out", required=True)
    sp.add_argument(
        "--reencode",
        action="store_true",
        help="frame-accurate cut (re-encode) instead of fast stream-copy",
    )
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_trim)

    # concat
    sp = sub.add_parser(
        "concat", help="join clips (demuxer if codecs match, else re-encode)"
    )
    sp.add_argument("--inputs", nargs="+", required=True, help="2+ input files in order")
    sp.add_argument("--out", required=True)
    sp.add_argument(
        "--reencode",
        action="store_true",
        help="force the concat filter (re-encode) even if codecs match",
    )
    sp.add_argument(
        "--fps", type=float, help="target fps for the re-encode path (default 30)"
    )
    sp.add_argument(
        "--keep-list",
        action="store_true",
        help="keep the temporary concat list file (demuxer path)",
    )
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_concat)

    # speed
    sp = sub.add_parser("speed", help="change speed (setpts + atempo)")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument(
        "--factor",
        type=float,
        required=True,
        help="speed multiplier (2.0=2x faster, 0.5=half speed)",
    )
    sp.add_argument("--out", required=True)
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_speed)

    # subtitle
    sp = sub.add_parser("subtitle", help="burn subtitles (or --soft to mux)")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--srt", required=True, help=".srt / .ass subtitle file")
    sp.add_argument("--out", required=True)
    sp.add_argument(
        "--soft",
        action="store_true",
        help="mux as a selectable soft-sub track (no burn-in, stream-copy)",
    )
    sp.add_argument(
        "--force-style",
        help="burn-in style override, e.g. 'FontName=Arial,FontSize=24,"
        "PrimaryColour=&H00FFFFFF&'",
    )
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_subtitle)

    # overlay
    sp = sub.add_parser("overlay", help="watermark image / drawtext")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--image", help="watermark/overlay image (png with alpha ok)")
    sp.add_argument("--text", help="text to draw")
    sp.add_argument(
        "--pos",
        default="br",
        help="tl|tr|bl|br|center, or a raw ffmpeg 'x:y' (default br)",
    )
    sp.add_argument(
        "--scale",
        type=float,
        help="(image) scale watermark width to this fraction of its own size, "
        "e.g. 0.2",
    )
    sp.add_argument("--fontsize", type=int, default=36, help="(text) font size")
    sp.add_argument("--fontcolor", default="white", help="(text) font color")
    sp.add_argument(
        "--boxcolor", default="black@0.5", help="(text) background box color"
    )
    sp.add_argument("--out", required=True)
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_overlay)

    # audio-replace
    sp = sub.add_parser("audio-replace", help="swap the audio track")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--audio", required=True, help="new audio file")
    sp.add_argument("--out", required=True)
    add_common(sp)
    sp.set_defaults(func=cmd_audio_replace)

    # audio-mix
    sp = sub.add_parser(
        "audio-mix", help="mix BGM under original audio (optional ducking)"
    )
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--music", required=True, help="background music file")
    sp.add_argument(
        "--music-volume",
        type=float,
        default=0.3,
        help="music volume multiplier (default 0.3)",
    )
    sp.add_argument(
        "--duck",
        action="store_true",
        help="duck the music when original audio is loud (sidechaincompress)",
    )
    sp.add_argument("--duck-threshold", default="0.03", help="ducking threshold")
    sp.add_argument("--duck-ratio", default="8", help="ducking ratio")
    sp.add_argument("--duck-attack", default="20", help="ducking attack ms")
    sp.add_argument("--duck-release", default="300", help="ducking release ms")
    sp.add_argument("--out", required=True)
    add_common(sp)
    sp.set_defaults(func=cmd_audio_mix)

    # resize
    sp = sub.add_parser("resize", help="scale + pad to a size or aspect (letterbox)")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--w", type=int, help="target width")
    sp.add_argument("--h", type=int, help="target height")
    sp.add_argument(
        "--aspect", help="target aspect like 16:9 | 9:16 | 1:1 | 4:5 (scale+pad)"
    )
    sp.add_argument(
        "--long",
        type=int,
        help="(with --aspect) length of the long side in px (default: source's)",
    )
    sp.add_argument(
        "--pad-color", default="black", help="padding/letterbox color (default black)"
    )
    sp.add_argument("--out", required=True)
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_resize)

    # fps
    sp = sub.add_parser("fps", help="change frame rate")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--fps", type=float, required=True, help="target frame rate")
    sp.add_argument("--out", required=True)
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_fps)

    # frames
    sp = sub.add_parser(
        "frames", help="extract frames to a dir, OR build a video from a frame dir"
    )
    sp.add_argument("--in", dest="input", help="(extract) input video")
    sp.add_argument("--out-dir", help="(extract) directory for PNG frames")
    sp.add_argument("--from-dir", help="(build) directory of frames to assemble")
    sp.add_argument("--out", help="(build) output video")
    sp.add_argument(
        "--fps",
        type=float,
        help="(extract) sample at this fps; (build) frame rate of the output",
    )
    sp.add_argument(
        "--pattern",
        default="frame_%06d.png",
        help="frame filename pattern (default frame_%%06d.png)",
    )
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_frames)

    # gif
    sp = sub.add_parser("gif", help="make a high-quality GIF (palettegen/use)")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--fps", type=int, default=12, help="GIF frame rate (default 12)")
    sp.add_argument("--width", type=int, default=480, help="GIF width px (default 480)")
    sp.add_argument("--ss", help="start time (optional)")
    sp.add_argument("--t", help="duration (optional)")
    sp.add_argument("--colors", type=int, default=256, help="palette colors (max 256)")
    sp.add_argument(
        "--dither",
        default="bayer:bayer_scale=5",
        help="paletteuse dither (e.g. none | sierra2_4a | bayer:bayer_scale=5)",
    )
    sp.add_argument("--out", required=True)
    add_common(sp)
    sp.set_defaults(func=cmd_gif)

    # thumb
    sp = sub.add_parser("thumb", help="grab a single still frame")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--at", required=True, help="timestamp (HH:MM:SS or seconds)")
    sp.add_argument("--width", type=int, help="scale the thumbnail to this width")
    sp.add_argument(
        "--quality", type=int, default=2, help="JPEG q:v (2=best..31=worst); default 2"
    )
    sp.add_argument("--out", required=True)
    add_common(sp)
    sp.set_defaults(func=cmd_thumb)

    # reencode
    sp = sub.add_parser("reencode", help="transcode with safe defaults")
    sp.add_argument("--in", dest="input", required=True)
    sp.add_argument("--out", required=True)
    add_common_encode_opts(sp)
    add_common(sp)
    sp.set_defaults(func=cmd_reencode)

    return p


def _validate_input(a: argparse.Namespace) -> None:
    """Most subcommands take --in; check it exists early for a clean error."""
    inp = getattr(a, "input", None)
    # frames-build uses --from-dir not --in
    if a.cmd == "frames" and getattr(a, "from_dir", None):
        return
    if inp and not Path(inp).exists():
        die(f"input not found: {inp}")


def main(argv: list[str] | None = None) -> int:
    global FFMPEG, FFPROBE
    parser = build_parser()
    a = parser.parse_args(argv)
    FFMPEG = _resolve("ffmpeg")
    FFPROBE = _resolve("ffprobe")
    log(f"ffmpeg = {FFMPEG}")
    _validate_input(a)
    a.func(a)
    if not getattr(a, "dry_run", False):
        out = getattr(a, "out", None) or getattr(a, "out_dir", None)
        if out:
            log(f"done -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
