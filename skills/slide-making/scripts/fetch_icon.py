# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""
Fetch an SVG icon from theSVG via jsDelivr CDN and cache it locally.

Usage:
    uv run fetch_icon.py --slug github --variant default
    uv run fetch_icon.py --slug arrow-right --variant mono --recolor
    uv run fetch_icon.py --slug aws-s3 --variant default  # AWS: recolor skipped automatically

Options:
    --slug       Icon slug (e.g. github, openai, arrow-right)
    --variant    Icon variant: default | mono | light | dark | wordmark  [default: default]
    --recolor    Replace fill colors with currentColor (decorative icons only)
    --cache-dir  Base cache directory  [default: ../cache/icons relative to this script]
    --output     Write SVG to this path instead of cache
"""

import argparse
import re
import sys
from pathlib import Path

import requests

CDN_BASE = "https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons"

BRAND_KEEP_SLUGS: set[str] = {
    "github", "gitlab", "bitbucket",
    "aws", "azure", "google-cloud", "gcp",
    "python", "javascript", "typescript", "nodejs", "node-js",
    "openai", "anthropic",
    "docker", "kubernetes",
    "slack", "notion", "figma", "miro",
    "react", "vue", "angular", "svelte",
    "postgresql", "mysql", "mongodb",
    "linux", "windows", "apple", "android",
    "youtube", "twitter", "x", "linkedin", "facebook", "instagram",
}


def _is_aws_architecture(slug: str) -> bool:
    return slug.startswith("aws-architecture-") or slug.startswith("aws-arch-")


def _is_brand_icon(slug: str) -> bool:
    return slug in BRAND_KEEP_SLUGS or _is_aws_architecture(slug)


def _recolor_svg(svg_text: str) -> str:
    svg_text = re.sub(r'fill="#[0-9a-fA-F]{3,8}"', 'fill="currentColor"', svg_text)
    svg_text = re.sub(r'(style="[^"]*fill\s*:\s*)#[0-9a-fA-F]{3,8}', r'\1currentColor', svg_text)
    return svg_text


def fetch_icon(
    slug: str,
    variant: str = "default",
    recolor: bool = False,
    cache_dir: Path | None = None,
    output: Path | None = None,
) -> str:
    if cache_dir is None:
        cache_dir = Path(__file__).parent.parent / "cache" / "icons"

    cache_path = cache_dir / slug / f"{variant}.svg"

    if cache_path.exists() and not output:
        svg = cache_path.read_text(encoding="utf-8")
        if recolor and not _is_brand_icon(slug):
            svg = _recolor_svg(svg)
        return svg

    url = f"{CDN_BASE}/{slug}/{variant}.svg"
    resp = requests.get(url, timeout=10)

    if resp.status_code == 404 and variant != "default":
        print(f"[fetch_icon] 404 for variant '{variant}', falling back to 'default'", file=sys.stderr)
        return fetch_icon(slug, "default", recolor, cache_dir, output)

    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: HTTP {resp.status_code}")

    svg = resp.text
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(svg, encoding="utf-8")

    if recolor:
        if _is_aws_architecture(slug):
            print(
                f"[fetch_icon] WARNING: '{slug}' is AWS Architecture (CC BY-ND). Recolor skipped.",
                file=sys.stderr,
            )
        elif _is_brand_icon(slug):
            print(f"[fetch_icon] NOTE: '{slug}' is a brand icon. Recolor skipped.", file=sys.stderr)
        else:
            svg = _recolor_svg(svg)

    if output:
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(f"[fetch_icon] Written to {out}", file=sys.stderr)

    return svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch theSVG icon and cache locally.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--variant", default="default")
    parser.add_argument("--recolor", action="store_true")
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    svg = fetch_icon(
        slug=args.slug,
        variant=args.variant,
        recolor=args.recolor,
        cache_dir=args.cache_dir,
        output=args.output,
    )
    if not args.output:
        print(svg)


if __name__ == "__main__":
    main()
