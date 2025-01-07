from enum import Enum
from datetime import datetime
from typing import Annotated, TypedDict
from pydantic import BeforeValidator, PlainSerializer, BaseModel, EmailStr, Field
from server.models import ResponseModel


class LAFItemRequest(BaseModel):
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


class LostReportRequest(BaseModel):
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


class LAFItem(TypedDict):
    id: int
    type: str
    display_id: str
    location: str
    date: str
    description: str


class ArchivedLAFItem(LAFItem):
    found: bool
    archived: str
    name: str
    email: EmailStr
    returned: str


class LostReportItem(TypedDict):
    id: str
    name: str
    email: EmailStr
    type: str
    location: list[str]
    date: str
    description: str
    found: bool
    archived: bool


class ExpiredItem(TypedDict):
    expired: list[LAFItem]
    potential: list[LAFItem]


class LAFItemResponse(ResponseModel):
    data: LAFItem


class LAFItemsResponse(ResponseModel):
    data: list[LAFItem]


class ExpireLAFItemsReponse(ResponseModel):
    data: ExpiredItem


class ArchivedLAFItemsResponse(ResponseModel):
    data: list[ArchivedLAFItem]


class LostReportItemResponse(ResponseModel):
    data: LostReportItem


class LostReportItemsResponse(ResponseModel):
    data: list[LostReportItem]
