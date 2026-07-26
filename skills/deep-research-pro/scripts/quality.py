#!/usr/bin/env python3
"""Transparent composite source-quality scoring."""
from __future__ import annotations

import argparse
import json
import math
from typing import Any

TYPE_PRIOR = {
    "systematic-review": 0.95, "meta-analysis": 0.95, "randomized-trial": 0.9,
    "cohort": 0.75, "government": 0.85, "primary": 0.8, "preprint": 0.5,
    "news": 0.4, "opinion": 0.25, "unknown": 0.35,
}
RETRACTION_FLOOR = 0.0


def quality_score(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("is_retracted"):
        return {"quality_score": RETRACTION_FLOOR, "components": {"retracted": True}}
    prior = TYPE_PRIOR.get(str(source.get("type", "unknown")).lower(), TYPE_PRIOR["unknown"])
    citations = min(1.0, math.log1p(max(0, int(source.get("cited_by_count", 0)))) / math.log(501))
    transparency = sum(bool(source.get(k)) for k in ("doi", "authors", "published_at", "methods")) / 4
    recency = max(0.0, min(1.0, float(source.get("recency_score", 0.5))))
    peer = 1.0 if source.get("peer_reviewed") else 0.35
    score = 0.35 * prior + 0.2 * citations + 0.2 * transparency + 0.15 * peer + 0.1 * recency
    return {"quality_score": round(score, 4), "components": {
        "type_prior": prior, "citations": citations, "transparency": transparency,
        "peer_review": peer, "recency": recency, "retracted": False,
    }}


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="source JSON or JSON file")
    args = parser.parse_args()
    try:
        source = json.loads(args.input)
    except json.JSONDecodeError:
        source = json.loads(open(args.input, encoding="utf-8").read())
    print(json.dumps(quality_score(source), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
