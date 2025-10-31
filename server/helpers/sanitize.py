from __future__ import annotations

import re
from typing import Any

import bleach

_OBJECT_ID_RE = re.compile(r"^[a-fA-F0-9]{24}$")


def strip_tags(text: str) -> str:
    if text is None:
        return ""
    # Remove all remaining HTML tags using bleach
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def normalize_ws(text: str) -> str:
    # Collapse whitespace and trim
    return re.sub(r"\s+", " ", text or "").strip()


def sanitize_text(text: str, max_len: int | None = None) -> str:
    cleaned = normalize_ws(strip_tags(str(text)))
    if max_len is not None and len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned


def is_valid_object_id(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_OBJECT_ID_RE.fullmatch(value))


def _reject_key(key: Any) -> None:
    if isinstance(key, str) and (key.startswith("$") or "." in key):
        raise ValueError("MongoDB operator or dotted keys are not allowed in input")


def reject_mongo_operators(obj: Any) -> Any:
    # Recursively validate that no keys start with '$' or contain '.'
    if isinstance(obj, dict):
        for k, v in obj.items():
            _reject_key(k)
            reject_mongo_operators(v)
    elif isinstance(obj, list):
        for item in obj:
            reject_mongo_operators(item)
    return obj
