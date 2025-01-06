from typing import Any, Tuple

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from server.database.loanertech import (
    add_loanertech,
    delete_loanertech,
    retrieve_loanertech,
    retrieve_loanertechs,
    retrieve_loanertechs_unauthenticated,
    update_loanertech,
)
from server.helpers.auth import required_auth, simple_auth_check
from server.helpers.responses import Response, ErrorResponse
from server.models.loanertech import LoanerTech, LoanerTechCheckin, LoanerTechCheckout

router = APIRouter()


@router.get("/", response_description="LoanerTech list retrieved")
async def get_loanertechs(
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check)
) -> dict[str, Any]:
    authenticated = auth[0]

    loanertechs = (
        await retrieve_loanertechs()
        if authenticated
        else await retrieve_loanertechs_unauthenticated()
    )
    if loanertechs:
        return Response(loanertechs, "LoanerTech data retrieved successfully")
    return Response(loanertechs, "Empty list returned")


@router.post("/", response_description="LoanerTech data added into the database")
async def add_loanertech_data(
    loanertech: LoanerTech = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_loanertech = jsonable_encoder(loanertech)
    new_loanertech = await add_loanertech(dict_loanertech)
    return Response(new_loanertech, "LoanerTech added successfully.")


@router.get("/{id}", response_description="LoanerTech data retrieved")
async def get_loanertech_data(id: int) -> dict[str, Any]:
    loanertech = await retrieve_loanertech(id)
    if loanertech:
        return Response(loanertech, "LoanerTech data retrieved successfully")
    return ErrorResponse("An error occurred.", 404, "LoanerTech doesn't exist.")


@router.put("/update/{id}")
async def update_loanertech_data(
    id: int,
    req: LoanerTech = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_req = jsonable_encoder(req)
    updated_loanertech = await update_loanertech(id, dict_req)
    if updated_loanertech:
        return Response(
            f"LoanerTech with ID: {id} name update is successful",
            "LoanerTech name updated successfully",
        )
    return ErrorResponse(
        "An error occurred",
        404,
        "There was an error updating the loanertech data.",
    )


@router.delete(
    "/delete/{id}", response_description="LoanerTech data deleted from the database"
)
async def delete_loanertech_data(
    id: int,
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    deleted_loanertech = await delete_loanertech(id)
    if deleted_loanertech:
        return Response(
            f"LoanerTech with ID: {id} removed", "LoanTech deleted successfully"
        )
    return ErrorResponse(
        "An error occurred", 404, f"LoanerTech with id {id} doesn't exist"
    )


@router.put("/checkout")
async def checkout_loanertech(
    req: LoanerTechCheckout = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_req = jsonable_encoder(req)
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
        return Response(
            f"LoanerTech with IDs: {ids} checked out",
            "LoanerTech checked out successfully",
        )
    return ErrorResponse(
        "An error occurred",
        500,
        "There was an error checking out the loanertech data.",
    )


@router.put("/checkin")
async def checkin_loanertech(
    req: LoanerTechCheckin = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_req = jsonable_encoder(req)
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
        return Response(
            f"LoanerTech with IDs: {ids} checked in",
            "LoanerTech checked in successfully",
        )
    return ErrorResponse(
        "An error occurred",
        500,
        "There was an error checking in the loanertech data.",
    )
