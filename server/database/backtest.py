from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import HTTPException

from server.database import database
from server.models.backtest import Backtests, Course

backtest_course_code_collection = database.get_collection(
    "backtest_course_code_collection"
)
backtest_courses_collection = database.get_collection("backtest_courses_collection")
backtest_collection = database.get_collection("backtest_collection")

course_code_cache = {"datetime": datetime(1970, 1, 1), "data": []}
courses_cache = {}


def course_helper(course) -> dict:
    return {
        "id": str(course["_id"]),
        "name": course["name"],
    }


# Retrieve all course codes present in the database
async def retrieve_coursecodes() -> list[str]:
    if course_code_cache["datetime"] > datetime.now() - timedelta(hours=24):
        return course_code_cache["data"]

    course_codes = []
    async for course_code in backtest_course_code_collection.find().sort("course_code"):
        course_codes.append(course_code["course_code"])

    course_code_cache["datetime"] = datetime.now()
    course_code_cache["data"] = course_codes
    return course_codes


async def retrieve_courses(course_code: str) -> list[Course]:
    if courses_cache.get(course_code) and courses_cache[course_code][
        "datetime"
    ] > datetime.now() - timedelta(hours=24):
        return courses_cache[course_code]["data"]

    courses = []
    async for course in backtest_courses_collection.find({"course_code": course_code}):
        courses.append(course_helper(course))

    courses.sort(key=lambda x: x["name"])
    courses_cache[course_code] = {"datetime": datetime.now(), "data": courses}
    return courses


async def retrieve_backtest(backtest_id: str) -> list[Backtests]:
    backtest = await backtest_collection.find_one(
        {"course_ids": {"$in": [ObjectId(backtest_id)]}}
    )
    if backtest:
        return backtest["tests"]
    raise HTTPException(status_code=404, detail="Backtest not found")
