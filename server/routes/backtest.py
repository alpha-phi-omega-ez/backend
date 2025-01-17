from fastapi import APIRouter

from server.database.backtest import (
    retrieve_backtest,
    retrieve_coursecodes,
    retrieve_courses,
)
from server.models import StringListResponse
from server.models.backtest import BacktestsReponse, CoursesResponse

router = APIRouter()


@router.get(
    "/coursecodes/",
    response_description="Course Code list retrieved",
    response_model=StringListResponse,
)
async def get_coursecodes() -> StringListResponse:
    course_codes = await retrieve_coursecodes()
    return StringListResponse(
        data=course_codes, message="Course Codes data retrieved successfully"
    )


@router.get(
    "/courses/{course_code}",
    response_description="Courses list retrieved",
    response_model=CoursesResponse,
)
async def get_courses(course_code: str) -> CoursesResponse:
    courses = await retrieve_courses(course_code)
    return CoursesResponse(data=courses, message="Courses data retrieved successfully")


@router.get(
    "/backtest/{course_id}",
    response_description="Backtests retrieved",
    response_model=BacktestsReponse,
)
async def get_backtest(course_id: str) -> BacktestsReponse:
    backtest = await retrieve_backtest(course_id)
    return BacktestsReponse(
        data=backtest, message="Backtests data retrieved successfully"
    )
