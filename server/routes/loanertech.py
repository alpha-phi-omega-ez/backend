from typing import Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
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
from server.models.loanertech import (
    LoanerTechRequest,
    LoanerTechCheckin,
    LoanerTechCheckout,
    LoanerTechResponse,
)
from server.models import BoolResponse

router = APIRouter()


@router.get(
    "/",
    response_description="LoanerTech list retrieved",
)
async def get_loanertechs(
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check)
) -> JSONResponse:
    authenticated = auth[0]

    loanertechs = (
        await retrieve_loanertechs()
        if authenticated
        else await retrieve_loanertechs_unauthenticated()
    )
    return JSONResponse(
        {"data": loanertechs, "message": "LoanerTech data retrieved successfully"}
    )


@router.post(
    "/",
    response_description="LoanerTech data added into the database",
    response_model=LoanerTechResponse,
)
async def add_loanertech_data(
    loanertech: LoanerTechRequest = Body(...),
    auth: dict = Depends(required_auth),
) -> LoanerTechResponse:

    dict_loanertech = jsonable_encoder(loanertech)
    new_loanertech = await add_loanertech(dict_loanertech)
    return LoanerTechResponse(
        data=new_loanertech, message="LoanerTech added successfully."
    )


@router.get("/{id}", response_description="LoanerTech data retrieved")
async def get_loanertech_data(id: int) -> LoanerTechResponse:
    loanertech = await retrieve_loanertech(id)
    if loanertech:
        return LoanerTechResponse(
            data=loanertech, message="LoanerTech data retrieved successfully"
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Failed to find loanertech"
    )


@router.put(
    "/update/{id}",
    response_description="LoanerTech data updated",
    response_model=BoolResponse,
)
async def update_loanertech_data(
    id: int,
    req: LoanerTechRequest = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_req = jsonable_encoder(req)
    if await update_loanertech(id, dict_req):
        return BoolResponse(data=True, message="LoanerTech name updated successfully")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Failed to update loanertech"
    )


@router.delete(
    "/delete/{id}",
    response_description="LoanerTech data deleted from the database",
    response_model=BoolResponse,
)
async def delete_loanertech_data(
    id: int,
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    if await delete_loanertech(id):
        return BoolResponse(data=True, message="LoanerTech deleted successfully")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to add checkout loanertech",
    )


@router.put(
    "/checkout",
    response_description="Checked out LAF items",
    response_model=BoolResponse,
)
async def checkout_loanertech(
    req: LoanerTechCheckout = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_req = jsonable_encoder(req)
    item = {
        "in_office": False,
        "phone": dict_req["phone_number"],
        "email": dict_req["email"],
        "name": dict_req["name"],
    }
    for id in dict_req["ids"]:
        if not await update_loanertech(id, item):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add checkout loanertech",
            )

    return BoolResponse(data=True, message="LoanerTech checked out successfully")


checkin_item = {
    "in_office": True,
    "phone": "",
    "email": "",
    "name": "",
}


@router.put(
    "/checkin", response_description="Checked in LAF items", response_model=BoolResponse
)
async def checkin_loanertech(
    req: LoanerTechCheckin = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_req = jsonable_encoder(req)
    for id in dict_req["ids"]:
        if not await update_loanertech(id, checkin_item):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add checking loanertech",
            )

    return BoolResponse(data=True, message="LoanerTech checked in successfully")
