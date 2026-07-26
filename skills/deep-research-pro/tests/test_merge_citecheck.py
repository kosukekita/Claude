import json

import pytest

from merge_citecheck import merge, unresolved_count


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def setup_merge(tmp_path, verdicts):
    machine = tmp_path / "machine.json"
    verdict_dir = tmp_path / "verdicts"
    verdict_dir.mkdir()
    write_json(machine, {
        "sample": [{"pair_id": "p1"}, {"pair_id": "p2"}],
        "critical": [{"pair_id": "p3"}],
    })
    for index, verdict in enumerate(verdicts):
        write_json(verdict_dir / f"review-{index}.json", verdict)
    return machine, verdict_dir


def verdict(pair_id, value):
    return {"pair_id": pair_id, "verdict": value, "reason": "reason", "repair": "repair"}


def test_merge_maps_supported_to_pass_and_other_verdicts_to_fail(tmp_path):
    machine, verdict_dir = setup_merge(
        tmp_path, [verdict("p1", "supported"), verdict("p2", "partial")]
    )
    result = merge(machine, verdict_dir, "review", 2)
    assert [item["llm_verdict"] for item in result["sample"]] == ["pass", "fail"]
    assert result["critical"][0]["resolved"] is False
    assert unresolved_count(result) == 2
    js_unresolved = 1 + sum(
        item["llm_verdict"] != "pass" for item in result["sample"]
    )
    assert unresolved_count(result) == js_unresolved


@pytest.mark.parametrize("value", ["partial", "unsupported", "unclear", ""])
def test_merge_maps_every_non_supported_verdict_to_fail(tmp_path, value):
    machine, verdict_dir = setup_merge(
        tmp_path, [verdict("p1", "supported"), verdict("p2", value)]
    )
    result = merge(machine, verdict_dir, "review", 2)
    assert result["sample"][0]["llm_verdict"] == "pass"
    assert result["sample"][1]["llm_verdict"] == "fail"


def test_unresolved_count_adds_critical_and_non_passing_samples():
    data = {
        "critical": [{"pair_id": "p1"}, {"pair_id": "p2"}],
        "sample": [
            {"pair_id": "p3", "llm_verdict": "pass"},
            {"pair_id": "p4", "llm_verdict": "fail"},
            {"pair_id": "p5"},
        ],
    }
    assert unresolved_count(data) == 4


def test_merge_rejects_ids_that_do_not_match_deterministic_sample(tmp_path):
    machine, verdict_dir = setup_merge(
        tmp_path, [verdict("p1", "supported"), verdict("wrong", "supported")]
    )
    with pytest.raises(ValueError, match="deterministic sample"):
        merge(machine, verdict_dir, "review", 2)


def test_merge_rejects_duplicate_pair_ids(tmp_path):
    machine, verdict_dir = setup_merge(
        tmp_path, [verdict("p1", "supported"), verdict("p1", "supported")]
    )
    with pytest.raises(ValueError, match="duplicate pair_id"):
        merge(machine, verdict_dir, "review", 2)
