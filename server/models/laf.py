from enum import Enum
from datetime import datetime
from typing import Annotated
from pydantic import BeforeValidator, PlainSerializer

from pydantic import BaseModel, EmailStr, Field


class LAFItem(BaseModel):
    type: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    date: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "Apparel",
                "location": "Union",
                "description": "Red sweater",
                "date": "2024-09-01",
            }
        }


class LAFFoundItem(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)

    class Config:
        json_schema_extra = {
            "example": {"name": "Alfred Glump", "email": "glump@rpi.edu"}
        }


class LAFArchiveItems(BaseModel):
    ids: list[str] = Field(...)

    class Config:
        json_schema_extra = {"example": {"ids": ["1", "2", "3"]}}


class LostReport(BaseModel):
    type: str = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)
    description: str = Field(...)
    date: str = Field(...)
    location: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "Apparel",
                "name": "Alfred Glump",
                "email": "glump@rpi.edu",
                "description": "Red sweater",
                "date": "2024-09-01",
                "location": "Union,DCC",
            }
        }


class LAFLocation(BaseModel):
    location: str = Field(...)

    class Config:
        json_schema_extra = {"example": {"location": "ECAV"}}


class LAFType(BaseModel):
    type: str = Field(...)

    class Config:
        json_schema_extra = {"example": {"type": "Washing Machines"}}


class DateFilter(str, Enum):
    before = "Before"
    after = "After"


DateString = Annotated[
    str,
    BeforeValidator(lambda x: None if x is None else str(x)),
    BeforeValidator(
        lambda x: (
            x if x is None else datetime.strptime(x, "%Y-%m-%d").strftime("%Y-%m-%d")
        )
    ),
    PlainSerializer(lambda x: x, return_type=str),
]
