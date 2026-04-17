"""Unit tests for server.helpers.description_search."""

import asyncio
import re

import pytest

from server.helpers.description_search import (
    DESCRIPTION_SEARCH_RESULT_LIMIT,
    _prefilter_regex_alternates,
    build_description_prefilter,
    canonicalize_token,
    description_similarity_score,
    normalize_search_text,
    rank_by_description,
    rank_by_description_async,
    token_match_score,
    tokenize_search_text,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  Black  Beanie!!!  ", "black beanie"),
        ("", ""),
        ("UPPER", "upper"),
    ],
    ids=[
        "normalizes_whitespace_and_strips_punctuation",
        "empty_string",
        "lowercases_uppercase",
    ],
)
def test_normalize_search_text(raw: str, expected: str) -> None:
    assert normalize_search_text(raw) == expected


@pytest.mark.parametrize(
    "a,b",
    [
        ("beanie", "hat"),
        ("airpods", "earbuds"),
    ],
    ids=[
        "hat_synonym_group_maps_to_same_canonical",
        "earbuds_synonym_group_maps_to_same_canonical",
    ],
)
def test_canonicalize_token_maps_synonyms(a: str, b: str) -> None:
    assert canonicalize_token(a) == canonicalize_token(b)


@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        pytest.param("", [], id="empty_input_yields_no_tokens"),
        pytest.param(
            "black beanie",
            ["black", "beanie"],
            id="tokens_use_canonical_synonym_forms",
        ),
    ],
)
def test_tokenize_search_text(text: str, expected_tokens: list[str]) -> None:
    assert tokenize_search_text(text) == expected_tokens


@pytest.mark.parametrize(
    "query_tokens,text_tokens",
    [
        ([], ["a"]),
        (["a"], []),
    ],
    ids=["empty_query_tokens_scores_zero", "empty_text_tokens_scores_zero"],
)
def test_token_match_score_zero_for_empty(
    query_tokens: list[str], text_tokens: list[str]
) -> None:
    assert token_match_score(query_tokens, text_tokens) == 0.0


def test_token_match_score_averages_best_ratios() -> None:
    """Single query token: score equals best fuzzy ratio against text tokens."""
    score = token_match_score(["cat"], ["bat", "car"])
    assert 0.0 < score <= 100.0


def test_prefilter_regex_alternates_expands_synonyms_sorted_deduped() -> None:
    """'hat' expands to synonym set; result sorted unique tokens."""
    alts = _prefilter_regex_alternates("hat")
    assert alts == sorted(set(alts))
    assert "hat" in alts
    assert "beanie" in alts


def test_prefilter_regex_alternates_unknown_token_only_self() -> None:
    alts = _prefilter_regex_alternates("xyzzy123")
    assert alts == ["xyzzy123"]


@pytest.mark.parametrize(
    "query,text",
    [
        ("", "hello"),
        ("hello", ""),
    ],
    ids=["empty_query_returns_zero", "empty_text_returns_zero"],
)
def test_description_similarity_score_empty(query: str, text: str) -> None:
    assert description_similarity_score(query, text) == 0.0


def test_description_similarity_score_related_text_higher() -> None:
    q = "black wool hat"
    near = description_similarity_score(q, "black beanie")
    far = description_similarity_score(q, "blue umbrella")
    assert near > far


def test_description_similarity_score_typo_still_matches() -> None:
    assert description_similarity_score("airpods", "Apple airpords white case") >= 55


@pytest.mark.parametrize(
    "description_query",
    [
        pytest.param("", id="empty_query_returns_original_list"),
        pytest.param("   ", id="whitespace_only_query_returns_original_list"),
    ],
)
def test_rank_by_description_blank_query_returns_input(description_query: str) -> None:
    items = [{"description": "a", "date": "2024-01-01"}]
    assert rank_by_description(items, description_query) is items


@pytest.mark.parametrize(
    "description_query",
    [
        pytest.param("", id="empty_query_yields_no_prefilter"),
        pytest.param("   ", id="whitespace_only_yields_no_prefilter"),
    ],
)
def test_build_description_prefilter_blank_query(description_query: str) -> None:
    assert build_description_prefilter(description_query) is None


def test_build_description_prefilter_uses_token_regex() -> None:
    prefilter = build_description_prefilter("Apple AirPods case")
    assert prefilter is not None
    assert "$regex" in prefilter["description"]
    assert "airpods" in prefilter["description"]["$regex"]
    assert prefilter["description"]["$options"] == "i"


def test_build_description_prefilter_hat_matches_raw_and_synonym_descriptions() -> None:
    """Prefilter must not map hat->beanie only; raw descriptions may say 'hat'."""
    prefilter = build_description_prefilter("hat")
    assert prefilter is not None
    pattern = prefilter["description"]["$regex"]
    assert "hat" in pattern
    compiled = re.compile(pattern, re.IGNORECASE)
    assert compiled.search("red wool hat")
    assert compiled.search("black beanie")


def test_rank_by_description_orders_by_relevance_then_date() -> None:
    items = [
        {"_id": 1, "description": "red umbrella", "date": "2024-02-01"},
        {"_id": 2, "description": "Apple AirPods case", "date": "2024-01-01"},
        {"_id": 3, "description": "math textbook", "date": "2024-03-01"},
    ]
    ranked = rank_by_description(items, "airpods")
    assert ranked
    assert ranked[0]["_id"] == 2


def test_rank_by_description_respects_result_limit() -> None:
    items = [
        {"description": f"water bottle number {i}", "date": "2024-01-01"}
        for i in range(DESCRIPTION_SEARCH_RESULT_LIMIT + 5)
    ]
    ranked = rank_by_description(items, "water bottle")
    assert len(ranked) <= DESCRIPTION_SEARCH_RESULT_LIMIT


def test_rank_by_description_custom_field() -> None:
    items = [
        {"title": "hidden", "description": "zzz"},
        {"title": "find me airpods", "description": "zzz"},
    ]
    ranked = rank_by_description(items, "airpods", description_field="title")
    assert len(ranked) == 1
    assert "airpods" in ranked[0]["title"]


def test_rank_by_description_async_matches_sync() -> None:
    items = [
        {"description": "coat", "date": "2024-01-01"},
        {"description": "AirPods Pro", "date": "2024-01-02"},
    ]

    async def _run() -> None:
        async_result = await rank_by_description_async(items, "airpods")
        sync_result = rank_by_description(items, "airpods")
        assert async_result == sync_result

    asyncio.run(_run())
