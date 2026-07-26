#!/usr/bin/env python3
"""Citation-pair extraction, mechanical triage, and deterministic sampling."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from sentence_split import split_sentences

FOOTNOTE_DEF = re.compile(r"^\[\^([^\]]+)\]:\s*(.+)$", re.M)
CITATION = re.compile(r"\[\^([^\]]+)\]|\[\[source:([^\]]+)\]\]|\[[^\]]+\]\((https?://[^)]+)\)")
NUMBER = re.compile(
    r"(?<!\w)[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:[.,]\d+)?|\.\d+)%?"
)


def _sentences(text: str) -> list[str]:
    text = re.sub(r"^\[\^[^\]]+\]:.*$", "", text, flags=re.M)
    return [chunk for chunk in split_sentences(text, CITATION)
            if not chunk.lstrip().startswith("#")]


def extract_pairs(report: str) -> list[dict[str, Any]]:
    definitions = {key: value.strip() for key, value in FOOTNOTE_DEF.findall(report)}
    pairs: list[dict[str, Any]] = []
    for index, sentence in enumerate(_sentences(report)):
        for match in CITATION.finditer(sentence):
            footnote, source_id, url = match.groups()
            ref = footnote or source_id or url
            pairs.append({
                "pair_id": f"p{len(pairs) + 1}",
                "sentence_index": index,
                "sentence": sentence,
                "citation": match.group(0),
                "reference": ref,
                "resolved_reference": definitions.get(ref, url or source_id or ""),
            })
    return pairs


def load_claim_index(research: str | Path) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for path in sorted((Path(research) / "claims").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        claims = data.get("accepted", [])
        index[path.stem.casefold()] = claims
        source_id = str(data.get("source_id", path.stem)).casefold()
        index[source_id] = claims
    # Resolve inline URL/DOI citations as aliases of the corresponding note id.
    from vault import read_note
    for path in sorted((Path(research) / "sources").glob("*.md")):
        meta, _ = read_note(path)
        claims = index.get(path.stem.casefold(), [])
        for alias in (meta.get("url"), meta.get("doi")):
            if alias:
                index[str(alias).casefold()] = claims
    return index


def load_source_index(research: str | Path) -> set[str]:
    """Return note ids and citation aliases for every source note in the vault."""
    from vault import read_note

    aliases: set[str] = set()
    for path in sorted((Path(research) / "sources").glob("*.md")):
        meta, _ = read_note(path)
        aliases.add(path.stem.casefold())
        for alias in (meta.get("url"), meta.get("doi")):
            if alias:
                aliases.add(str(alias).casefold())
    return aliases


def _candidate_claims(pair: dict[str, Any], claims: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    haystack = (pair["reference"] + " " + pair["resolved_reference"]).casefold()
    matched = [items for key, items in claims.items() if key in haystack]
    return [claim for items in matched for claim in items]


def _resolves_to_source(pair: dict[str, Any], sources: set[str]) -> bool:
    haystack = (pair["reference"] + " " + pair["resolved_reference"]).casefold()
    return any(alias in haystack for alias in sources)


def triage_pairs(
    pairs: list[dict[str, Any]],
    claims: dict[str, list[dict[str, Any]]],
    sources: set[str] | None = None,
) -> list[dict[str, Any]]:
    results = []
    sources = sources or set()
    for pair in pairs:
        candidates = _candidate_claims(pair, claims)
        status, reason, severity = "llm_review", "semantic support requires review", "medium"
        if not candidates:
            if _resolves_to_source(pair, sources):
                status = "unverified"
                reason = "citation resolves to a vault note with no accepted claims"
                severity = "warning"
            else:
                status, reason, severity = "unresolved", "citation resolves to no vault note", "critical"
        else:
            sentence_numbers = set(NUMBER.findall(pair["sentence"]))
            for claim in candidates:
                quote = str(claim.get("quoted_support", ""))
                statement = str(claim.get("claim", claim.get("text", "")))
                claim_numbers = set(NUMBER.findall(quote + " " + statement))
                if quote and quote in pair["sentence"]:
                    status, reason, severity = "auto_pass", "verbatim support appears in sentence", "none"
                    break
                if sentence_numbers and sentence_numbers <= claim_numbers:
                    status, reason, severity = "auto_pass", "all sentence numbers occur in cited claim", "none"
                    break
        results.append({**pair, "status": status, "reason": reason, "severity": severity})
    return results


def deterministic_sample(items: list[dict[str, Any]], size: int) -> list[dict[str, Any]]:
    """Stable across processes and resume; does not use process-randomized hash()."""
    eligible = [item for item in items if item.get("status") == "llm_review"]
    ranked = sorted(eligible, key=lambda item: (
        hashlib.sha256((item["sentence"] + "\0" + item["citation"]).encode("utf-8")).hexdigest(),
        item["pair_id"],
    ))
    return ranked[:max(0, size)]


def run(report_path: str | Path, research: str | Path, sample_size: int = 10) -> dict[str, Any]:
    report = Path(report_path).read_text(encoding="utf-8")
    results = triage_pairs(
        extract_pairs(report),
        load_claim_index(research),
        load_source_index(research),
    )
    critical = [item for item in results if item["severity"] == "critical"]
    unverified = [item for item in results if item["status"] == "unverified"]
    return {
        "pairs": results,
        "sample": deterministic_sample(results, sample_size),
        "critical": critical,
        "critical_count": len(critical),
        "unverified": unverified,
        "unverified_count": len(unverified),
        "counts": {status: sum(item["status"] == status for item in results)
                   for status in ("auto_pass", "llm_review", "unverified", "unresolved")},
    }


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--research", default="research")
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run(args.report, args.research, args.sample_size)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(encoded, encoding="utf-8")
        summary = {
            "output": Path(args.output).as_posix(),
            "counts": result["counts"],
            "critical_count": len(result["critical"]),
            "unverified_count": result["unverified_count"],
            "sample": [{"pair_id": item["pair_id"]} for item in result["sample"]],
        }
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(encoded, end="")
    return 1 if result["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(_main())
