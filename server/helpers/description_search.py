"""
Fuzzy description search for LAF, inventory, and similar item lookups.

Pure helpers plus async ranking via asyncio.to_thread so callers stay non-blocking.
"""

import re
from asyncio import to_thread
from typing import Any

from rapidfuzz import fuzz

DESCRIPTION_SEARCH_CANDIDATE_LIMIT = 300
DESCRIPTION_SEARCH_RESULT_LIMIT = 30
DESCRIPTION_MATCH_THRESHOLD = 55

SYNONYM_GROUPS = [
    {"hat", "beanie", "beenie", "cap", "toque", "headwear"},
    {"jacket", "coat", "hoodie", "sweater", "pullover", "outerwear", "attire"},
    {"shirt", "tee", "tshirt"},
    {"pants", "trousers", "jeans", "slacks", "bottoms"},
    {"shorts", "athleticshorts", "gymshorts"},
    {"shoes", "sneakers", "trainers", "footwear", "kicks"},
    {"boots", "boot"},
    {"sandals", "slides", "flipflops"},
    {"gloves", "mittens"},
    {"scarf", "scarves"},
    {"glasses", "eyeglasses", "spectacles"},
    {"sunglasses", "shades"},
    {"keys", "key", "keychain", "keyring"},
    {"id", "idcard", "studentid", "badge", "accesscard", "campusid"},
    {"wallet", "billfold", "cardholder", "purse"},
    {"backpack", "bookbag", "bag", "knapsack", "rucksack"},
    {"duffel", "duffle", "gymbag"},
    {"lunchbox", "lunchbag"},
    {"book", "textbook", "notebook", "binder", "workbook"},
    {"folder", "filefolder"},
    {"calculator", "graphingcalculator"},
    {"laptop", "notebookcomputer", "macbook", "chromebook"},
    {"tablet", "ipad"},
    {"phone", "cellphone", "mobile", "smartphone", "iphone", "android"},
    {"charger", "chargingcable", "cable", "cord", "poweradapter", "adapter"},
    {"headphones", "headset", "earphones", "earbuds", "airpods", "pods"},
    {"mouse", "wirelessmouse"},
    {"keyboard", "wirelesskeyboard"},
    {"stylus", "applepencil", "pen"},
    {"watch", "smartwatch", "applewatch", "fitbit"},
    {"ring", "band"},
    {"bracelet", "wristband"},
    {"necklace", "chain"},
    {"earring", "earrings"},
    {"umbrella", "parasol"},
    {"bottle", "waterbottle", "flask", "thermos", "hydroflask"},
    {"mug", "tumbler", "cup"},
    {"scooter", "eskate", "skateboard", "longboard"},
    {"helmet", "bikehelmet"},
    {"usb", "flashdrive", "thumbdrive"},
]

TOKEN_TO_CANONICAL: dict[str, str] = {
    synonym: sorted(group)[0] for group in SYNONYM_GROUPS for synonym in group
}


def normalize_search_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def canonicalize_token(token: str) -> str:
    return TOKEN_TO_CANONICAL.get(token, token)


def tokenize_search_text(text: str) -> list[str]:
    if not text:
        return []
    return [
        canonicalize_token(token)
        for token in normalize_search_text(text).split(" ")
        if token
    ]


def token_match_score(query_tokens: list[str], text_tokens: list[str]) -> float:
    if not query_tokens or not text_tokens:
        return 0.0

    total = 0.0
    for query_token in query_tokens:
        best_ratio = max(
            fuzz.ratio(query_token, text_token) for text_token in text_tokens
        )
        total += best_ratio
    return total / len(query_tokens)


def description_similarity_score(query: str, text: str) -> float:
    normalized_query = normalize_search_text(query)
    normalized_text = normalize_search_text(text)
    if not normalized_query or not normalized_text:
        return 0.0

    query_tokens = tokenize_search_text(normalized_query)
    text_tokens = tokenize_search_text(normalized_text)

    wratio_score = fuzz.WRatio(normalized_query, normalized_text)
    token_set_score = fuzz.token_set_ratio(normalized_query, normalized_text)
    partial_score = fuzz.partial_ratio(normalized_query, normalized_text)
    token_score = token_match_score(query_tokens, text_tokens)

    contains_bonus = 10 if normalized_query in normalized_text else 0

    return (
        (0.35 * wratio_score)
        + (0.35 * token_set_score)
        + (0.20 * partial_score)
        + (0.10 * token_score)
        + contains_bonus
    )


def rank_by_description(
    items: list[dict[str, Any]],
    description_query: str,
    description_field: str = "description",
) -> list[dict[str, Any]]:
    normalized_query = normalize_search_text(description_query)
    if not normalized_query:
        return items

    ranked_items: list[tuple[float, dict[str, Any]]] = []
    for item in items:
        score = description_similarity_score(
            normalized_query, item.get(description_field, "")
        )
        if score >= DESCRIPTION_MATCH_THRESHOLD:
            ranked_items.append((score, item))

    ranked_items.sort(
        key=lambda pair: (
            pair[0],
            pair[1].get("date", ""),
        ),
        reverse=True,
    )
    return [item for _, item in ranked_items[:DESCRIPTION_SEARCH_RESULT_LIMIT]]


def build_description_prefilter(
    description_query: str,
) -> dict[str, dict[str, str]] | None:
    normalized_query = normalize_search_text(description_query)
    if not normalized_query:
        return None

    tokens = tokenize_search_text(normalized_query)
    if not tokens:
        return None

    token_pattern = "|".join(sorted({re.escape(token) for token in tokens}))
    return {"description": {"$regex": token_pattern, "$options": "i"}}


async def rank_by_description_async(
    items: list[dict[str, Any]],
    description_query: str,
    description_field: str = "description",
) -> list[dict[str, Any]]:
    return await to_thread(
        rank_by_description, items, description_query, description_field
    )
