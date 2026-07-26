from enrich import crossref, enrich_doi, normalize_doi, openalex, pubmed_retraction


def fixture_transport(url):
    if "openalex" in url:
        return {"id": "W1", "doi": "https://doi.org/10.1234/ABC", "title": "Study",
                "cited_by_count": 42, "is_retracted": False, "type": "article", "publication_year": 2020}
    if "crossref" in url:
        return {"message": {"update-to": [{"type": "retraction", "DOI": "10.1234/abc"}]}}
    return {"esearchresult": {"count": "0", "idlist": []}}


def test_openalex_first_shape_and_aggregate_retraction():
    result = enrich_doi("https://doi.org/10.1234/ABC", fixture_transport)
    assert result["cited_by_count"] == 42
    assert result["is_retracted"] is True
    assert result["retraction_signals"] == ["crossref"]
    assert result["providers"][0]["provider"] == "openalex"


def test_provider_parsers():
    assert normalize_doi("doi:10.5555/X.Y.") == "10.5555/x.y"
    assert openalex("10.1234/abc", fixture_transport)["title"] == "Study"
    assert crossref("10.1234/abc", fixture_transport)["is_retracted"]
    assert not pubmed_retraction("10.1234/abc", fixture_transport)["is_retracted"]
