from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field


def validate_uuid_code(v: str) -> str:
    """Validate that a string is a valid UUID v4."""
    # Strip whitespace
    v = v.strip() if isinstance(v, str) else str(v).strip()
    try:
        # Validate it's a valid UUID v4
        uuid_obj = UUID(v, version=4)
        return str(uuid_obj)
    except (ValueError, AttributeError):
        raise ValueError("code must be a valid UUID v4")


UUIDCode = Annotated[str, BeforeValidator(validate_uuid_code)]


class TokenRequest(BaseModel):
    code: UUIDCode = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
