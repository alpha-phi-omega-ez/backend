from typing import Any

from fastapi import APIRouter

from server.database.backtest import (
    retrieve_backtest,
    retrieve_coursecodes,
    retrieve_courses,
)
from server.helpers.responses import Response

router = APIRouter()


@router.get("/coursecodes/", response_description="Course Code list retrieved")
async def get_coursecodes() -> dict[str, Any]:
    course_codes = await retrieve_coursecodes()
    if len(course_codes) > 0:
        return Response(course_codes, "Course Codes data retrieved successfully")
    return Response(course_codes, "Empty list returned")


@router.get("/courses/{course_code}", response_description="Courses list retrieved")
async def get_courses(course_code: str) -> dict[str, Any]:
    courses = await retrieve_courses(course_code)
    if len(courses) > 0:
        return Response(courses, "Courses data retrieved successfully")
    return Response(courses, "Empty list returned")


@router.get("/backtest/{course_id}", response_description="Backtests retrieved")
async def get_backtest(course_id: str) -> dict[str, Any]:
    backtest = await retrieve_backtest(course_id)
    if len(backtest) > 0:
        return Response(backtest, "Backtests data retrieved successfully")
    return Response(backtest, "Empty list returned")
