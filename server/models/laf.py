from enum import Enum

from pydantic import BaseModel, EmailStr, Field, constr


class NewLAFItem(BaseModel):
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


class NewLostReport(BaseModel):
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
                "location": ["Union", "DCC"],
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


class DateString(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field):
        try:
            # Ensure the value matches the format YYYY-MM-DD
            from datetime import datetime

            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
