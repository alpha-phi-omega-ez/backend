from aiocache import cached
from bson import ObjectId
from fastapi import HTTPException, Request

from server.helpers.cache import cache_key_exclude_request
from server.helpers.sanitize import is_valid_object_id
from server.models.backtest import Backtests, Course


async def course_helper(course) -> Course:
    return {
        "id": str(course["_id"]),
        "name": course["name"],
    }


# Retrieve all course codes present in the database
@cached(ttl=86400, key_builder=cache_key_exclude_request)
async def retrieve_coursecodes(request: Request) -> list[str]:
    backtest_course_code_collection = request.app.state.mongo_database.get_collection(
        "backtest_course_code_collection"
    )
    course_codes = await backtest_course_code_collection.distinct("course_code")
    return sorted(course_codes)


@cached(ttl=86400, key_builder=cache_key_exclude_request)
async def retrieve_courses(request: Request, course_code: str) -> list[Course]:
    backtest_courses_collection = request.app.state.mongo_database.get_collection(
        "backtest_courses_collection"
    )
    cursor = backtest_courses_collection.find({"course_code": course_code})
    courses = [await course_helper(course) async for course in cursor]

    return sorted(courses, key=lambda x: x["name"])


@cached(ttl=86400, key_builder=cache_key_exclude_request)
async def retrieve_backtest(request: Request, backtest_id: str) -> list[Backtests]:
    if not is_valid_object_id(backtest_id):
        raise HTTPException(status_code=404, detail="Backtest not found")

    backtest_collection = request.app.state.mongo_database.get_collection(
        "backtest_collection"
    )
    backtest = await backtest_collection.find_one(
        {"course_ids": {"$in": [ObjectId(backtest_id)]}}
    )
    if backtest:
        return backtest["tests"]
    raise HTTPException(status_code=404, detail="Backtest not found")
