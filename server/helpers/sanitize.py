from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import bleach

_OBJECT_ID_RE = re.compile(r"^[a-fA-F0-9]{24}$")
_WHITESPACE_RE = re.compile(r"\s+")
_UNSAFE_REDIRECT_CHARS_RE = re.compile(r"[\x00-\x1f\\]")


def strip_tags(text: str | None) -> str:
    if text is None:
        return ""
    # Remove all remaining HTML tags using bleach
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def normalize_ws(text: str | None) -> str:
    # Collapse whitespace and trim; None treated as empty string
    return _WHITESPACE_RE.sub(" ", text or "").strip()


def sanitize_text(text: str, max_len: int | None = None) -> str:
    cleaned = normalize_ws(strip_tags(str(text)))
    if max_len is not None and len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned


def is_valid_object_id(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_OBJECT_ID_RE.fullmatch(value))


def sanitize_redirect_path(redirect: str | None, default: str = "/") -> str:
    """Return a same-app relative path, or *default* if the value is unsafe.

    Allows only paths that start with a single ``/`` (not ``//``). Rejects
    absolute URLs, protocol-relative URLs, backslashes, and control characters
    so post-login navigation cannot leave the frontend origin.
    """
    if not isinstance(redirect, str):
        return default

    path = redirect.strip()
    if not path.startswith("/") or path.startswith("//"):
        return default
    if _UNSAFE_REDIRECT_CHARS_RE.search(path):
        return default

    parsed = urlparse(path)
    if parsed.scheme or parsed.netloc:
        return default

    return path


def _reject_key(key: Any) -> None:
    if isinstance(key, str) and (key.startswith("$") or "." in key):
        raise ValueError("MongoDB operator or dotted keys are not allowed in input")


def reject_mongo_operators(obj: Any) -> Any:
    # Recursively validate that no keys start with '$' or contain '.'
    # Only dict and iterable container types need validation (primitives pass through)
    if isinstance(obj, dict):
        for k, v in obj.items():
            _reject_key(k)
            reject_mongo_operators(v)
    elif isinstance(obj, (list, tuple, set)):
        for item in obj:
            reject_mongo_operators(item)
    # Primitives (str, int, float, bool, None) and other types pass through unchanged
    return obj
