from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.database.loanertech import (
    add_loanertech,
    delete_loanertech,
    retrieve_loanertech,
    retrieve_loanertechs,
    update_loanertech,
)
from server.models.loanertech import (
    LoanerTechCheckout,
    LoanerTechCheckIn,
    LoanerTech,
)

from server.models import ResponseModel, ErrorResponseModel

router = APIRouter()


@router.post("/", response_description="LoanerTech data added into the database")
async def add_loanertech_data(loanertech: LoanerTech = Body(...)) -> dict[str, Any]:
    loanertech = jsonable_encoder(loanertech)
    new_loanertech = await add_loanertech(loanertech)
    return ResponseModel(new_loanertech, "LoanerTech added successfully.")


@router.get("/", response_description="LoanerTech list retrieved")
async def get_loanertechs():
    loanertechs = await retrieve_loanertechs()
    if loanertechs:
        return ResponseModel(loanertechs, "LoanerTech data retrieved successfully")
    return ResponseModel(loanertechs, "Empty list returned")


@router.get("/{id}", response_description="LoanerTech data retrieved")
async def get_loanertech_data(id):
    loanertech = await retrieve_loanertech(id)
    if loanertech:
        return ResponseModel(loanertech, "LoanerTech data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "LoanerTech doesn't exist.")


@router.put("/{id}")
async def update_loanertech_data(id: str, req: LoanerTech = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_loanertech = await update_loanertech(id, req)
    if updated_loanertech:
        return ResponseModel(
            "LoanerTech with ID: {} name update is successful".format(id),
            "LoanerTech name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the loanertech data.",
    )


@router.delete(
    "/{id}", response_description="LoanerTech data deleted from the database"
)
async def delete_loanertech_data(id: str):
    deleted_loanertech = await delete_loanertech(id)
    if deleted_loanertech:
        return ResponseModel(
            "LoanerTech with ID: {} removed".format(id), "LoanTech deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "LoanerTech with id {0} doesn't exist".format(id)
    )
