import json

from citecheck import NUMBER, _sentences, deterministic_sample, extract_pairs, run


def make_claim(research, source="s1"):
    (research / "claims").mkdir(parents=True)
    (research / "claims" / f"{source}.json").write_text(json.dumps({
        "source_id": source, "accepted": [
            {"claim": "The rate was 25%.", "quoted_support": "The observed rate was 25%."}
        ]
    }), encoding="utf-8")


def test_extract_and_triage(tmp_path):
    research = tmp_path / "research"
    make_claim(research)
    report = tmp_path / "report.md"
    report.write_text("The measured rate was 25%.[^s1]\n\n[^s1]: s1", encoding="utf-8")
    result = run(report, research)
    assert result["counts"]["auto_pass"] == 1
    assert not result["critical"]


def test_unresolved_is_critical(tmp_path):
    research = tmp_path / "research"
    make_claim(research)
    report = tmp_path / "report.md"
    report.write_text("This assertion has enough words to form a sentence.[^ghost]\n\n[^ghost]: nowhere", encoding="utf-8")
    assert run(report, research)["critical"][0]["severity"] == "critical"


def test_existing_note_without_claims_is_counted_as_unverified_not_critical(tmp_path):
    research = tmp_path / "research"
    (research / "sources").mkdir(parents=True)
    (research / "sources" / "src-1.md").write_text(
        '---\nurl: "https://example.org/src-1"\n---\nSource body.\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.md"
    report.write_text(
        "This supported statement cites an existing source note [[source:src-1]].",
        encoding="utf-8",
    )
    result = run(report, research)
    assert not result["critical"]
    assert result["unverified_count"] == result["counts"]["unverified"] == 1
    assert result["pairs"][0]["severity"] == "warning"


def test_sample_is_deterministic_and_order_independent():
    items = [{"pair_id": str(i), "sentence": f"sentence {i}", "citation": f"[^{i}]",
              "status": "llm_review"} for i in range(12)]
    first = [x["pair_id"] for x in deterministic_sample(items, 5)]
    second = [x["pair_id"] for x in deterministic_sample(list(reversed(items)), 5)]
    assert first == second


def test_inline_url_resolves_through_note_alias(tmp_path):
    research = tmp_path / "research"
    make_claim(research)
    (research / "sources").mkdir()
    (research / "sources" / "s1.md").write_text(
        '---\nurl: "https://example.org/paper"\ndoi: "10.1/x"\n---\nThe observed rate was 25%.\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.md"
    report.write_text("The measured rate was 25%.[paper](https://example.org/paper)", encoding="utf-8")
    assert run(report, research)["counts"]["auto_pass"] == 1


def test_decimal_sentence_stays_whole_and_verbatim_quote_auto_passes(tmp_path):
    research = tmp_path / "research"
    (research / "claims").mkdir(parents=True)
    (research / "claims" / "note-a.json").write_text(json.dumps({
        "source_id": "note-a",
        "accepted": [{
            "claim": "Lean mass declined during the trial.",
            "quoted_support": "a 12.4% reduction in lean mass over 68 weeks",
        }],
    }), encoding="utf-8")
    sentence = (
        'The trial reported "a 12.4% reduction in lean mass over 68 weeks" '
        "in the treatment arm [[source:note-a]]."
    )
    report = tmp_path / "report.md"
    report.write_text(sentence, encoding="utf-8")

    assert _sentences(sentence) == [sentence]
    result = run(report, research)
    assert result["counts"]["auto_pass"] == 1
    assert result["pairs"][0]["reason"] == "verbatim support appears in sentence"


def test_sentence_split_preserves_numbers_abbreviations_japanese_and_citations():
    text = (
        "Values were 0.05, 1,234.5, and 68.0% in the U.S. trial by Dr. Smith et al. "
        "See Fig. 2 vs. Fig. 3, No. 4, i.e. the approx. comparison e.g. baseline.[^1] "
        "次の文です。さらに確認します！最後です？ "
        "A linked finding ends here.[paper](https://example.org/a.b) Final sentence."
    )
    assert _sentences(text) == [
        ("Values were 0.05, 1,234.5, and 68.0% in the U.S. trial by Dr. Smith et al. "
         "See Fig. 2 vs. Fig. 3, No. 4, i.e. the approx. comparison e.g. baseline.[^1]"),
        "次の文です。",
        "さらに確認します！",
        "最後です？",
        "A linked finding ends here.[paper](https://example.org/a.b)",
        "Final sentence.",
    ]
    assert NUMBER.findall("Values: 12.4%, 0.05, and 1,234.5.") == [
        "12.4%", "0.05", "1,234.5"
    ]


def test_rework_reproduction_splits_into_exactly_two_sentences():
    text = (
        'The trial reported "a 12.4% reduction in lean mass over 68 weeks" '
        "in the treatment arm [[source:note-a]]. Longer follow-up "
        "(see Smith et al. 2024, U.S. cohort) was not assessed [[source:note-a]]."
    )
    assert _sentences(text) == [
        ('The trial reported "a 12.4% reduction in lean mass over 68 weeks" '
         "in the treatment arm [[source:note-a]]."),
        ("Longer follow-up (see Smith et al. 2024, U.S. cohort) was not assessed "
         "[[source:note-a]]."),
    ]


def test_run_reports_critical_count(tmp_path):
    research = tmp_path / "research"
    make_claim(research)
    report = tmp_path / "report.md"
    report.write_text("A dangling citation remains unresolved.[^ghost]\n\n[^ghost]: missing", encoding="utf-8")
    result = run(report, research)
    assert result["critical_count"] == len(result["critical"]) == 1
