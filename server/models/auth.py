from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TokenRequest(BaseModel):
    code: str = Field(...)

    @field_validator("code", mode="before")
    @classmethod
    def v_code(cls, v: str) -> str:
        # Strip whitespace
        v = v.strip() if isinstance(v, str) else str(v)
        try:
            # Validate it's a valid UUID v4
            uuid_obj = UUID(v, version=4)
            return str(uuid_obj)
        except (ValueError, AttributeError):
            raise ValueError("code must be a valid UUID v4")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
