from pydantic import BaseModel
from typing import Any


class ResponseModel(BaseModel):
    data: Any
    message: str


class BoolResponse(ResponseModel):
    data: bool


class StringListResponse(ResponseModel):
    data: list[str]
