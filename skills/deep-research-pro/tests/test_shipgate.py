import json

from shipgate import _main, _sentences, inspect
from vault import write_claims, write_note


def setup_project(tmp_path, *, retracted=False):
    meta = {
        "url": "https://example.org/source", "retrieved_at": "2026-07-26T00:00:00Z",
        "title": "Source", "type": "primary", "utility_score": .9,
        "doi": "10.1234/source", "is_retracted": retracted,
    }
    write_note(tmp_path, "s1", meta, "The observed rate was 25%. Exact support words.")
    write_claims(tmp_path, "s1", [{"claim": "The observed rate was 25%.",
                                  "quoted_support": "The observed rate was 25%."}])
    return tmp_path / "research"


def config():
    return {"required_headings": ["Summary", "Evidence"], "min_words": 8, "max_words": 100,
            "min_citation_density": .5}


def test_all_checks_pass_in_one_gate(tmp_path):
    research = setup_project(tmp_path)
    report = tmp_path / "report.md"
    report.write_text(
        '# Summary\nThe result says "Exact support words." and the observed rate was 25%.[^s1]\n'
        "# Evidence\nThe evidence supports the reported result with direct source material.[^s1]\n\n[^s1]: s1\n",
        encoding="utf-8",
    )
    result = inspect(report, research, config())
    assert result["passed"], result
    assert result["metrics"]["quoted_spans"] == 1


def test_hallucinated_quote_fails(tmp_path):
    research = setup_project(tmp_path)
    report = tmp_path / "report.md"
    report.write_text('# Summary\nA sentence contains "invented quotation" with a citation.[^s1]\n'
                      "# Evidence\nAnother sufficiently long evidence sentence is here.[^s1]\n\n[^s1]: s1", encoding="utf-8")
    result = inspect(report, research, {**config(), "min_words": 1})
    assert not result["passed"]
    assert "verbatim_quotes" in {x["check"] for x in result["failures"]}


def test_retracted_citation_fails_and_exit_code_is_nonzero(tmp_path, capsys):
    research = setup_project(tmp_path, retracted=True)
    report = tmp_path / "report.md"
    report.write_text("# Summary\nThe observed rate was 25% in the cited study.[^s1]\n"
                      "# Evidence\nThis source is directly cited as supporting evidence.[^s1]\n\n[^s1]: s1", encoding="utf-8")
    config_file = tmp_path / "gate.json"
    config_file.write_text(json.dumps({**config(), "min_words": 1}), encoding="utf-8")
    code = _main([str(report), "--research", str(research), "--config", str(config_file)])
    assert code == 1
    output = json.loads(capsys.readouterr().out)
    assert "retracted_sources" in {x["check"] for x in output["failures"]}


def test_heading_order_and_unresolved_citation_fail(tmp_path):
    research = setup_project(tmp_path)
    report = tmp_path / "report.md"
    report.write_text("# Evidence\nThis is evidence with an unknown source citation.[^ghost]\n"
                      "# Summary\nThis comes second and therefore violates the contract.[^s1]\n\n"
                      "[^ghost]: missing\n[^s1]: s1", encoding="utf-8")
    checks = {x["check"] for x in inspect(report, research, {**config(), "min_words": 1})["failures"]}
    assert {"required_headings", "citecheck_unresolved"} <= checks


def test_note_without_claims_passes_and_is_reported_as_unverified(tmp_path):
    meta = {
        "url": "https://example.org/unverified", "retrieved_at": "2026-07-27T00:00:00Z",
        "title": "Unverified source", "type": "primary", "utility_score": .7,
    }
    write_note(tmp_path, "src-1", meta, "A source body with no extracted claims.")
    report = tmp_path / "report.md"
    report.write_text(
        "# Summary\nThis statement cites an existing source note [[source:src-1]].\n"
        "# Evidence\nThis second statement cites the same existing note [[source:src-1]].",
        encoding="utf-8",
    )
    result = inspect(report, tmp_path / "research", {**config(), "min_words": 1})
    assert result["passed"], result
    assert result["metrics"]["unverified_citations"] == 2


def test_citation_density_sentence_split_does_not_break_decimal_or_marker():
    first = "The measured change was 12.4% in the treatment arm.[^s1]"
    second = "This uncited sentence is long enough to be included."
    assert _sentences(first + " " + second) == [first, second]


def test_citation_density_split_preserves_abbreviations_and_normal_boundary():
    first = (
        "Dr. Smith reported approx. 68.0% in the U.S. cohort, "
        "see Fig. 2 and Smith et al. 2024.[^s1]"
    )
    second = "Longer follow-up was not assessed."
    assert _sentences(first + " " + second) == [first, second]
