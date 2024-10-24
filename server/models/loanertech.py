from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoanerTechCheckout(BaseModel):
    phone_number: str = Field(..., max_length=12)
    email: Optional[EmailStr] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "518-276-6516",
                "email": "glump@rpi.edu",
            }
        }


class LoanerTech(BaseModel):
    description: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "description": "Apple 96 watt USB C charger",
            }
        }
