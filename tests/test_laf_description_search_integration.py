"""
Integration-style tests for LAF description search: mocked Mongo cursors and helpers.

These exercise ``retrieve_laf_items`` and ``retrieve_lost_reports`` wiring without a
real database. For full stack tests, use a test Mongo instance and the HTTP API.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId

from server.database import laf as laf_module


class _FakeCursor:
    """Minimal async cursor: ``find().sort().limit()`` chain."""

    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs
        self._limit: int | None = None

    def sort(self, *_args, **_kwargs) -> "_FakeCursor":
        return self

    def limit(self, n: int) -> "_FakeCursor":
        self._limit = n
        return self

    def __aiter__(self) -> "_FakeCursor":
        self._idx = 0
        return self

    async def __anext__(self) -> dict:
        cap = self._limit if self._limit is not None else len(self._docs)
        if self._idx >= min(cap, len(self._docs)):
            raise StopAsyncIteration
        doc = self._docs[self._idx]
        self._idx += 1
        return doc


def _make_laf_query(**overrides: object) -> dict:
    base = {
        "date": None,
        "dateFilter": None,
        "location": None,
        "description": None,
        "type": None,
        "id": None,
    }
    base.update(overrides)
    return base


def _request_with_mongo_collection(collection: MagicMock) -> MagicMock:
    """Request mock: ``mongo_database.get_collection`` returns ``collection``."""
    mongo_db = MagicMock()
    mongo_db.get_collection = MagicMock(return_value=collection)
    state = MagicMock()
    state.mongo_database = mongo_db
    app = MagicMock()
    app.state = state
    request = MagicMock()
    request.app = app
    return request


@pytest.fixture
def sample_type_oid() -> ObjectId:
    return ObjectId("674000000000000000000001")


@pytest.fixture
def laf_docs(sample_type_oid: ObjectId) -> list[dict]:
    return [
        {
            "_id": 1,
            "type_id": sample_type_oid,
            "location": "Library",
            "date": "2024-01-15",
            "description": "Calculus textbook blue cover",
            "archived": False,
        },
        {
            "_id": 2,
            "type_id": sample_type_oid,
            "location": "Gym",
            "date": "2024-06-20",
            "description": "White Apple AirPods in case",
            "archived": False,
        },
        {
            "_id": 3,
            "type_id": sample_type_oid,
            "location": "Quad",
            "date": "2024-05-01",
            "description": "Red umbrella small",
            "archived": False,
        },
    ]


def test_retrieve_laf_items_ranks_by_description(
    sample_type_oid: ObjectId, laf_docs: list[dict]
) -> None:
    async def _run() -> list:
        collection = MagicMock()
        collection.find = MagicMock(return_value=_FakeCursor(laf_docs))
        request = _request_with_mongo_collection(collection)

        type_doc = {"type": "Other", "letter": "O"}

        with patch.object(
            laf_module,
            "get_type_from_id",
            new_callable=AsyncMock,
            return_value=type_doc,
        ):
            return await laf_module.retrieve_laf_items(
                request,
                _make_laf_query(description="airpods"),
                archived=False,
            )

    results = asyncio.run(_run())
    assert results
    assert results[0]["id"] == 2
    assert results[0]["description"] == "White Apple AirPods in case"


def test_retrieve_laf_items_by_id_skips_description_ranking(
    sample_type_oid: ObjectId, laf_docs: list[dict]
) -> None:
    """Exact id lookup must return that row without fuzzy reordering."""

    async def _run() -> list:
        target = next(d for d in laf_docs if d["_id"] == 1)
        collection = MagicMock()
        collection.find = MagicMock(return_value=_FakeCursor([target]))
        request = _request_with_mongo_collection(collection)

        type_doc = {"type": "Other", "letter": "O"}

        with patch.object(
            laf_module,
            "get_type_from_id",
            new_callable=AsyncMock,
            return_value=type_doc,
        ):
            return await laf_module.retrieve_laf_items(
                request,
                _make_laf_query(id=1, description="airpods"),
                archived=False,
            )

    results = asyncio.run(_run())
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert "textbook" in results[0]["description"].lower()


def test_retrieve_lost_reports_ranks_by_description(sample_type_oid: ObjectId) -> None:
    reports = [
        {
            "_id": ObjectId("674000000000000000000010"),
            "type_id": sample_type_oid,
            "name": "A",
            "email": "a@example.edu",
            "location": ["Library"],
            "date": "2024-02-01",
            "description": "Lost my umbrella",
            "found": False,
            "archived": False,
        },
        {
            "_id": ObjectId("674000000000000000000011"),
            "type_id": sample_type_oid,
            "name": "B",
            "email": "b@example.edu",
            "location": ["Gym"],
            "date": "2024-03-01",
            "description": "Missing airpods left ear only",
            "found": False,
            "archived": False,
        },
    ]

    async def _run() -> list:
        collection = MagicMock()
        collection.find = MagicMock(return_value=_FakeCursor(reports))
        request = _request_with_mongo_collection(collection)
        type_doc = {"type": "Electronics", "letter": "E"}

        with patch.object(
            laf_module,
            "get_type_from_id",
            new_callable=AsyncMock,
            return_value=type_doc,
        ):
            return await laf_module.retrieve_lost_reports(
                request,
                {
                    "date": None,
                    "dateFilter": None,
                    "location": None,
                    "description": "airpods",
                    "type": None,
                    "name": None,
                    "email": None,
                },
                archived=False,
            )

    results = asyncio.run(_run())
    assert results
    assert "airpods" in results[0]["description"].lower()
