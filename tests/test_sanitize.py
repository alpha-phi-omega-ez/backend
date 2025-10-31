from server.helpers.sanitize import (
    is_valid_object_id,
    reject_mongo_operators,
    sanitize_text,
    strip_tags,
)


def test_strip_tags_removes_html_and_scripts():
    html = "<script>alert('x')</script><b>hello</b> world"
    assert strip_tags(html) == "hello world"


def test_sanitize_text_normalizes_whitespace_and_limits():
    text = "  Hello\n\tworld   "
    assert sanitize_text(text) == "Hello world"
    long = "a" * 10
    assert sanitize_text(long, max_len=5) == "aaaaa"


def test_is_valid_object_id():
    assert is_valid_object_id("0" * 24)
    assert not is_valid_object_id("g" * 24)
    assert not is_valid_object_id("123")


def test_reject_mongo_operators_allows_safe():
    safe = {"name": "ok", "nested": {"list": [1, 2, {"a": "b"}]}}
    assert reject_mongo_operators(safe) is safe


def test_reject_mongo_operators_blocks_dollar_and_dots():
    bads = [
        {"$where": 1},
        {"nested": {"$gt": 5}},
        {"a.b": 1},
        {"nested": {"a.b": 2}},
    ]
    for bad in bads:
        try:
            reject_mongo_operators(bad)
            assert False, "Expected ValueError not raised"
        except ValueError:
            pass
