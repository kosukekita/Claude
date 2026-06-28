#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.0"]
# ///
"""Compose individual panel images into a manga page with gutters and borders.

Why: gen_image.py is text-to-image only. Generating each panel as a single
big frame (so the model fills it with real content) and then laying them out
here is the reliable way to get a multi-panel manga page where every panel
has actual content -- the "draw many panels in one shot" approach tends to
leave panels empty because SDXL spends its capacity on the grid, not the art.

Layout: rows of panels. --rows "2,1,2" means row0 has 2 panels, row1 has 1,
row2 has 2. Panels are consumed left-to-right, top-to-bottom from --panels.
Right-to-left reading order (Japanese manga) with --rtl: within each row the
first panel goes on the RIGHT.

Example:
  manga_page.py --panels p0.png p1.png p2.png p3.png p4.png \
      --rows "2,1,2" --rtl --page-size 1448x2048 \
      --gutter 18 --border 5 --out page.png
"""
import argparse, sys
from PIL import Image, ImageOps


def parse_rows(spec, n_panels):
    rows = [int(x) for x in spec.split(",") if x.strip()]
    if sum(rows) != n_panels:
        sys.exit(f"--rows sums to {sum(rows)} but got {n_panels} panels")
    return rows


def fit_cover(img, w, h):
    """Resize+crop to exactly fill (w,h), preserving aspect (cover)."""
    return ImageOps.fit(img, (w, h), method=Image.LANCZOS, centering=(0.5, 0.4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panels", nargs="+", required=True, help="panel image paths, in reading order")
    ap.add_argument("--rows", required=True, help='panels per row, e.g. "2,1,2"')
    ap.add_argument("--page-size", default="1448x2048", help="WxH of full page")
    ap.add_argument("--gutter", type=int, default=18, help="white gap between panels (px)")
    ap.add_argument("--margin", type=int, default=28, help="white page margin (px)")
    ap.add_argument("--border", type=int, default=5, help="black panel border thickness (px)")
    ap.add_argument("--rtl", action="store_true", help="right-to-left reading order per row")
    ap.add_argument("--bg", default="white", help="page background color")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    PW, PH = (int(x) for x in a.page_size.lower().split("x"))
    rows = parse_rows(a.rows, len(a.panels))
    page = Image.new("RGB", (PW, PH), a.bg)

    imgs = [Image.open(p).convert("RGB") for p in a.panels]
    idx = 0

    inner_w = PW - 2 * a.margin
    inner_h = PH - 2 * a.margin
    n_rows = len(rows)
    row_h = (inner_h - a.gutter * (n_rows - 1)) // n_rows

    y = a.margin
    for ncols in rows:
        cell_w = (inner_w - a.gutter * (ncols - 1)) // ncols
        # panels for this row
        row_imgs = imgs[idx: idx + ncols]
        idx += ncols
        if a.rtl:
            xs = [a.margin + (ncols - 1 - c) * (cell_w + a.gutter) for c in range(ncols)]
        else:
            xs = [a.margin + c * (cell_w + a.gutter) for c in range(ncols)]
        for c, im in enumerate(row_imgs):
            x = xs[c]
            panel = fit_cover(im, cell_w, row_h)
            page.paste(panel, (x, y))
            if a.border > 0:
                # draw black border by pasting on a slightly larger black rect underneath
                from PIL import ImageDraw
                d = ImageDraw.Draw(page)
                for t in range(a.border):
                    d.rectangle([x - t, y - t, x + cell_w - 1 + t, y + row_h - 1 + t], outline="black")
        y += row_h + a.gutter

    page.save(a.out)
    print(f"saved-> {a.out} ({PW}x{PH}, {len(a.panels)} panels, rows={rows}, rtl={a.rtl})")


if __name__ == "__main__":
    main()
