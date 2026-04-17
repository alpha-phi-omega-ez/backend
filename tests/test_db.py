"""Unit tests for server.helpers.db."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from server.helpers.db import (
    async_dict_itr,
    datetime_time_delta,
    get_next_sequence_value,
)


def test_async_dict_itr_yields_items_in_order() -> None:
    async def _run() -> list[tuple[str, int]]:
        out: list[tuple[str, int]] = []
        async for pair in async_dict_itr({"a": 1, "b": 2}):
            out.append(pair)
        return out

    assert asyncio.run(_run()) == [("a", 1), ("b", 2)]


@pytest.mark.parametrize(
    "now,days,expected",
    [
        (
            datetime(2024, 3, 10, 15, 0, 0, tzinfo=timezone.utc),
            5,
            "2024-03-05",
        ),
        (
            datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            0,
            "2024-01-01",
        ),
    ],
    ids=["subtract_five_days", "zero_days"],
)
def test_datetime_time_delta(now: datetime, days: int, expected: str) -> None:
    async def _run() -> str:
        return await datetime_time_delta(now, days)

    assert asyncio.run(_run()) == expected


def test_get_next_sequence_value_returns_incremented_unique() -> None:
    seq_coll = MagicMock()
    seq_coll.find_one_and_update = AsyncMock(return_value={"seq": 7})
    check_coll = MagicMock()
    check_coll.find_one = AsyncMock(return_value=None)

    async def _run() -> int:
        return await get_next_sequence_value("myseq", seq_coll, check_coll)

    assert asyncio.run(_run()) == 7
    seq_coll.insert_one.assert_not_called()
    check_coll.find_one.assert_called_once_with({"_id": 7})


def test_get_next_sequence_value_inserts_when_sequence_missing() -> None:
    seq_coll = MagicMock()
    seq_coll.find_one_and_update = AsyncMock(return_value=None)
    seq_coll.insert_one = AsyncMock()
    check_coll = MagicMock()
    check_coll.find_one = AsyncMock(return_value=None)

    async def _run() -> int:
        return await get_next_sequence_value("newseq", seq_coll, check_coll)

    assert asyncio.run(_run()) == 1
    seq_coll.insert_one.assert_awaited_once_with({"_id": "newseq", "seq": 1})


def test_get_next_sequence_value_repairs_duplicate_then_returns_next() -> None:
    seq_coll = MagicMock()
    check_coll = MagicMock()

    # First inc gives 3 but _id 3 exists; max _id is 10; second inc gives 11, free.
    seq_coll.find_one_and_update = AsyncMock(
        side_effect=[{"seq": 3}, {"seq": 11}],
    )
    seq_coll.update_one = AsyncMock()

    async def find_one_side_effect(
        filter=None, sort=None, projection=None, **_kwargs
    ):
        if filter == {"_id": 3}:
            return {"_id": 3, "data": "dup"}
        if sort == [("_id", -1)]:
            return {"_id": 10}
        if filter == {"_id": 11}:
            return None
        return None

    check_coll.find_one = AsyncMock(side_effect=find_one_side_effect)

    async def _run() -> int:
        return await get_next_sequence_value("s", seq_coll, check_coll)

    assert asyncio.run(_run()) == 11
    seq_coll.update_one.assert_awaited_once_with(
        {"_id": "s"},
        {"$max": {"seq": 10}},
    )


def test_get_next_sequence_value_duplicate_max_collection_empty() -> None:
    seq_coll = MagicMock()
    check_coll = MagicMock()
    seq_coll.find_one_and_update = AsyncMock(
        side_effect=[{"seq": 2}, {"seq": 3}],
    )
    seq_coll.update_one = AsyncMock()

    async def find_one_side_effect(
        filter=None, sort=None, projection=None, **_kwargs
    ):
        if filter == {"_id": 2}:
            return {"_id": 2}
        if sort == [("_id", -1)]:
            return None
        if filter == {"_id": 3}:
            return None
        return None

    check_coll.find_one = AsyncMock(side_effect=find_one_side_effect)

    async def _run() -> int:
        return await get_next_sequence_value("empty_max", seq_coll, check_coll)

    assert asyncio.run(_run()) == 3
    seq_coll.update_one.assert_awaited_once_with(
        {"_id": "empty_max"},
        {"$max": {"seq": 0}},
    )
