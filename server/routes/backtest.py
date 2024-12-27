from typing import Any

from fastapi import APIRouter

from server.database.backtest import (
    retrieve_backtest,
    retrieve_coursecodes,
    retrieve_courses,
)
from server.models import ResponseModel

router = APIRouter()


@router.get("/coursecodes/", response_description="Course Code list retrieved")
async def get_coursecodes() -> dict[str, Any]:
    course_codes = await retrieve_coursecodes()
    if len(course_codes) > 0:
        return ResponseModel(course_codes, "Course Codes data retrieved successfully")
    return ResponseModel(course_codes, "Empty list returned")


@router.get("/courses/{course_code}", response_description="Courses list retrieved")
async def get_courses(course_code: str) -> dict[str, Any]:
    print(course_code)
    courses = await retrieve_courses(course_code)
    if len(courses) > 0:
        return ResponseModel(courses, "Courses data retrieved successfully")
    return ResponseModel(courses, "Empty list returned")


@router.get("/backtest/{course_id}", response_description="Backtests retrieved")
async def get_backtest(course_id: str) -> dict[str, Any]:
    backtest = await retrieve_backtest(course_id)
    if len(backtest) > 0:
        return ResponseModel(backtest, "Backtests data retrieved successfully")
    return ResponseModel(backtest, "Empty list returned")
