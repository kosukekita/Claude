from quality import RETRACTION_FLOOR, quality_score


def test_retraction_forces_floor():
    result = quality_score({"type": "meta-analysis", "cited_by_count": 1000, "is_retracted": True})
    assert result["quality_score"] == RETRACTION_FLOOR


def test_composite_score_is_bounded_and_transparent():
    result = quality_score({"type": "primary", "cited_by_count": 10, "doi": "x",
                            "authors": ["A"], "published_at": "2024", "methods": "RCT",
                            "peer_reviewed": True, "recency_score": .8})
    assert 0 < result["quality_score"] <= 1
    assert set(result["components"]) >= {"type_prior", "citations", "transparency"}
