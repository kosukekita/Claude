#!/usr/bin/env python3
"""Markdown research vault primitives (standard library only)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FIELDS = ("url", "retrieved_at", "title", "type", "utility_score")
_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def research_root(project: str | Path = ".") -> Path:
    return Path(project).resolve() / "research"


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in ("null", "~"):
        return None
    if value in ("true", "false"):
        return value == "true"
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            return float(value) if "." in value else int(value)
        except ValueError:
            return value


def dump_frontmatter(meta: dict[str, Any]) -> str:
    return "---\n" + "".join(f"{k}: {_scalar(v)}\n" for k, v in meta.items()) + "---\n"


def parse_note(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    meta: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        meta[key.strip()] = _parse_scalar(value)
    return meta, text[end + 5 :]


def slug(value: str) -> str:
    clean = _SAFE.sub("-", value).strip("-._").lower()
    return (clean[:100] or "source")


def init_vault(project: str | Path = ".") -> Path:
    root = research_root(project)
    for part in ("sources", "claims", "intermediate", "checks", "drafts"):
        (root / part).mkdir(parents=True, exist_ok=True)
    return root


def write_note(
    project: str | Path,
    note_id: str,
    metadata: dict[str, Any],
    body: str,
    *,
    overwrite: bool = False,
) -> Path:
    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        raise ValueError("missing required frontmatter: " + ", ".join(missing))
    root = init_vault(project)
    path = root / "sources" / f"{slug(note_id)}.md"
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text(dump_frontmatter(metadata) + body.rstrip() + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def read_note(path: str | Path) -> tuple[dict[str, Any], str]:
    return parse_note(Path(path).read_text(encoding="utf-8"))


def iter_notes(project: str | Path = ".") -> Iterable[tuple[Path, dict[str, Any], str]]:
    root = research_root(project) / "sources"
    if not root.exists():
        return
    for path in sorted(root.glob("*.md")):
        meta, body = read_note(path)
        yield path, meta, body


def search(project: str | Path, query: str, *, case_sensitive: bool = False) -> list[dict[str, Any]]:
    needle = query if case_sensitive else query.casefold()
    found = []
    for path, meta, body in iter_notes(project):
        haystack = body if case_sensitive else body.casefold()
        if needle in haystack:
            found.append({"path": str(path), "metadata": meta, "matches": haystack.count(needle)})
    return found


def write_claims(project: str | Path, note_id: str, claims: list[dict[str, Any]]) -> tuple[Path, int]:
    """Persist only claims whose quoted_support is verbatim in the source note."""
    root = init_vault(project)
    source = root / "sources" / f"{slug(note_id)}.md"
    _, body = read_note(source)
    accepted, rejected = [], 0
    for claim in claims:
        quote = claim.get("quoted_support")
        if isinstance(quote, str) and quote and quote in body:
            accepted.append(claim)
        else:
            rejected += 1
    payload = {"source_id": slug(note_id), "accepted": accepted, "rejected_without_verbatim_quote": rejected}
    path = root / "claims" / f"{slug(note_id)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, rejected


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("--project", default=".")
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--project", default=".")
    p.add_argument("--case-sensitive", action="store_true")
    p = sub.add_parser("read"); p.add_argument("path")
    args = parser.parse_args(argv)
    if args.command == "init":
        print(init_vault(args.project).as_posix())
    elif args.command == "search":
        print(json.dumps(search(args.project, args.query, case_sensitive=args.case_sensitive), ensure_ascii=False))
    else:
        meta, body = read_note(args.path)
        print(json.dumps({"metadata": meta, "body": body}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except Exception as exc:
        print(f"vault: {exc}", file=sys.stderr)
        raise SystemExit(2)
