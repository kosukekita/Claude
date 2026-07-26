#!/usr/bin/env python3
"""Academic metadata enrichment via OpenAlex first, then Crossref/PubMed."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Any, Callable

Transport = Callable[[str], dict[str, Any]]
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)


def normalize_doi(value: str) -> str:
    match = DOI_RE.search(urllib.parse.unquote(value))
    return match.group(0).rstrip(".,;)").lower() if match else ""


def http_json(url: str, *, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "deep-research-pro/1.0 (mailto:research@example.invalid)"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def openalex(doi: str, transport: Transport = http_json) -> dict[str, Any]:
    encoded = urllib.parse.quote(f"https://doi.org/{normalize_doi(doi)}", safe="")
    data = transport("https://api.openalex.org/works/" + encoded + "?select=id,doi,title,cited_by_count,is_retracted,type,publication_year")
    return {
        "provider": "openalex", "id": data.get("id"), "doi": normalize_doi(data.get("doi", doi)),
        "title": data.get("title"), "cited_by_count": int(data.get("cited_by_count") or 0),
        "is_retracted": bool(data.get("is_retracted")), "type": data.get("type"),
        "publication_year": data.get("publication_year"),
    }


def crossref(doi: str, transport: Transport = http_json) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(normalize_doi(doi), safe="")
    message = transport(url).get("message", {})
    updates = message.get("update-to") or []
    retracted = any(str(item.get("type", "")).lower() in {"retraction", "withdrawal"} for item in updates)
    return {"provider": "crossref", "doi": normalize_doi(doi), "is_retracted": retracted, "updates": updates}


def pubmed_retraction(doi: str, transport: Transport = http_json) -> dict[str, Any]:
    term = f'"{normalize_doi(doi)}"[DOI] AND "Retracted Publication"[Publication Type]'
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "retmode": "json", "term": term}
    )
    result = transport(url).get("esearchresult", {})
    return {"provider": "pubmed", "doi": normalize_doi(doi), "is_retracted": int(result.get("count", 0)) > 0,
            "pmids": result.get("idlist", [])}


def enrich_doi(doi: str, transport: Transport = http_json) -> dict[str, Any]:
    """Best-effort aggregation; a positive retraction signal always wins."""
    if not normalize_doi(doi):
        raise ValueError("invalid DOI")
    results, errors = [], []
    for query in (openalex, crossref, pubmed_retraction):
        try:
            results.append(query(doi, transport))
        except Exception as exc:
            errors.append({"provider": query.__name__, "error": str(exc)})
    if not results:
        raise RuntimeError("all enrichment providers failed: " + repr(errors))
    primary = next((r for r in results if r["provider"] == "openalex"), results[0])
    return {
        **primary,
        "doi": normalize_doi(doi),
        "is_retracted": any(r.get("is_retracted", False) for r in results),
        "retraction_signals": [r["provider"] for r in results if r.get("is_retracted")],
        "providers": results,
        "errors": errors,
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("doi")
    args = parser.parse_args(argv)
    print(json.dumps(enrich_doi(args.doi), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except Exception as exc:
        print(f"enrich: {exc}", file=sys.stderr)
        raise SystemExit(2)
