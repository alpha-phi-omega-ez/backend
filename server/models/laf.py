from datetime import datetime
from enum import Enum
from typing import Annotated, TypedDict

from pydantic import (
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    PlainSerializer,
)

from server.helpers.sanitize import sanitize_text
from server.models.common import Name, ResponseModel

# Constants for field length limits
LOCATION_MAX_LEN = 60


def parse_date_flexible(date_str: str) -> str:
    # Parse date string in either MM/DD/YYYY or YYYY-MM-DD format and return YYYY-MM-DD
    if not date_str:
        return date_str

    # Try MM/DD/YYYY format first
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Try YYYY-MM-DD format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # If neither works, raise an error
    raise ValueError(f"Date '{date_str}' must be in MM/DD/YYYY or YYYY-MM-DD format")


# TODO: limit on frontend
def validate_description(v: str) -> str:
    """Validate and sanitize description (max 2000 characters)."""
    return sanitize_text(v, max_len=2000)


def validate_type(v: str) -> str:
    """Validate and sanitize type (max 40 characters)."""
    return sanitize_text(v, max_len=40)


# TODO: will convert to list[str] later
def validate_location(v: str) -> str:
    """Validate and sanitize location (max 60 characters per comma-separated item)."""
    # Split by comma, sanitize each item individually, then join back
    if not v:
        return v
    location_items = [
        sanitize_text(item.strip(), max_len=LOCATION_MAX_LEN) for item in v.split(",")
    ]
    return ",".join(location_items)


def validate_description_filter(v: str | None) -> str | None:
    """Validate and sanitize description filter (max 2000 characters)."""
    if v is None:
        return None
    return validate_description(v)


def validate_type_filter(v: str | None) -> str | None:
    """Validate and sanitize type filter (max 40 characters)."""
    if v is None:
        return None
    return validate_type(v)


# Optional versions for query parameters
DescriptionFilter = Annotated[str, BeforeValidator(validate_description_filter)]
TypeFilter = Annotated[str, BeforeValidator(validate_type_filter)]

# Non-optional versions for required model fields
Description = Annotated[str, BeforeValidator(validate_description)]
TypeString = Annotated[str, BeforeValidator(validate_type)]
Location = Annotated[str, BeforeValidator(validate_location)]


class LAFItemRequest(BaseModel):
    type: TypeString = Field(...)
    location: Location = Field(...)
    description: Description = Field(...)
    date: Annotated[
        str,
        Field(...),
        BeforeValidator(parse_date_flexible),
    ]

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
    name: Name = Field(...)
    email: EmailStr = Field(...)

    class Config:
        json_schema_extra = {
            "example": {"name": "Alfred Glump", "email": "glump@rpi.edu"}
        }


class LAFArchiveItems(BaseModel):
    ids: list[int] = Field(...)

    class Config:
        json_schema_extra = {"example": {"ids": [1, 2, 3]}}


class LostReportRequest(BaseModel):
    type: TypeString = Field(...)
    name: Name = Field(...)
    email: EmailStr = Field(...)
    description: Description = Field(...)
    date: Annotated[
        str,
        Field(...),
        BeforeValidator(parse_date_flexible),
    ]
    location: Location = Field(...)

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
    BeforeValidator(lambda x: (x if x is None else parse_date_flexible(x))),
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
