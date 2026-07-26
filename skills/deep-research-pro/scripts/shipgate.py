#!/usr/bin/env python3
"""The single, non-bypassable release gate for deep-research-pro reports."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from citecheck import run as run_citecheck
from sentence_split import split_sentences
from vault import iter_notes

QUOTED = re.compile(r'"([^"\n]+)"|“([^”\n]+)”|「([^」\n]+)」|『([^』\n]+)』')
CITATION = re.compile(r"\[\^[^\]]+\]|\[\[source:[^\]]+\]\]|\[[^\]]+\]\(https?://[^)]+\)")


def _words(text: str) -> int:
    clean = re.sub(r"```.*?```|`[^`]*`|[#>*_\[\]()]", " ", text, flags=re.S)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[\u3040-\u30ff\u3400-\u9fff]+", clean))


def _sentences(text: str) -> list[str]:
    return [sentence for sentence in split_sentences(text, CITATION)
            if len(sentence) >= 20 and not sentence.lstrip().startswith(("#", "[^"))]


def _heading_positions(report: str, headings: list[str]) -> list[int]:
    positions = []
    for heading in headings:
        match = re.search(rf"(?m)^#{{1,6}}\s+{re.escape(heading)}\s*$", report)
        positions.append(match.start() if match else -1)
    return positions


def _cited(meta: dict[str, Any], path: Path, report: str) -> bool:
    needles = [path.stem, str(meta.get("url", "")), str(meta.get("doi", ""))]
    folded = report.casefold()
    return any(n and n.casefold() in folded for n in needles)


def inspect(report_path: str | Path, research: str | Path, config: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    report_file = Path(report_path)
    if not report_file.is_file():
        return {"passed": False, "failures": [{"check": "report_exists", "message": str(report_file)}]}
    report = report_file.read_text(encoding="utf-8")
    notes = list(iter_notes(Path(research).parent))
    corpus = "\n".join(body for _, _, body in notes)

    headings = list(config.get("required_headings", []))
    positions = _heading_positions(report, headings)
    if any(p < 0 for p in positions) or positions != sorted(positions):
        failures.append({"check": "required_headings", "message": "missing or out of order: " + repr(headings)})

    word_count = _words(report)
    minimum, maximum = int(config.get("min_words", 1)), int(config.get("max_words", 10**9))
    if not minimum <= word_count <= maximum:
        failures.append({"check": "word_count", "message": f"{word_count} not in [{minimum}, {maximum}]"})

    sentences = _sentences(report)
    cited_sentences = sum(bool(CITATION.search(sentence)) for sentence in sentences)
    density = cited_sentences / len(sentences) if sentences else 0.0
    if density < float(config.get("min_citation_density", 0.0)):
        failures.append({"check": "citation_density", "message": f"{density:.4f} below minimum"})

    missing_quotes = sorted({next(part for part in match.groups() if part is not None).strip()
                             for match in QUOTED.finditer(report)
                             if next(part for part in match.groups() if part is not None).strip() not in corpus})
    if missing_quotes:
        failures.append({"check": "verbatim_quotes", "message": json.dumps(missing_quotes, ensure_ascii=False)})

    retracted = []
    for path, meta, _ in notes:
        if meta.get("is_retracted") and _cited(meta, path, report):
            explicitly_authorized = bool(meta.get("authorized_retracted")) and re.search(
                rf"(?i)(retract(?:ed|ion)|撤回).{{0,120}}{re.escape(path.stem)}|"
                rf"{re.escape(path.stem)}.{{0,120}}(retract(?:ed|ion)|撤回)", report)
            if not explicitly_authorized:
                retracted.append(path.stem)
    if retracted:
        failures.append({"check": "retracted_sources", "message": ", ".join(retracted)})

    cite_result = run_citecheck(report_file, research, int(config.get("cite_sample_size", 10)))
    check_file = config.get("citecheck_result")
    if check_file:
        saved = json.loads(Path(check_file).read_text(encoding="utf-8"))
        unresolved_llm = [x for x in saved.get("sample", []) if x.get("llm_verdict") not in ("pass", "resolved")]
        saved_critical = [x for x in saved.get("critical", []) if not x.get("resolved")]
        if unresolved_llm or saved_critical:
            failures.append({"check": "citecheck_findings", "message": "saved cite-check has unresolved findings"})
    if cite_result["critical"]:
        failures.append({"check": "citecheck_unresolved", "message": f"{len(cite_result['critical'])} unresolved citation(s)"})

    return {
        "passed": not failures, "failures": failures, "metrics": {
            "word_count": word_count, "citation_density": round(density, 4),
            "quoted_spans": len(list(QUOTED.finditer(report))), "notes": len(notes),
            "citation_pairs": len(cite_result["pairs"]),
            "unverified_citations": cite_result["unverified_count"],
        },
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run every release check; exit 0 only on pass.")
    parser.add_argument("report")
    parser.add_argument("--research", default="research")
    parser.add_argument("--config", help="JSON config file")
    parser.add_argument("--required-heading", action="append", default=[])
    parser.add_argument("--min-words", type=int, default=1)
    parser.add_argument("--max-words", type=int, default=10**9)
    parser.add_argument("--min-citation-density", type=float, default=0.2)
    parser.add_argument("--citecheck-result")
    args = parser.parse_args(argv)
    config = json.loads(Path(args.config).read_text(encoding="utf-8")) if args.config else {
        "required_headings": args.required_heading, "min_words": args.min_words,
        "max_words": args.max_words, "min_citation_density": args.min_citation_density,
        "citecheck_result": args.citecheck_result,
    }
    result = inspect(args.report, args.research, config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except Exception as exc:
        print(json.dumps({"passed": False, "failures": [{"check": "gate_error", "message": str(exc)}]},
                         ensure_ascii=False, indent=2))
        raise SystemExit(2)
