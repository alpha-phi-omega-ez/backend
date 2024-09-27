from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


class LoanerTechCheckout(BaseModel):
    id: int = Field(...)
    phone_number: str = Field(..., max_length=12)
    email: Optional[EmailStr] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "phone_number": "518-276-6516",
                "email": "glump@rpi.edu",
            }
        }


class LoanerTechCheckIn(BaseModel):
    id: int = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
            }
        }


class LoanerTech(BaseModel):
    id: int = Field(...)
    description: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "description": "Apple 96 watt USB C charger",
            }
        }
