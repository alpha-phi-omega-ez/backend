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
from server.models import ErrorResponseModel, ResponseModel
from server.models.loanertech import LoanerTech, LoanerTechCheckIn, LoanerTechCheckout

router = APIRouter()


@router.post("/", response_description="LoanerTech data added into the database")
async def add_loanertech_data(loanertech: LoanerTech = Body(...)) -> dict[str, Any]:
    dict_loanertech = jsonable_encoder(loanertech)
    new_loanertech = await add_loanertech(dict_loanertech)
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
    dict_req = {k: v for k, v in req.model_dump().items() if v is not None}
    updated_loanertech = await update_loanertech(id, dict_req)
    if updated_loanertech:
        return ResponseModel(
            f"LoanerTech with ID: {id} name update is successful",
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
            f"LoanerTech with ID: {id} removed", "LoanTech deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, f"LoanerTech with id {id} doesn't exist"
    )


@router.put(f"/checkout/{id}")
async def checkout_loanertech(id: str, req: LoanerTechCheckout = Body(...)):
    dict_req = {k: v for k, v in req.model_dump().items() if v is not None}
    updated_loanertech = await update_loanertech(id, dict_req)
    if updated_loanertech:
        return ResponseModel(
            f"LoanerTech with ID: {id} checked out",
            "LoanerTech checked out successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error checking out the loanertech data.",
    )


@router.put(f"/checkin/{id}")
async def checkin_loanertech(id: str, req: LoanerTechCheckIn = Body(...)):
    dict_req = {k: v for k, v in req.model_dump().items() if v is not None}
    updated_loanertech = await update_loanertech(id, dict_req)
    if updated_loanertech:
        return ResponseModel(
            f"LoanerTech with ID: {id} checked in",
            "LoanerTech checked in successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error checking in the loanertech data.",
    )
