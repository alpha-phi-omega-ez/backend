from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class LoanerTechCheckout(BaseModel):
    ids: list[int] = Field(...)
    phone_number: str = Field(..., max_length=12)
    email: Optional[EmailStr] = Field(...)
    name: str = Field(...)

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


class LoanerTech(BaseModel):
    description: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Apple 96 watt USB C charger",
            }
        }
