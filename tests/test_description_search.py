"""Unit tests for server.helpers.description_search."""

import asyncio

import pytest

from server.helpers.description_search import (
    DESCRIPTION_SEARCH_RESULT_LIMIT,
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
)
def test_normalize_search_text(raw: str, expected: str) -> None:
    assert normalize_search_text(raw) == expected


def test_canonicalize_token_maps_synonyms() -> None:
    # Canonical is lexicographically first in the hat group
    assert canonicalize_token("beanie") == canonicalize_token("hat")
    assert canonicalize_token("airpods") == canonicalize_token("earbuds")


def test_tokenize_search_text_empty() -> None:
    assert tokenize_search_text("") == []


def test_tokenize_search_text_applies_synonyms() -> None:
    tokens = tokenize_search_text("black beanie")
    assert "black" in tokens
    assert canonicalize_token("beanie") in tokens


def test_token_match_score_zero_for_empty() -> None:
    assert token_match_score([], ["a"]) == 0.0
    assert token_match_score(["a"], []) == 0.0


def test_description_similarity_score_empty() -> None:
    assert description_similarity_score("", "hello") == 0.0
    assert description_similarity_score("hello", "") == 0.0


def test_description_similarity_score_related_text_higher() -> None:
    q = "black wool hat"
    near = description_similarity_score(q, "black beanie")
    far = description_similarity_score(q, "blue umbrella")
    assert near > far


def test_description_similarity_score_typo_still_matches() -> None:
    assert description_similarity_score("airpods", "Apple airpords white case") >= 55


def test_rank_by_description_empty_query_returns_input() -> None:
    items = [{"description": "a", "date": "2024-01-01"}]
    assert rank_by_description(items, "") is items


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
