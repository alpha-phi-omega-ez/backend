"""Unit tests for server.helpers.cache."""

from fastapi import Request

from server.helpers.cache import cache_key_exclude_request


def _http_request() -> Request:
    """Minimal Starlette/FastAPI Request for isinstance checks."""
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.4"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "root_path": "",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 80),
        }
    )


def sample_fn(*_args, **_kwargs) -> None:
    """Module-level function for cache key naming."""
    pass


def test_cache_key_exclude_request_strips_request_from_args() -> None:
    req = _http_request()
    key = cache_key_exclude_request(sample_fn, 1, req, "keep")
    expected = f"{sample_fn.__module__}.{sample_fn.__name__}:(1, 'keep'):()"
    assert key == expected


def test_cache_key_exclude_request_strips_request_from_kwargs() -> None:
    req = _http_request()
    key = cache_key_exclude_request(sample_fn, 10, r=req, z=1, a=2)
    expected = f"{sample_fn.__module__}.{sample_fn.__name__}:(10,):(('a', 2), ('z', 1))"
    assert key == expected


def test_cache_key_exclude_request_kwargs_sorted_deterministically() -> None:
    key_zy = cache_key_exclude_request(sample_fn, 0, z=1, y=2)
    key_yz = cache_key_exclude_request(sample_fn, 0, y=2, z=1)
    assert key_zy == key_yz


def test_cache_key_exclude_request_includes_module_and_function_name() -> None:
    key = cache_key_exclude_request(sample_fn, 42)
    assert key.startswith(f"{sample_fn.__module__}.{sample_fn.__name__}:")
