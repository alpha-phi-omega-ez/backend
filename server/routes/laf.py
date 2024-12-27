from typing import Any, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from server.database.laf import (
    add_laf,
    add_laf_location,
    add_laf_type,
    add_lost_report,
    delete_laf_location,
    delete_laf_type,
    retrieve_laf_items,
    retrieve_laf_locations,
    retrieve_laf_types,
    retrieve_lost_reports,
)
from server.helpers.auth import simple_auth_check
from server.models import ErrorResponseModel, ResponseModel
from server.models.laf import (
    DateFilter,
    DateString,
    LAFLocation,
    LAFType,
    NewLAFItem,
    NewLostReport,
)

router = APIRouter()


@router.get("/types/", response_description="LAF types list retrieved")
async def get_laf_types() -> dict[str, Any]:
    laf_types = await retrieve_laf_types()
    if len(laf_types) > 0:
        return ResponseModel(laf_types, "Laf types data retrieved successfully")
    return ResponseModel(laf_types, "Empty list returned")


@router.get("/locations/", response_description="LAF locations list retrieved")
async def get_laf_locations() -> dict[str, Any]:
    laf_locations = await retrieve_laf_locations()
    if len(laf_locations) > 0:
        return ResponseModel(laf_locations, "Laf locations data retrieved successfully")
    return ResponseModel(laf_locations, "Empty list returned")


@router.post("/item/", response_description="Created a new LAF item")
async def new_laf_item(
    laf_item: NewLAFItem = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf = jsonable_encoder(laf_item)
    new_laf_item = await add_laf(dict_laf)
    return ResponseModel(new_laf_item, "LAF added successfully")


@router.post("/report/", response_description="Created a new Lost Report")
async def new_lost_report(
    lost_report: NewLostReport = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, _, _ = auth

    dict_lost_report = jsonable_encoder(lost_report)
    dict_lost_report["location"] = dict_lost_report["location"].split(",")
    new_lost_report = await add_lost_report(dict_lost_report, authenticated)
    return ResponseModel(new_lost_report, "LAF added successfully")


@router.post("/location/", response_description="Created a new LAF Location")
async def new_laf_location(
    laf_location: LAFLocation = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf_location = jsonable_encoder(laf_location)
    new_location = await add_laf_location(dict_laf_location["location"])
    return ResponseModel(new_location, "LAF location added successfully")


@router.post("/type/", response_description="Created a new LAF Type")
async def new_laf_type(
    laf_type: LAFType = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf_type = jsonable_encoder(laf_type)
    new_type = await add_laf_type(dict_laf_type["type"])
    return ResponseModel(new_type, "LAF type added successfully")


@router.delete("/location/", response_description="Delete a LAF location")
async def delete_laf_location_route(
    laf_location: LAFLocation = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf_location = jsonable_encoder(laf_location)
    if await delete_laf_location(dict_laf_location["location"]):
        return ResponseModel({"delete": True}, "LAF location added successfully")
    return ErrorResponseModel(
        "Failed to delete LAF location", 500, "Failed to delete LAF location"
    )


@router.delete("/type/", response_description="Delete a LAF type")
async def delete_laf_type_route(
    laf_type: LAFType = Body(...),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf_type = jsonable_encoder(laf_type)
    if await delete_laf_type(dict_laf_type["location"]):
        return ResponseModel({"delete": True}, "LAF location added successfully")
    return ErrorResponseModel(
        "Failed to delete LAF type", 500, "Failed to delete LAF type"
    )


@router.get("/items/", response_description="Filter for LAF items")
async def get_laf_items(
    date: Optional[DateString] = Query(None, description="Date of the item"),
    dateFilter: Optional[DateFilter] = Query(None, description="Filter for date"),
    location: Optional[List[str]] = Query(
        None, description="List of possible locations"
    ),
    description: Optional[str] = Query(None, description="Description of the item"),
    type: Optional[str] = Query(None, description="Type of the item"),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_laf_filters = {
        "date": date,
        "dateFilter": dateFilter,
        "location": location,
        "description": description,
        "type": type,
    }

    laf_items = await retrieve_laf_items(dict_laf_filters)
    return ResponseModel(laf_items, "Retrieved LAF items")


@router.get("/reports/", response_description="Filter for Lost Reports")
async def get_lost_reports(
    date: Optional[DateString] = Query(None, description="Date of the item"),
    dateFilter: Optional[DateFilter] = Query(None, description="Filter for date"),
    location: Optional[List[str]] = Query(
        None, description="List of possible locations"
    ),
    description: Optional[str] = Query(None, description="Description of the item"),
    type: Optional[str] = Query(None, description="Type of the item"),
    name: Optional[str] = Query(None, description="Name of the owner"),
    email: Optional[str] = Query(None, description="Email of the owner"),
    auth: Tuple[bool, str, Any] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated, message, _ = auth
    if not authenticated:
        raise HTTPException(status_code=401, detail=message)

    dict_lost_report_filters = {
        "date": date,
        "dateFilter": dateFilter,
        "location": location,
        "description": description,
        "type": type,
        "name": name,
        "email": email,
    }
    lost_reports = await retrieve_lost_reports(dict_lost_report_filters)
    return ResponseModel(lost_reports, "Retrieved Lost Reports")
