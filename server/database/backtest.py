from aiocache import cached
from bson import ObjectId
from fastapi import HTTPException

from server.database import database
from server.helpers.sanitize import is_valid_object_id
from server.models.backtest import Backtests, Course

backtest_course_code_collection = database.get_collection(
    "backtest_course_code_collection"
)
backtest_courses_collection = database.get_collection("backtest_courses_collection")
backtest_collection = database.get_collection("backtest_collection")


async def course_helper(course) -> Course:
    return {
        "id": str(course["_id"]),
        "name": course["name"],
    }


# Retrieve all course codes present in the database
@cached(ttl=86400)
async def retrieve_coursecodes() -> list[str]:
    course_codes = await backtest_course_code_collection.distinct("course_code")
    return sorted(course_codes)


@cached(ttl=86400)
async def retrieve_courses(course_code: str) -> list[Course]:
    cursor = backtest_courses_collection.find({"course_code": course_code})
    courses = [await course_helper(course) async for course in cursor]

    return sorted(courses, key=lambda x: x["name"])


@cached(ttl=86400)
async def retrieve_backtest(backtest_id: str) -> list[Backtests]:
    if not is_valid_object_id(backtest_id):
        raise HTTPException(status_code=404, detail="Backtest not found")

    backtest = await backtest_collection.find_one(
        {"course_ids": {"$in": [ObjectId(backtest_id)]}}
    )
    if backtest:
        return backtest["tests"]
    raise HTTPException(status_code=404, detail="Backtest not found")
