
from app.agents.citation_validator import validate_citations


def test_valid_citation_is_accepted():
    result = validate_citations(
        "The report states three findings [E1].",
        {"E1", "E2"},
    )

    assert result.valid is True
    assert result.cited_ids == ["E1"]
    assert result.invalid_ids == []
    assert result.missing_citation is False


def test_unknown_citation_is_flagged():
    result = validate_citations(
        "The report states three findings [E9].",
        {"E1", "E2"},
    )

    assert result.valid is False
    assert result.invalid_ids == ["E9"]


def test_missing_citation_is_flagged():
    result = validate_citations(
        "The report states three findings.",
        {"E1"},
    )

    assert result.valid is False
    assert result.missing_citation is True


def test_duplicate_citations_are_deduplicated():
    result = validate_citations(
        "Finding one [E1]. Finding two [E1].",
        {"E1"},
    )

    assert result.valid is True
    assert result.cited_ids == ["E1"]


def test_uncited_bullet_is_flagged():
    answer = (
        "- Patient age: 50 years\n"
        "- Sex: Male\n"
        "- Report type: Training only [E1]"
    )

    result = validate_citations(answer, {"E1"})

    assert result.valid is False
    assert result.missing_citation is True


def test_each_cited_bullet_is_accepted():
    answer = (
        "- Patient age: 50 years [E1]\n"
        "- Sex: Male [E1]"
    )

    result = validate_citations(answer, {"E1"})

    assert result.valid is True
    assert result.missing_citation is False


def test_mixed_valid_and_invalid_citations_are_flagged():
    answer = (
        "- Patient age: 50 years [E1]\n"
        "- Sex: Male [E99]"
    )

    result = validate_citations(answer, {"E1"})

    assert result.valid is False
    assert result.invalid_ids == ["E99"]