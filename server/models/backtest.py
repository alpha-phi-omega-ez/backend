from typing import Annotated, TypedDict

from pydantic import BeforeValidator

from server.models.common import ResponseModel, validate_object_id


def validate_course_code(v: str) -> str:
    """Validate that a string is a valid course code (exactly 4 uppercase letters)."""
    v = v.strip() if isinstance(v, str) else str(v).strip()
    if not (len(v) == 4 and v.isalpha() and v.isupper()):
        raise ValueError("must be exactly 4 uppercase letters (A-Z)")
    return v


# Backtest route path param: course id stored as MongoDB ObjectId
CourseId = Annotated[str, BeforeValidator(validate_object_id)]
CourseCode = Annotated[str, BeforeValidator(validate_course_code)]


class Course(TypedDict):
    id: CourseId
    name: str


class Backtests(TypedDict):
    type: str
    tests: list[str]


class CoursesResponse(ResponseModel):
    data: list[Course]


class BacktestsReponse(ResponseModel):
    data: list[Backtests]
