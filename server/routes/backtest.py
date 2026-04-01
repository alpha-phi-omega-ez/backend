from fastapi import APIRouter, Request

from server.database.backtest import (
    retrieve_backtest,
    retrieve_coursecodes,
    retrieve_courses,
)
from server.models.backtest import (
    BacktestsReponse,
    CourseCode,
    CourseId,
    CoursesResponse,
)
from server.models.common import StringListResponse

router = APIRouter()


@router.get(
    "/coursecodes/",
    response_description="Course Code list retrieved",
    response_model=StringListResponse,
)
async def get_coursecodes(request: Request) -> StringListResponse:
    course_codes = await retrieve_coursecodes(request)
    return StringListResponse(
        data=course_codes, message="Course Codes data retrieved successfully"
    )


@router.get(
    "/courses/{course_code}",
    response_description="Courses list retrieved",
    response_model=CoursesResponse,
)
async def get_courses(request: Request, course_code: CourseCode) -> CoursesResponse:
    courses = await retrieve_courses(request, course_code)
    return CoursesResponse(data=courses, message="Courses data retrieved successfully")


@router.get(
    "/backtest/{course_id}",
    response_description="Backtests retrieved",
    response_model=BacktestsReponse,
)
async def get_backtest(request: Request, course_id: CourseId) -> BacktestsReponse:
    backtest = await retrieve_backtest(request, course_id)
    return BacktestsReponse(
        data=backtest, message="Backtests data retrieved successfully"
    )
