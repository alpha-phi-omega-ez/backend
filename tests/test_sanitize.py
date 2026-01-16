from server.helpers.sanitize import (
    is_valid_object_id,
    reject_mongo_operators,
    sanitize_text,
    strip_tags,
)


def test_strip_tags_removes_html_and_scripts():
    html = "<script>alert('x')</script><b>hello</b> world"
    assert strip_tags(html) == "alert('x')hello world"


def test_sanitize_text_normalizes_whitespace_and_limits():
    text = "  Hello\n\tworld   "
    assert sanitize_text(text) == "Hello world"
    long = "a" * 10
    assert sanitize_text(long, max_len=5) == "aaaaa"


def test_is_valid_object_id():
    # Valid cases
    assert is_valid_object_id("0" * 24)
    assert is_valid_object_id("a" * 24)  # lowercase
    assert is_valid_object_id("A" * 24)  # uppercase
    assert is_valid_object_id("AaBbCc012345678901234567")  # mixed case (24 chars)
    assert is_valid_object_id(
        "0123456789abcdefABCDEF01"
    )  # mixed case with all hex chars (24 chars)

    # Invalid cases
    assert not is_valid_object_id("g" * 24)  # invalid hex character
    assert not is_valid_object_id("123")  # too short
    assert not is_valid_object_id("")  # empty string
    assert not is_valid_object_id("0" * 23)  # too short (23 chars)
    assert not is_valid_object_id("0" * 25)  # too long (25 chars)

    # Non-string types
    assert not is_valid_object_id(None)
    assert not is_valid_object_id(123)
    assert not is_valid_object_id(123456789012345678901234)  # integer
    assert not is_valid_object_id([])
    assert not is_valid_object_id({})


def test_reject_mongo_operators_allows_safe():
    # Test dicts with nested structures
    safe = {"name": "ok", "nested": {"list": [1, 2, {"a": "b"}]}}
    assert reject_mongo_operators(safe) is safe

    # Test tuples containing safe data
    safe_tuple = ({"a": 1}, {"b": 2})
    assert reject_mongo_operators(safe_tuple) is safe_tuple

    # Test sets containing safe data
    safe_set = {1, 2, 3, "test"}
    assert reject_mongo_operators(safe_set) is safe_set

    # Test primitives pass through unchanged
    assert reject_mongo_operators("string") == "string"
    assert reject_mongo_operators(123) == 123
    assert reject_mongo_operators(True) is True
    assert reject_mongo_operators(None) is None
    assert reject_mongo_operators(1.5) == 1.5


def test_reject_mongo_operators_blocks_dangerous_keys():
    # Test dangerous keys in top-level dict
    # Test dangerous keys in nested structures within lists
    # Test dangerous keys in nested structures within tuples
    test_cases = [
        {"$where": 1},
        {"nested": {"$gt": 5}},
        {"a.b": 1},
        {"nested": {"a.b": 2}},
        [{"$ne": 1}, {"safe": "ok"}],
        ({"$in": [1, 2]}, {"safe": "ok"}),
    ]

    for bad in test_cases:
        try:
            reject_mongo_operators(bad)
            assert False, f"Expected ValueError not raised for {bad}"
        except ValueError:
            pass
