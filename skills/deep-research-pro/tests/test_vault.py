import json

import pytest

from vault import init_vault, parse_note, search, write_claims, write_note


META = {
    "url": "https://example.org/a", "retrieved_at": "2026-07-26T00:00:00Z",
    "title": "A: study", "type": "primary", "utility_score": 0.8, "doi": "10.1/a",
}


def test_note_roundtrip_and_literal_search(tmp_path):
    path = write_note(tmp_path, "../unsafe name", META, "The exact quoted evidence is here.")
    assert path.parent == tmp_path / "research" / "sources"
    meta, body = parse_note(path.read_text(encoding="utf-8"))
    assert meta["title"] == "A: study"
    assert "exact quoted evidence" in body
    assert search(tmp_path, "QUOTED")[0]["matches"] == 1


def test_claims_without_verbatim_support_are_rejected(tmp_path):
    write_note(tmp_path, "s1", META, "Supported words.", overwrite=True)
    path, rejected = write_claims(tmp_path, "s1", [
        {"claim": "yes", "quoted_support": "Supported words."},
        {"claim": "no", "quoted_support": "invented"},
        {"claim": "missing"},
    ])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data["accepted"]) == 1
    assert rejected == data["rejected_without_verbatim_quote"] == 2


def test_required_frontmatter(tmp_path):
    with pytest.raises(ValueError):
        write_note(tmp_path, "x", {"url": "x"}, "body")
