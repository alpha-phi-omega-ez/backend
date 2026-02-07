import pytest

from server.helpers.sanitize import (
    is_valid_object_id,
    reject_mongo_operators,
    sanitize_text,
    strip_tags,
)


def test_strip_tags_removes_html_and_scripts():
    html = "<script>alert('x')</script><b>hello</b> world"
    assert strip_tags(html) == "alert('x')hello world"


@pytest.mark.parametrize(
    "text,kwargs,expected",
    [
        ("  Hello\n\tworld   ", {}, "Hello world"),
        ("a" * 10, {"max_len": 5}, "aaaaa"),
    ],
    ids=["normalizes_whitespace", "truncates_to_max_len"],
)
def test_sanitize_text(text, kwargs, expected):
    assert sanitize_text(text, **kwargs) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        # Valid
        ("0" * 24, True),
        ("a" * 24, True),
        ("A" * 24, True),
        ("AaBbCc012345678901234567", True),
        ("0123456789abcdefABCDEF01", True),
        # Invalid: bad chars or length
        ("g" * 24, False),
        ("123", False),
        ("", False),
        ("0" * 23, False),
        ("0" * 25, False),
        # Non-string
        (None, False),
        (123, False),
        (123456789012345678901234, False),
        ([], False),
        ({}, False),
    ],
    ids=[
        "valid_24_zeros",
        "valid_lowercase_hex",
        "valid_uppercase_hex",
        "valid_mixed_24_chars",
        "valid_mixed_hex_24_chars",
        "invalid_non_hex_char",
        "invalid_too_short",
        "invalid_empty",
        "invalid_23_chars",
        "invalid_25_chars",
        "invalid_none",
        "invalid_int",
        "invalid_large_int",
        "invalid_list",
        "invalid_dict",
    ],
)
def test_is_valid_object_id(value, expected):
    assert is_valid_object_id(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        {"name": "ok", "nested": {"list": [1, 2, {"a": "b"}]}},
        ({"a": 1}, {"b": 2}),
        {1, 2, 3, "test"},
        "string",
        123,
        True,
        None,
        1.5,
    ],
    ids=[
        "nested_dict",
        "tuple_of_dicts",
        "set",
        "string",
        "int",
        "bool",
        "none",
        "float",
    ],
)
def test_reject_mongo_operators_allows_safe(value):
    result = reject_mongo_operators(value)
    assert result is value


@pytest.mark.parametrize(
    "bad",
    [
        {"$where": 1},
        {"nested": {"$gt": 5}},
        {"a.b": 1},
        {"nested": {"a.b": 2}},
        [{"$ne": 1}, {"safe": "ok"}],
        ({"$in": [1, 2]}, {"safe": "ok"}),
    ],
    ids=[
        "top_level_dollar_where",
        "nested_dollar_gt",
        "top_level_dotted_key",
        "nested_dotted_key",
        "list_with_dollar_ne",
        "tuple_with_dollar_in",
    ],
)
def test_reject_mongo_operators_blocks_dangerous_keys(bad):
    with pytest.raises(ValueError):
        reject_mongo_operators(bad)
