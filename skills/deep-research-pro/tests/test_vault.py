import json

import pytest

from vault import _main, init_vault, parse_note, search, write_claims, write_note


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


def test_cli_writes_note_and_claims_and_reports_rejections(tmp_path, capsys):
    body_file = tmp_path / "body.txt"
    body_file.write_text("The exact result was 42%.", encoding="utf-8")
    assert _main([
        "write-note", "source-cli", "--project", str(tmp_path), "--body", str(body_file),
        "--url", "https://example.org/cli", "--retrieved-at", "2026-07-27T00:00:00Z",
        "--title", "CLI source", "--type", "primary", "--utility-score", "0.8",
    ]) == 0
    note_result = json.loads(capsys.readouterr().out)
    assert (tmp_path / "research" / "sources" / "source-cli.md").is_file()
    assert note_result["path"].endswith("/research/sources/source-cli.md")

    claims_file = tmp_path / "claims.json"
    claims_file.write_text(json.dumps([
        {"claim": "supported", "quoted_support": "exact result was 42%"},
        {"claim": "invented", "quoted_support": "not present in source"},
    ]), encoding="utf-8")
    assert _main([
        "write-claims", "source-cli", str(claims_file), "--project", str(tmp_path),
    ]) == 0
    claim_result = json.loads(capsys.readouterr().out)
    assert claim_result["accepted"] == 1
    assert claim_result["rejected_without_verbatim_quote"] == 1
