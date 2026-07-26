"""Sentence splitting shared by citation triage and the release gate."""
from __future__ import annotations

import re


_CITATION_TOKEN = re.compile(r"\ue000\d+\ue001")
_DECIMAL_POINT = "\ue100"
_ABBREVIATION_POINT = "\ue101"
_BOUNDARY = "\ue102"
_ABBREVIATION = re.compile(
    r"(?i)\b(?:et\s+al|fig|no|vs|i\.e|e\.g|dr|approx)\.|"
    r"(?<![A-Za-z])(?:[A-Za-z]\.){2,}"
)


def split_sentences(
    text: str,
    citation_pattern: re.Pattern[str],
) -> list[str]:
    """Split prose without breaking decimals, common abbreviations, or citations."""
    citations: list[str] = []

    def hold_citation(match: re.Match[str]) -> str:
        citations.append(match.group(0))
        return f"\ue000{len(citations) - 1}\ue001"

    held = citation_pattern.sub(hold_citation, text)
    held = re.sub(r"(?<=\d)\.(?=\d)", _DECIMAL_POINT, held)
    held = _ABBREVIATION.sub(
        lambda match: match.group(0).replace(".", _ABBREVIATION_POINT),
        held,
    )

    citation = _CITATION_TOKEN.pattern
    trailing_citations = rf"(?:[ \t]*{citation})*"
    held = re.sub(rf"([。！？]+{trailing_citations})", rf"\1{_BOUNDARY}", held)
    held = re.sub(
        rf"([.!?]+{trailing_citations})(?=[ \t]*(?:\r?\n|$)|[ \t]+\S)",
        rf"\1{_BOUNDARY}",
        held,
    )
    chunks = re.split(rf"{_BOUNDARY}|\r?\n+", held)

    def restore(chunk: str) -> str:
        chunk = chunk.replace(_DECIMAL_POINT, ".").replace(_ABBREVIATION_POINT, ".")
        return _CITATION_TOKEN.sub(
            lambda match: citations[int(match.group(0)[1:-1])],
            chunk,
        )

    return [restore(chunk).strip() for chunk in chunks if chunk.strip()]
