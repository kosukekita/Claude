# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright", "pypdf"]
# ///
"""
Render HTML slides to high-resolution PNG, or to PDF, using Playwright.

PNG mode (default):
    uv run render_slide.py --input slide-01.html --output slide-01.png
    uv run render_slide.py --input slide-01.html --output slide-01.png --scale 2
    uv run render_slide.py --input "slides/*.html" --output-dir ./png

PDF mode (--pdf): each HTML becomes one 1920x1080 page; a glob input is merged
into a single multi-page PDF (uses pypdf, declared above).
    uv run render_slide.py --input slide-01.html --pdf slide-01.pdf
    uv run render_slide.py --input "slides/*.html" --pdf deck.pdf

First-time setup:
    uv run playwright install chromium

Options:
    --input       Path to HTML file (glob accepted for batch mode)
    --output      Output PNG path (single file mode)
    --output-dir  Output directory for PNG batch mode
    --pdf         Output PDF path (merges multiple inputs into one PDF)
    --scale       Device scale factor [default: 2] → 3840×2160 (PNG only)
    --wait        Extra wait ms after fonts load [default: 200]
"""

import argparse
import asyncio
import glob
import sys
import tempfile
from pathlib import Path

SLIDE_W = 1920
SLIDE_H = 1080


async def _goto_ready(page, html_path: Path, wait_ms: int) -> None:
    file_url = html_path.resolve().as_uri()
    await page.goto(file_url)
    await page.wait_for_function("document.fonts.ready.then(() => true)")
    if wait_ms > 0:
        await page.wait_for_timeout(wait_ms)


async def render_one(page, html_path: Path, output_path: Path, scale: int, wait_ms: int) -> None:
    await _goto_ready(page, html_path, wait_ms)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(output_path), full_page=False)
    print(f"  Rendered: {output_path}", file=sys.stderr)


async def render_pdf_one(page, html_path: Path, output_path: Path, wait_ms: int) -> None:
    await _goto_ready(page, html_path, wait_ms)
    # Use screen media so the PDF matches the PNG output (not @media print rules).
    await page.emulate_media(media="screen")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await page.pdf(
        path=str(output_path),
        width=f"{SLIDE_W}px",
        height=f"{SLIDE_H}px",
        print_background=True,
        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        prefer_css_page_size=False,
    )


async def run(args: argparse.Namespace) -> None:
    from playwright.async_api import async_playwright

    inputs: list[Path] = []
    for pattern in args.input:
        matched = glob.glob(pattern, recursive=True)
        if not matched:
            print(f"[render_slide] WARNING: no files matched '{pattern}'", file=sys.stderr)
        inputs.extend(Path(p) for p in matched)

    if not inputs:
        print("[render_slide] ERROR: no input files found.", file=sys.stderr)
        sys.exit(1)

    if args.output and len(inputs) > 1:
        print("[render_slide] ERROR: --output accepts one file; use --output-dir for batch.", file=sys.stderr)
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch()  # headless; required for page.pdf()
        context = await browser.new_context(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=args.scale,
        )
        page = await context.new_page()

        if args.pdf:
            await _render_pdf(page, inputs, Path(args.pdf), args.wait)
        else:
            for html_path in inputs:
                if args.output:
                    out = Path(args.output)
                elif args.output_dir:
                    out = Path(args.output_dir) / (html_path.stem + ".png")
                else:
                    out = html_path.with_suffix(".png")
                await render_one(page, html_path, out, args.scale, args.wait)

        await browser.close()


async def _render_pdf(page, inputs: list[Path], out_pdf: Path, wait_ms: int) -> None:
    if len(inputs) == 1:
        await render_pdf_one(page, inputs[0], out_pdf, wait_ms)
        print(f"  Rendered PDF: {out_pdf}", file=sys.stderr)
        return

    # Multiple slides: render each to a temp 1-page PDF, then merge with pypdf.
    from pypdf import PdfWriter

    writer = PdfWriter()
    with tempfile.TemporaryDirectory() as tmp:
        for i, html_path in enumerate(inputs):
            page_pdf = Path(tmp) / f"page-{i:03d}.pdf"
            await render_pdf_one(page, html_path, page_pdf, wait_ms)
            writer.append(str(page_pdf))
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        with open(out_pdf, "wb") as f:
            writer.write(f)
    print(f"  Rendered PDF: {out_pdf}  ({len(inputs)} pages)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render HTML slides to PNG via Playwright.")
    parser.add_argument("--input", nargs="+", required=True)
    parser.add_argument("--output", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--pdf", default=None, help="Output PDF path (overrides PNG mode)")
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--wait", type=int, default=200)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
