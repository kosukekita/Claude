#!/usr/bin/env python3
"""Syndication clustering using URL, wire signatures, and text similarity."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
from collections import defaultdict
from typing import Any

TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
WIRE_PATTERNS = [
    re.compile(r"\b(?:reuters|associated press|the canadian press|agence france-presse|afp)\b", re.I),
    re.compile(r"\((?:reuters|ap|afp)\)\s*[-—]", re.I),
    re.compile(
        r"\b(?:pr newswire|business wire|globenewswire|accesswire|newsfile"
        r"(?:\s+corp(?:oration)?)?)\b",
        re.I,
    ),
]


def normalize_url(url: str) -> str:
    raw = url.strip().replace("\\", "/")
    parsed = urllib.parse.urlsplit(raw if "://" in raw else "https://" + raw)
    host = (parsed.hostname or "").encode("idna").decode("ascii").lower()
    port = parsed.port
    netloc = host + (f":{port}" if port and port not in (80, 443) else "")
    path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/") or "/"
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = sorted((k, v) for k, v in query if not k.lower().startswith("utm_") and k.lower() not in TRACKING)
    return urllib.parse.urlunsplit(((parsed.scheme or "https").lower(), netloc, path, urllib.parse.urlencode(query), ""))


def wire_signature(text: str) -> str | None:
    lead = re.sub(r"\s+", " ", text[:1000])
    for pattern in WIRE_PATTERNS:
        match = pattern.search(lead)
        if match:
            paragraphs = [p.strip().lower() for p in re.split(r"\n\s*\n", text) if p.strip()]
            basis = " ".join(paragraphs[:2])
            return match.group(0).lower() + ":" + hashlib.sha256(basis.encode()).hexdigest()[:16]
    return None


def _shingles(text: str, width: int = 5) -> set[str]:
    words = re.findall(r"\w+", text.casefold())
    return {" ".join(words[i:i + width]) for i in range(max(0, len(words) - width + 1))}


def text_similarity(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def cluster_sources(sources: list[dict[str, Any]], similarity_threshold: float = 0.72) -> list[dict[str, Any]]:
    parent = list(range(len(sources)))
    reasons: dict[tuple[int, int], set[str]] = defaultdict(set)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int, reason: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
        reasons[tuple(sorted((a, b)))].add(reason)

    urls = [normalize_url(str(s.get("url", ""))) for s in sources]
    wires = [wire_signature(str(s.get("text", ""))) for s in sources]
    for i in range(len(sources)):
        for j in range(i):
            if urls[i] and urls[i] == urls[j]:
                union(i, j, "normalized_url")
            if wires[i] and wires[i] == wires[j]:
                union(i, j, "wire_signature")
            if text_similarity(str(sources[i].get("text", "")), str(sources[j].get("text", ""))) >= similarity_threshold:
                union(i, j, "text_similarity")
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(sources)):
        groups[find(i)].append(i)
    output = []
    for cluster_number, members in enumerate(sorted(groups.values(), key=lambda x: x[0]), 1):
        representative = max(members, key=lambda i: (float(sources[i].get("quality_score", 0)), -i))
        weight = 1.0 / len(members)
        for i in members:
            item = dict(sources[i])
            item.update({
                "cluster_id": f"cluster-{cluster_number}",
                "representative": i == representative,
                "independence_score": 1.0 if i == representative else weight,
                "cluster_size": len(members),
                "cluster_reasons": sorted({r for pair, rs in reasons.items() if i in pair for r in rs}),
            })
            output.append(item)
    return output


def independent_evidence_sum(sources: list[dict[str, Any]]) -> float:
    return sum(float(s.get("independence_score", 1.0)) for s in sources)


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON array file")
    parser.add_argument("--threshold", type=float, default=0.72)
    args = parser.parse_args()
    data = json.loads(open(args.input, encoding="utf-8").read())
    print(json.dumps(cluster_sources(data, args.threshold), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
