# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Export HTML slide(s) to an editable .pptx via html2pptx.app REST API.

Usage:
    uv run export_to_pptx.py --input slide-01.html --output slide-01.pptx
    uv run export_to_pptx.py --input "slides/*.html" --output deck.pptx
    uv run export_to_pptx.py --input slide-01.html --output out.pptx --api-key sk_live_xxxx

Environment:
    HTML2PPTX_API_KEY   API key (alternative to --api-key)
"""

import argparse
import glob
import os
import re
import sys
import time
from pathlib import Path

import httpx

BASE_URL = "https://html2pptx.app"
SLIDE_W_INCH = 13.333  # 16:9 PowerPoint standard width
SLIDE_H_INCH = 7.5     # 16:9 PowerPoint standard height


def extract_styles(html: str) -> str:
    """Extract all <style> block contents from the document head."""
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    return "\n".join(styles)


def load_html(paths: list[Path]) -> tuple[str, str]:
    """
    Return (combined_sections_html, combined_css).
    CSS is extracted from the first file's <head> (all files share the same design system).
    """
    sections: list[str] = []
    combined_css = ""

    for i, p in enumerate(paths):
        raw = p.read_text(encoding="utf-8")

        # Extract CSS from first file (design tokens are identical across slides)
        if i == 0:
            combined_css = extract_styles(raw)

        match = re.search(
            r'<section[^>]+class=["\'][^"\']*slide[^"\']*["\'][^>]*>.*?</section>',
            raw,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            sections.append(match.group(0))
        else:
            body = re.search(r'<body[^>]*>(.*?)</body>', raw, re.DOTALL | re.IGNORECASE)
            content = body.group(1).strip() if body else raw.strip()
            sections.append(
                f'<section class="slide" style="width:1920px;height:1080px;">{content}</section>'
            )

    return "\n".join(sections), combined_css


def create_job(client: httpx.Client, html: str, css: str, file_name: str, embed_fonts: bool) -> str:
    payload = {
        "fileName": file_name,
        "html": html,
        "css": css,
        "autoEmbedFonts": embed_fonts,
        "width": SLIDE_W_INCH,
        "height": SLIDE_H_INCH,
        "responseFormat": "url",
    }
    resp = client.post(f"{BASE_URL}/api/export/jobs", json=payload, timeout=30)
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", "60"))
        print(f"[export_to_pptx] Rate limited. Retry after {retry_after}s.", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    data = resp.json()
    job_id = data["jobId"]
    print(f"[export_to_pptx] Job created: {job_id} ({data.get('slideCount', '?')} slides)", file=sys.stderr)
    return job_id


def poll_job(client: httpx.Client, job_id: str, interval: float, timeout: float) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        resp = client.get(f"{BASE_URL}/api/export/jobs/{job_id}", timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        print(f"[export_to_pptx] Status: {status}", file=sys.stderr)
        if status == "completed":
            return data["downloadUrl"]
        if status == "failed":
            msg = data.get("message", "unknown error")
            print(f"[export_to_pptx] ERROR: Job failed - {msg}", file=sys.stderr)
            sys.exit(1)
        time.sleep(interval)
    print(f"[export_to_pptx] ERROR: Timed out after {timeout}s.", file=sys.stderr)
    sys.exit(1)


def download_pptx(client: httpx.Client, url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with client.stream("GET", url, timeout=60) as resp:
        resp.raise_for_status()
        output.write_bytes(resp.read())
    print(f"[export_to_pptx] Saved: {output}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export HTML slides to .pptx via html2pptx.app")
    parser.add_argument("--input", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--no-embed-fonts", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=3.0)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("HTML2PPTX_API_KEY")
    if not api_key:
        print("[export_to_pptx] ERROR: Set HTML2PPTX_API_KEY or use --api-key.", file=sys.stderr)
        sys.exit(1)

    inputs: list[Path] = []
    for pattern in args.input:
        matched = glob.glob(pattern, recursive=True)
        if not matched:
            print(f"[export_to_pptx] WARNING: no files matched '{pattern}'", file=sys.stderr)
        inputs.extend(sorted(Path(p) for p in matched))

    if not inputs:
        print("[export_to_pptx] ERROR: no input files found.", file=sys.stderr)
        sys.exit(1)

    print(f"[export_to_pptx] Processing {len(inputs)} file(s)...", file=sys.stderr)
    html, css = load_html(inputs)
    output = Path(args.output)

    headers = {"Authorization": f"Bearer {api_key}"}
    with httpx.Client(headers=headers) as client:
        job_id = create_job(client, html, css, output.name, embed_fonts=not args.no_embed_fonts)
        download_url = poll_job(client, job_id, args.poll_interval, args.timeout)
        download_pptx(client, download_url, output)

    print(f"[export_to_pptx] Done: {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
