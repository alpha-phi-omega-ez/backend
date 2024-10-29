from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    code: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "adsa-sda-dsa-ds-d-asd",
            }
        }
