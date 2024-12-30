from typing import Any, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, Query
from fastapi.encoders import jsonable_encoder

from server.database.laf import (
    add_laf,
    add_laf_location,
    add_laf_type,
    add_lost_report,
    archive_laf_items,
    delete_laf_location,
    delete_laf_type,
    found_laf_item,
    found_lost_report,
    retrieve_expired_laf,
    retrieve_laf_items,
    retrieve_laf_locations,
    retrieve_laf_types,
    retrieve_lost_reports,
    update_laf_item,
    update_lost_report_item,
)
from server.helpers.auth import required_auth, simple_auth_check
from server.models import ErrorResponseModel, ResponseModel
from server.models.laf import (
    DateFilter,
    DateString,
    LAFArchiveItems,
    LAFFoundItem,
    LAFItem,
    LAFLocation,
    LAFType,
    LostReport,
)

router = APIRouter()


# LAF Type routes


@router.get("/types/", response_description="LAF types list retrieved")
async def get_laf_types() -> dict[str, Any]:
    laf_types = await retrieve_laf_types()
    return ResponseModel(laf_types, "Laf types data retrieved successfully")


@router.post("/type/", response_description="Created a new LAF Type")
async def new_laf_type(
    laf_type: LAFType = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf_type = jsonable_encoder(laf_type)
    new_type = await add_laf_type(dict_laf_type["type"])
    if new_type:
        return ResponseModel(new_type, "LAF type added successfully")
    return ErrorResponseModel("Failed to add LAF type", 500, "Failed to add LAF type")


@router.delete("/type/", response_description="Delete a LAF type")
async def delete_laf_type_route(
    laf_type: LAFType = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf_type = jsonable_encoder(laf_type)
    if await delete_laf_type(dict_laf_type["location"]):
        return ResponseModel({"delete": True}, "LAF location added successfully")
    return ErrorResponseModel(
        "Failed to delete LAF type", 500, "Failed to delete LAF type"
    )


# LAF Location routes


@router.get("/locations/", response_description="LAF locations list retrieved")
async def get_laf_locations() -> dict[str, Any]:
    laf_locations = await retrieve_laf_locations()
    return ResponseModel(laf_locations, "Laf locations data retrieved successfully")


@router.post("/location/", response_description="Created a new LAF Location")
async def new_laf_location(
    laf_location: LAFLocation = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf_location = jsonable_encoder(laf_location)
    new_location = await add_laf_location(dict_laf_location["location"])
    if new_location:
        return ResponseModel(new_location, "LAF location added successfully")
    return ErrorResponseModel(
        "Failed to add LAF location", 500, "Failed to add LAF location"
    )


@router.delete("/location/", response_description="Delete a LAF location")
async def delete_laf_location_route(
    laf_location: LAFLocation = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf_location = jsonable_encoder(laf_location)
    if await delete_laf_location(dict_laf_location["location"]):
        return ResponseModel({"delete": True}, "LAF location added successfully")
    return ErrorResponseModel(
        "Failed to delete LAF location", 500, "Failed to delete LAF location"
    )


# LAF Item routes


@router.post("/item/", response_description="Created a new LAF item")
async def new_laf_item(
    laf_item: LAFItem = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf = jsonable_encoder(laf_item)
    new_laf_item = await add_laf(dict_laf)
    if new_laf_item:
        return ResponseModel(new_laf_item, "LAF added successfully")
    return ErrorResponseModel("Failed to add LAF item", 500, "Failed to add LAF item")


@router.get("/items/", response_description="Filter for LAF items")
async def get_laf_items(
    date: Optional[DateString] = Query(None, description="Date of the item"),
    dateFilter: Optional[DateFilter] = Query(None, description="Filter for date"),
    location: Optional[List[str]] = Query(
        None, description="List of possible locations"
    ),
    description: Optional[str] = Query(None, description="Description of the item"),
    type: Optional[str] = Query(None, description="Type of the item"),
    archived: bool = Query(False, description="Archived items"),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf_filters = {
        "date": date,
        "dateFilter": dateFilter,
        "location": location,
        "description": description,
        "type": type,
    }

    laf_items = await retrieve_laf_items(dict_laf_filters, archived)
    return ResponseModel(laf_items, "Retrieved LAF items")


@router.get("/items/expired/", response_description="Filter for LAF items")
async def get_laf_items_expired(
    water_bottle: int = Query(30, description="Water Bottle days to expiration"),
    clothing: int = Query(90, description="Clothing days to expiration"),
    umbrella: int = Query(90, description="Umbrella days to expiration"),
    inexpensive: int = Query(180, description="Inexpensive days to expiration"),
    expensive: int = Query(365, description="Expensive days to expiration"),
    type: str = Query("All", description="Type of the item"),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    laf_items = await retrieve_expired_laf(
        water_bottle, clothing, umbrella, inexpensive, expensive, type
    )
    return ResponseModel(laf_items, "Retrieved expired LAF items")


@router.put("/item/found/{id}", response_description="Found a LAF item")
async def found_laf_item_route(
    id: str,
    laf_found: LAFFoundItem = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    laf_found_dict = jsonable_encoder(laf_found)
    updated_laf_item = await found_laf_item(id, laf_found_dict)
    if updated_laf_item:
        return ResponseModel(updated_laf_item, "LAF item updated successfully")
    return ErrorResponseModel(
        "Failed to update LAF item", 500, "Failed to update LAF item"
    )


@router.put("/item/{id}", response_description="Update a LAF item")
async def update_laf_item_route(
    id: str,
    laf_item: LAFItem = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf = jsonable_encoder(laf_item)
    updated_laf_item = await update_laf_item(id, dict_laf)
    if updated_laf_item:
        return ResponseModel(updated_laf_item, "LAF item updated successfully")
    return ErrorResponseModel(
        "Failed to update LAF item", 500, "Failed to update LAF item"
    )


@router.post("/items/archive/", response_description="Archive LAF items")
async def archive_laf_items_route(
    laf_items: LAFArchiveItems = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_laf = jsonable_encoder(laf_items)

    print("DICT LAF", dict_laf)

    await archive_laf_items(dict_laf["ids"])
    return ResponseModel({"archive": True}, "LAF items archived successfully")


# Lost Report Routes


@router.post("/report/", response_description="Created a new Lost Report")
async def new_lost_report(
    lost_report: LostReport = Body(...),
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check),
) -> dict[str, Any]:
    authenticated = auth[0]

    dict_lost_report = jsonable_encoder(lost_report)
    dict_lost_report["location"] = dict_lost_report["location"].split(",")
    new_lost_report = await add_lost_report(dict_lost_report, authenticated)
    if new_lost_report:
        return ResponseModel(new_lost_report, "Lost report added successfully")
    return ErrorResponseModel(
        "Failed to add Lost Report", 500, "Failed to add Lost Report"
    )


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
    archived: bool = Query(False, description="Archived items"),
    auth: bool = Depends(required_auth),
) -> dict[str, Any]:

    dict_lost_report_filters = {
        "date": date,
        "dateFilter": dateFilter,
        "location": location,
        "description": description,
        "type": type,
        "name": name,
        "email": email,
    }
    lost_reports = await retrieve_lost_reports(dict_lost_report_filters, archived)
    return ResponseModel(lost_reports, "Retrieved Lost Reports")


@router.put("/report/found/{id}", response_description="Found a Lost Report")
async def found_lost_report_route(
    id: str,
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    updated_lost_report = await found_lost_report(id)
    if updated_lost_report:
        return ResponseModel(updated_lost_report, "Lost Report updated successfully")
    return ErrorResponseModel(
        "Failed to update Lost Report", 404, "Failed to update Lost Report"
    )


@router.put("/report/{id}", response_description="Update a Lost Report")
async def update_lost_report_route(
    id: str,
    lost_report: LostReport = Body(...),
    auth: dict = Depends(required_auth),
) -> dict[str, Any]:

    dict_lost_report = jsonable_encoder(lost_report)
    updated_lost_report = await update_lost_report_item(id, dict_lost_report)
    if updated_lost_report:
        return ResponseModel(updated_lost_report, "Lost Report updated successfully")
    return ErrorResponseModel(
        "Failed to update Lost Report", 404, "Failed to update Lost Report"
    )
