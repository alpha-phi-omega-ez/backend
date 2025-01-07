from typing import Optional, Tuple

from fastapi import APIRouter, Body, Depends, Query, HTTPException, status
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
from server.models.laf import (
    DateFilter,
    DateString,
    LAFArchiveItems,
    LAFFoundItem,
    LAFItemRequest,
    LAFLocation,
    LAFType,
    LostReportRequest,
    LAFItemResponse,
    LAFItemsResponse,
    ExpireLAFItemsReponse,
    LostReportItemResponse,
    LostReportItemsResponse,
)
from server.models import BoolResponse, StringListResponse

router = APIRouter()


# LAF Type routes


@router.get(
    "/types/",
    response_description="LAF types list retrieved",
    response_model=StringListResponse,
)
async def get_laf_types() -> StringListResponse:
    laf_types = await retrieve_laf_types()
    return StringListResponse(
        data=laf_types, message="Laf types data retrieved successfully"
    )


@router.post(
    "/type/",
    response_description="Created a new LAF Type",
    response_model=BoolResponse,
)
async def new_laf_type(
    laf_type: LAFType = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf_type = jsonable_encoder(laf_type)
    if await add_laf_type(dict_laf_type["type"]):
        return BoolResponse(data=True, message="LAF type added successfully")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to add LAF type",
    )


@router.delete(
    "/type/", response_description="Delete a LAF type", response_model=BoolResponse
)
async def delete_laf_type_route(
    laf_type: LAFType = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf_type = jsonable_encoder(laf_type)
    if await delete_laf_type(dict_laf_type["location"]):
        return BoolResponse(data=True, message="LAF location added successfully")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete LAF type",
    )


# LAF Location routes


@router.get(
    "/locations/",
    response_description="LAF locations list retrieved",
    response_model=StringListResponse,
)
async def get_laf_locations() -> StringListResponse:
    laf_locations = await retrieve_laf_locations()
    return StringListResponse(
        data=laf_locations, message="Laf locations data retrieved successfully"
    )


@router.post(
    "/location/",
    response_description="Created a new LAF Location",
    response_model=BoolResponse,
)
async def new_laf_location(
    laf_location: LAFLocation = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf_location = jsonable_encoder(laf_location)
    if await add_laf_location(dict_laf_location["location"]):
        return BoolResponse(data=True, message="LAF location added successfully")
    raise HTTPException(status_code=500, detail="Failed to add LAF location")


@router.delete(
    "/location/",
    response_description="Delete a LAF location",
    response_model=BoolResponse,
)
async def delete_laf_location_route(
    laf_location: LAFLocation = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf_location = jsonable_encoder(laf_location)
    if await delete_laf_location(dict_laf_location["location"]):
        return BoolResponse(data=True, message="LAF location added successfully")
    raise HTTPException(status_code=500, detail="Failed to delete LAF location")


# LAF Item routes


@router.post(
    "/item/",
    response_description="Created a new LAF item",
    response_model=LAFItemResponse,
)
async def new_laf_item(
    laf_item: LAFItemRequest = Body(...),
    auth: dict = Depends(required_auth),
) -> LAFItemResponse:

    dict_laf = jsonable_encoder(laf_item)
    new_laf_item = await add_laf(dict_laf)
    return LAFItemResponse(data=new_laf_item, message="LAF added successfully")


@router.get(
    "/items/",
    response_description="Filter for LAF items",
    response_model=LAFItemsResponse,
)
async def get_laf_items(
    date: Optional[DateString] = Query(None, description="Date of the item"),
    dateFilter: Optional[DateFilter] = Query(None, description="Filter for date"),
    location: Optional[list[str]] = Query(
        None, description="List of possible locations"
    ),
    description: Optional[str] = Query(None, description="Description of the item"),
    type: Optional[str] = Query(None, description="Type of the item"),
    archived: bool = Query(False, description="Archived items"),
    auth: dict = Depends(required_auth),
) -> LAFItemsResponse:

    dict_laf_filters = {
        "date": date,
        "dateFilter": dateFilter,
        "location": location,
        "description": description,
        "type": type,
    }

    laf_items = await retrieve_laf_items(dict_laf_filters, archived)
    return LAFItemsResponse(data=laf_items, message="Retrieved LAF items")


@router.get(
    "/items/expired/",
    response_description="Filter for LAF items",
    response_model=ExpireLAFItemsReponse,
)
async def get_laf_items_expired(
    water_bottle: int = Query(30, description="Water Bottle days to expiration"),
    clothing: int = Query(90, description="Clothing days to expiration"),
    umbrella: int = Query(90, description="Umbrella days to expiration"),
    inexpensive: int = Query(180, description="Inexpensive days to expiration"),
    expensive: int = Query(365, description="Expensive days to expiration"),
    type: str = Query("All", description="Type of the item"),
    auth: dict = Depends(required_auth),
) -> ExpireLAFItemsReponse:

    laf_items = await retrieve_expired_laf(
        water_bottle, clothing, umbrella, inexpensive, expensive, type
    )
    return ExpireLAFItemsReponse(data=laf_items, message="Retrieved expired LAF items")


@router.put(
    "/item/found/{id}",
    response_description="Found a LAF item",
    response_model=BoolResponse,
)
async def found_laf_item_route(
    id: str,
    laf_found: LAFFoundItem = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    laf_found_dict = jsonable_encoder(laf_found)
    if await found_laf_item(id, laf_found_dict):
        return BoolResponse(data=True, message="LAF item updated successfully")
    raise HTTPException(status_code=500, detail="Failed to mark LAF item as found")


@router.put(
    "/item/{id}", response_description="Update a LAF item", response_model=BoolResponse
)
async def update_laf_item_route(
    id: str,
    laf_item: LAFItemRequest = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf = jsonable_encoder(laf_item)
    if await update_laf_item(id, dict_laf):
        return BoolResponse(data=True, message="LAF item updated successfully")
    raise HTTPException(status_code=500, detail="Failed to update LAF")


@router.post(
    "/items/archive/",
    response_description="Archive LAF items",
    response_model=BoolResponse,
)
async def archive_laf_items_route(
    laf_items: LAFArchiveItems = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_laf = jsonable_encoder(laf_items)
    await archive_laf_items(dict_laf["ids"])
    return BoolResponse(data=True, message="LAF items archived successfully")


# Lost Report Routes


@router.post(
    "/report/",
    response_description="Created a new Lost Report",
    response_model=LostReportItemResponse,
)
async def new_lost_report(
    lost_report: LostReportRequest = Body(...),
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check),
) -> LostReportItemResponse:
    authenticated = auth[0]

    dict_lost_report = jsonable_encoder(lost_report)
    dict_lost_report["location"] = [
        location.strip() for location in dict_lost_report["location"].split(",")
    ]
    new_lost_report = await add_lost_report(dict_lost_report, authenticated)
    return LostReportItemResponse(
        data=new_lost_report, message="Lost report added successfully"
    )


@router.get(
    "/reports/",
    response_description="Filter for Lost Reports",
    response_model=LostReportItemsResponse,
)
async def get_lost_reports(
    date: Optional[DateString] = Query(None, description="Date of the item"),
    dateFilter: Optional[DateFilter] = Query(None, description="Filter for date"),
    location: Optional[list[str]] = Query(
        None, description="List of possible locations"
    ),
    description: Optional[str] = Query(None, description="Description of the item"),
    type: Optional[str] = Query(None, description="Type of the item"),
    name: Optional[str] = Query(None, description="Name of the owner"),
    email: Optional[str] = Query(None, description="Email of the owner"),
    archived: bool = Query(False, description="Archived items"),
    auth: bool = Depends(required_auth),
) -> LostReportItemsResponse:

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
    return LostReportItemsResponse(data=lost_reports, message="Retrieved Lost Reports")


@router.put(
    "/report/found/{id}",
    response_description="Found a Lost Report",
    response_model=BoolResponse,
)
async def found_lost_report_route(
    id: str,
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    if await found_lost_report(id):
        return BoolResponse(data=True, message="Lost Report updated successfully")
    raise HTTPException(status_code=500, detail="Failed to mark a Lost Report as found")


@router.put(
    "/report/{id}",
    response_description="Update a Lost Report",
    response_model=BoolResponse,
)
async def update_lost_report_route(
    id: str,
    lost_report: LostReportRequest = Body(...),
    auth: dict = Depends(required_auth),
) -> BoolResponse:

    dict_lost_report = jsonable_encoder(lost_report)
    dict_lost_report["location"] = dict_lost_report["location"].split(",")
    if await update_lost_report_item(id, dict_lost_report):
        return BoolResponse(data=True, message="Lost Report updated successfully")
    raise HTTPException(status_code=500, detail="Failed to update a Lost Report")
