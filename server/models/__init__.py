from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    data: Any
    message: str


class BoolResponse(ResponseModel):
    data: bool


class StringListResponse(ResponseModel):
    data: list[str]


class IntResponse(ResponseModel):
    data: int
