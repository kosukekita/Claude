#!/usr/bin/env python3
"""
Pitch-shift the target WAV while preserving the exact input frame count.

Default output:
  /home/kita/media-out/v2v-xvideos-part2-8min/audio/source_pitched.wav

The implementation uses the local ffmpeg build's asetrate + aresample + atempo
path because this environment does not include ffmpeg's rubberband filter or the
standalone rubberband CLI required by pyrubberband.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import wave
from pathlib import Path


FFMPEG = Path("/home/kita/anaconda3/bin/ffmpeg")
INPUT = Path("/home/kita/media-out/v2v-xvideos-part2-8min/audio/source_10s-8m10s.wav")
OUTPUT = Path("/home/kita/media-out/v2v-xvideos-part2-8min/audio/source_pitched.wav")


def wav_info(path: Path) -> tuple[int, int, int, int]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.getnframes()
    return sample_rate, channels, sample_width, frames


def atempo_chain(tempo: float) -> list[str]:
    """Build atempo filters while respecting ffmpeg's best-quality 0.5..2 range."""
    filters: list[str] = []
    remaining = tempo

    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0

    filters.append(f"atempo={remaining:.12g}")
    return filters


def run(cmd: list[str]) -> None:
    print("Running:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pitch-shift source_10s-8m10s.wav and force exact duration."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT,
        help=f"Input WAV path. Default: {INPUT}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help=f"Output WAV path. Default: {OUTPUT}",
    )
    parser.add_argument(
        "--semitones",
        type=float,
        default=3.0,
        help="Pitch shift in semitones. Default: +3.0",
    )
    args = parser.parse_args()

    if not FFMPEG.exists():
        raise FileNotFoundError(f"ffmpeg not found: {FFMPEG}")
    if not args.input.exists():
        raise FileNotFoundError(f"input not found: {args.input}")

    sample_rate, channels, sample_width, input_frames = wav_info(args.input)
    if sample_width != 2:
        print(
            f"Warning: input sample width is {sample_width} bytes; output will be PCM s16le.",
            file=sys.stderr,
        )

    factor = 2.0 ** (args.semitones / 12.0)
    tempo = 1.0 / factor

    filters = [
        f"asetrate={sample_rate}*{factor:.12g}",
        f"aresample={sample_rate}",
        *atempo_chain(tempo),
        "apad",
        f"atrim=end_sample={input_frames}",
        "asetpts=N/SR/TB",
    ]

    cmd = [
        str(FFMPEG),
        "-hide_banner",
        "-y",
        "-i",
        str(args.input),
        "-map",
        "0:a:0",
        "-af",
        ",".join(filters),
        "-ar",
        str(sample_rate),
        "-ac",
        str(channels),
        "-c:a",
        "pcm_s16le",
        str(args.output),
    ]
    run(cmd)

    out_sample_rate, out_channels, _out_sample_width, output_frames = wav_info(args.output)
    input_duration = input_frames / sample_rate
    output_duration = output_frames / out_sample_rate
    duration_delta_ms = abs(output_duration - input_duration) * 1000.0

    print(f"Input:  {input_frames} frames, {sample_rate} Hz, {channels} ch, {input_duration:.6f} s")
    print(f"Output: {output_frames} frames, {out_sample_rate} Hz, {out_channels} ch, {output_duration:.6f} s")
    print(f"Delta:  {duration_delta_ms:.6f} ms")

    if out_sample_rate != sample_rate:
        raise RuntimeError(f"sample-rate mismatch: input={sample_rate}, output={out_sample_rate}")
    if out_channels != channels:
        raise RuntimeError(f"channel-count mismatch: input={channels}, output={out_channels}")
    if output_frames != input_frames:
        raise RuntimeError(f"frame-count mismatch: input={input_frames}, output={output_frames}")
    if duration_delta_ms > 10.0:
        raise RuntimeError(f"duration mismatch exceeds 10 ms: {duration_delta_ms:.6f} ms")

    print(f"Wrote exact-duration pitched audio: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

