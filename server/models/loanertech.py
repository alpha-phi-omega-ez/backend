from typing import Annotated, Literal, Optional, TypedDict, Union

from pydantic import BaseModel, BeforeValidator, EmailStr, Field

from server.helpers.sanitize import sanitize_text
from server.models.common import Name, ResponseModel


def validate_loanertech_description(v: str) -> str:
    """Validate and sanitize loanertech description (max 250 characters)."""
    return sanitize_text(v, max_len=250)


LoanerTechDescription = Annotated[str, BeforeValidator(validate_loanertech_description)]


class LoanerTechCheckout(BaseModel):
    ids: list[int] = Field(...)
    phone_number: str = Field(..., max_length=20, pattern=r"^[0-9+()\-\s]{7,20}$")
    email: Optional[EmailStr] = Field(...)
    name: Name = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "ids": [1, 4],
                "phone_number": "518-276-6516",
                "email": "glump@rpi.edu",
                "name": "Alfred Glump",
            }
        }


class LoanerTechCheckin(BaseModel):
    ids: list[int] = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "ids": [1, 4],
            }
        }


class LoanerTechRequest(BaseModel):
    description: LoanerTechDescription = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Apple 96 watt USB C charger",
            }
        }


class LoanerTechItemUnauthorized(TypedDict):
    id: int
    in_office: bool
    description: str


class LoanerTechItem(TypedDict):
    id: int
    in_office: bool
    description: str
    phone: str
    email: Union[EmailStr, Literal[""]]
    name: str


class LoanerTechResponse(ResponseModel):
    data: LoanerTechItem
