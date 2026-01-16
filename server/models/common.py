from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator

from server.helpers.sanitize import is_valid_object_id, sanitize_text


def validate_name(v: str | None) -> str:
    """Validate and sanitize name filter (max 100 characters)."""
    return sanitize_text(v, max_len=100)


def validate_object_id(v: str) -> str:
    """Validate that a string is a valid MongoDB ObjectId (24 hex characters)."""
    if not is_valid_object_id(v):
        raise ValueError("must be a valid ObjectId (24 hexadecimal characters)")
    return v


def validate_name_filter(v: str | None) -> str | None:
    """Validate optional name filter."""
    if v is None:
        return None
    return validate_name(v)


NameFilter = Annotated[str, BeforeValidator(validate_name_filter)]
Name = Annotated[str, BeforeValidator(validate_name)]


class ResponseModel(BaseModel):
    data: Any
    message: str


class BoolResponse(ResponseModel):
    data: bool


class StringListResponse(ResponseModel):
    data: list[str]


class IntResponse(ResponseModel):
    data: int
