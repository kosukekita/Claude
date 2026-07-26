from independence import cluster_sources, independent_evidence_sum, normalize_url, text_similarity


def test_url_normalization_and_duplicate_weight():
    assert normalize_url("HTTPS://Example.COM/a/?utm_source=x&b=2") == "https://example.com/a?b=2"
    sources = [
        {"id": "a", "url": "https://e.test/x?utm_source=z", "text": "first", "quality_score": .9},
        {"id": "b", "url": "https://e.test/x", "text": "different", "quality_score": .5},
    ]
    result = cluster_sources(sources)
    assert len({x["cluster_id"] for x in result}) == 1
    assert [x["independence_score"] for x in result] == [1.0, .5]


def test_wire_signature_and_text_similarity_are_cluster_paths():
    wire = ("NEW YORK (Reuters) — " + "same lead sentence with enough words " * 8)
    similar_a = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    similar_b = similar_a + " lambda"
    sources = [
        {"url": "https://a.test/1", "text": wire},
        {"url": "https://b.test/2", "text": wire},
        {"url": "https://c.test/3", "text": similar_a},
        {"url": "https://d.test/4", "text": similar_b},
    ]
    result = cluster_sources(sources, similarity_threshold=.7)
    assert result[0]["cluster_id"] == result[1]["cluster_id"]
    assert result[2]["cluster_id"] == result[3]["cluster_id"]
    assert "wire_signature" in result[0]["cluster_reasons"]
    assert "text_similarity" in result[2]["cluster_reasons"]
    assert independent_evidence_sum(result) < 4


def test_press_release_wire_signatures_are_detected():
    services = [
        "PR Newswire",
        "Business Wire",
        "GlobeNewswire",
        "Accesswire",
        "Newsfile",
    ]
    for service in services:
        body = f"NEW YORK, July 26, 2026 /{service}/ -- " + "shared release wording " * 20
        sources = [
            {"url": "https://publisher-a.test/release", "text": body},
            {"url": "https://publisher-b.test/release", "text": body},
        ]
        result = cluster_sources(sources)
        assert result[0]["cluster_id"] == result[1]["cluster_id"], service
        assert "wire_signature" in result[0]["cluster_reasons"], service
