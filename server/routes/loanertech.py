from typing import Any, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from server.database.loanertech import (
    add_loanertech,
    delete_loanertech,
    retrieve_loanertech,
    retrieve_loanertechs,
    retrieve_loanertechs_unauthenticated,
    update_loanertech,
)
from server.helpers.auth import simple_auth_check
from server.models import ErrorResponseModel, ResponseModel
from server.models.loanertech import LoanerTech, LoanerTechCheckin, LoanerTechCheckout

router = APIRouter()


@router.get("/", response_description="LoanerTech list retrieved")
async def get_loanertechs(auth: Tuple[bool, str, Any] = Depends(simple_auth_check)):
    authenticated = auth[0]

    loanertechs = []
    if authenticated:
        loanertechs = await retrieve_loanertechs()
    else:
        loanertechs = await retrieve_loanertechs_unauthenticated()
    if loanertechs:
        return ResponseModel(
            loanertechs, "LoanerTech data retrieved successfully", authenticated
        )
    return ResponseModel(loanertechs, "Empty list returned", authenticated)


@router.post("/", response_description="LoanerTech data added into the database")
async def add_loanertech_data(
    request: Request,
    loanertech: LoanerTech = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, payload = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    print(payload)

    dict_loanertech = jsonable_encoder(loanertech)
    new_loanertech = await add_loanertech(dict_loanertech)
    return ResponseModel(new_loanertech, "LoanerTech added successfully.")


@router.get("/{id}", response_description="LoanerTech data retrieved")
async def get_loanertech_data(id: int):
    loanertech = await retrieve_loanertech(id)
    if loanertech:
        return ResponseModel(loanertech, "LoanerTech data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "LoanerTech doesn't exist.")


@router.put("/update/{id}")
async def update_loanertech_data(
    id: int,
    req: LoanerTech = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
):
    authenticated, message, payload = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    print(payload)

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
    "/delete/{id}", response_description="LoanerTech data deleted from the database"
)
async def delete_loanertech_data(
    id: int, auth: Tuple[bool, str, Any] = Depends(simple_auth_check)
):
    authenticated, message, payload = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    print(payload)

    deleted_loanertech = await delete_loanertech(id)
    if deleted_loanertech:
        return ResponseModel(
            f"LoanerTech with ID: {id} removed", "LoanTech deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, f"LoanerTech with id {id} doesn't exist"
    )


@router.put("/checkout")
async def checkout_loanertech(
    req: LoanerTechCheckout = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
):
    authenticated, message, _ = auth

    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_req = {k: v for k, v in req.model_dump().items() if v is not None}

    success = True
    ids = []
    for id in dict_req["ids"]:
        item = {
            "in_office": False,
            "phone": dict_req["phone_number"],
            "email": dict_req["email"],
            "name": dict_req["name"],
        }
        updated_loanertech = await update_loanertech(id, item)
        ids.append(id)
        if not updated_loanertech:
            success = False
            break

    if success:
        return ResponseModel(
            f"LoanerTech with IDs: {ids} checked out",
            "LoanerTech checked out successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        500,
        "There was an error checking out the loanertech data.",
    )


@router.put("/checkin")
async def checkin_loanertech(
    req: LoanerTechCheckin = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
):
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_req = {k: v for k, v in req.model_dump().items() if v is not None}

    success = True
    ids = []
    for id in dict_req["ids"]:
        item = {
            "in_office": True,
            "phone": "",
            "email": "",
            "name": "",
        }
        updated_loanertech = await update_loanertech(id, item)
        ids.append(id)
        if not updated_loanertech:
            success = False
            break

    if success:
        return ResponseModel(
            f"LoanerTech with IDs: {ids} checked in",
            "LoanerTech checked in successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        500,
        "There was an error checking in the loanertech data.",
    )
