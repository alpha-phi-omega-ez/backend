from typing import TypedDict

from server.models import ResponseModel


class Course(TypedDict):
    id: str
    name: str


class Backtests(TypedDict):
    type: str
    tests: list[str]


class CoursesResponse(ResponseModel):
    data: list[Course]


class BacktestsReponse(ResponseModel):
    data: list[Backtests]
