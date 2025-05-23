import re
from asyncio import gather
from datetime import datetime
from typing import Union

from aiocache import cached
from bson import ObjectId
from fastapi import HTTPException, status

from server.database import database
from server.helpers.db import (
    async_dict_itr,
    datetime_time_delta,
    get_next_sequence_value,
)
from server.models.laf import ArchivedLAFItem, ExpiredItem, LAFItem, LostReportItem

sequence_id_collection = database.get_collection("sequence_id")
laf_items_collection = database.get_collection("laf_items")
lost_reports_collection = database.get_collection("lost_reports")
laf_types_collection = database.get_collection("laf_types")
laf_locations_collection = database.get_collection("laf_locations")
laf_matching_collection = database.get_collection("laf_matching")


async def laf_db_setup() -> None:
    await laf_items_collection.create_index("date")
    await lost_reports_collection.create_index("date")
    await laf_items_collection.create_index([("description", "text")])
    await lost_reports_collection.create_index([("description", "text")])


# Cache for 1 hour
@cached(ttl=3600)
async def get_type_id(type_in: str) -> ObjectId:
    laf_type = await laf_types_collection.find_one({"type": type_in})
    if not laf_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="LAF Type not found"
        )
    return laf_type["_id"]


# Cache for 1 day
@cached(ttl=86400)
async def get_type_from_id(id: ObjectId) -> dict:
    laf_type = await laf_types_collection.find_one({"_id": id})
    if not laf_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="LAF Type not found"
        )
    return laf_type


# Helper functions to convert MongoDB documents to Python dictionaries
async def laf_helper(laf: dict) -> LAFItem:
    date = laf["date"]
    laf_type = await get_type_from_id(laf["type_id"])

    return {
        "id": laf["_id"],
        "type": laf_type["type"],
        "display_id": f"{laf_type['letter']}{laf['_id']}",
        "location": laf["location"],
        "date": f"{date[5:7]}/{date[8:]}/{date[:4]}",
        "description": laf["description"],
    }


async def laf_archived_helper(laf: dict) -> ArchivedLAFItem:
    returned_date = laf["returned"]
    date = laf["date"]
    laf_type = await get_type_from_id(laf["type_id"])

    return {
        "id": laf["_id"],
        "type": laf_type["type"],
        "display_id": f"{laf_type['letter']}{laf['_id']}",
        "location": laf["location"],
        "date": f"{date[5:7]}/{date[8:]}/{date[:4]}",
        "description": laf["description"],
        "found": laf["found"],
        "archived": laf["archived"],
        "name": laf["name"],
        "email": laf["email"],
        "returned": f"{returned_date[5:7]}/{returned_date[8:]}/{returned_date[:4]}",
    }


async def lost_report_helper(lost_report: dict) -> LostReportItem:
    date = lost_report["date"]
    laf_type = await get_type_from_id(lost_report["type_id"])

    return {
        "id": str(lost_report["_id"]),
        "name": lost_report["name"],
        "email": lost_report["email"],
        "type": laf_type["type"],
        "location": [location.strip() for location in lost_report["location"]],
        "date": f"{date[5:7]}/{date[8:]}/{date[:4]}",
        "description": lost_report["description"],
        "found": lost_report["found"],
        "archived": lost_report["archived"],
    }


# LAF Queries


# Add a new laf item into to the database
async def add_laf(laf_data: dict) -> LAFItem:
    type_id = await get_type_id(laf_data["type"])
    del laf_data["type"]

    now = datetime.now()

    laf_data["_id"] = await get_next_sequence_value("laf_id", sequence_id_collection)
    laf_data["description"] = laf_data["description"].strip()
    laf_data["found"] = False
    laf_data["archived"] = False
    laf_data["created"] = now
    laf_data["updated"] = now
    laf_data["name"] = None
    laf_data["email"] = None
    laf_data["returned"] = None
    laf_data["type_id"] = type_id

    laf_item = await laf_items_collection.insert_one(laf_data)
    new_laf_item = await laf_items_collection.find_one({"_id": laf_item.inserted_id})
    if new_laf_item:
        return await laf_helper(new_laf_item)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create LAF item",
    )


async def update_laf(laf_id: str, laf_data: dict, now: datetime) -> bool:
    laf_item = await laf_items_collection.find_one({"_id": int(laf_id)})
    if laf_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Laf item with id {laf_id} not found",
        )

    laf_data["updated"] = now
    if laf_data.get("type", False):
        type_id = await get_type_id(laf_data["type"])
        del laf_data["type"]
        laf_data["type_id"] = type_id

    updated_laf_item = await laf_items_collection.update_one(
        {"_id": int(laf_id)}, {"$set": laf_data}
    )
    if updated_laf_item.modified_count == 1:
        return True

    return False


async def found_laf_item(laf_id: str, laf_found: dict) -> bool:
    now = datetime.now()

    laf_found["found"] = True
    laf_found["archived"] = True
    laf_found["returned"] = now

    return await update_laf(laf_id, laf_found, now)


async def update_laf_item(laf_id: str, laf_data: dict) -> bool:
    now = datetime.now()

    return await update_laf(laf_id, laf_data, now)


async def archive_laf_items(ids: list[str]) -> None:
    now = datetime.now()
    await laf_items_collection.update_many(
        {"_id": {"$in": [int(id) for id in ids]}},
        {"$set": {"archived": True, "updated": now}},
    )


laf_item_query_mapping = {
    "dateFilter": lambda v, laf_query_data: (
        {"date": {"$lte": laf_query_data["date"]}}
        if v == "Before"
        else {"date": {"$gte": laf_query_data["date"]}}
    ),
    "location": lambda v, _: {"location": {"$in": v}},
    "description": lambda v, _: {
        "description": {"$regex": re.escape(v.strip()), "$options": "i"}
    },
}


# Retrieve all relevant laf items from the database
async def retrieve_laf_items(laf_query_data: dict, archived: bool = False) -> list:
    query: dict[str, Union[bool, dict, ObjectId, str, int]] = {"archived": archived}
    if laf_query_data["id"]:
        query["_id"] = int(laf_query_data["id"])
    else:
        async for k, v in async_dict_itr(laf_query_data):
            if v is not None and k in laf_item_query_mapping:
                query.update(laf_item_query_mapping[k](v, laf_query_data))
            elif k == "type" and v:
                query["type_id"] = await get_type_id(v)

    laf_items = []
    # Use .skip before limit for pagination
    async for laf_item in laf_items_collection.find(query).sort("date", -1).limit(30):
        if archived:
            laf_items.append(await laf_archived_helper(laf_item))
        else:
            laf_items.append(await laf_helper(laf_item))
    return laf_items


@cached(ttl=86400)
async def water_bottle_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, wb)
    type_id = await get_type_id("Water Bottle")
    return {
        "type_id": type_id,
        "date": {"$lte": cutoff_date},
    }


@cached(ttl=86400)
async def attire_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, c)
    type_id = await get_type_id("Attire")

    return {
        "type_id": type_id,
        "date": {"$lte": cutoff_date},
    }


@cached(ttl=86400)
async def umbrella_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, u)
    type_id = await get_type_id("Umbrellas")

    return {
        "type_id": type_id,
        "date": {"$lte": cutoff_date},
    }


type_expiration_mapping = {
    "Water Bottle": water_bottle_expiration_query,
    "Attire": attire_expiration_query,
    "Umbrellas": umbrella_expiration_query,
}


async def fetch_expired_laf_items(expired_query: dict) -> list[LAFItem]:
    expired_laf_items = []
    async for laf_item in (
        laf_items_collection.find(expired_query).sort("date", -1).limit(30)
    ):
        expired_laf_items.append(await laf_helper(laf_item))

    return expired_laf_items


async def fetch_potentially_expired_laf_items(
    potentially_expired_query: dict,
) -> list[LAFItem]:
    potentially_expired_laf_items = []
    async for laf_item in (
        laf_items_collection.find(potentially_expired_query).sort("date", -1).limit(30)
    ):
        potentially_expired_laf_items.append(await laf_helper(laf_item))

    return potentially_expired_laf_items


async def retrieve_expired_laf(
    water_bottle_expiration: int,
    attire_expiration: int,
    umbrella_expiration: int,
    inexpensive_expiration: int,
    expensive_expiration: int,
    type: str,
) -> ExpiredItem:
    now = datetime.now()

    if type == "All":
        wb, a, u, expensive_cutoff_date, inexpensive_cutoff_date = await gather(
            water_bottle_expiration_query(
                water_bottle_expiration,
                attire_expiration,
                umbrella_expiration,
                now,
            ),
            attire_expiration_query(
                water_bottle_expiration,
                attire_expiration,
                umbrella_expiration,
                now,
            ),
            umbrella_expiration_query(
                water_bottle_expiration,
                attire_expiration,
                umbrella_expiration,
                now,
            ),
            datetime_time_delta(now, expensive_expiration),
            datetime_time_delta(now, inexpensive_expiration),
        )

        type_ids = []
        for type in type_expiration_mapping.keys():
            type_id = await get_type_id(type)
            type_ids.append(type_id)

        expired_query = {
            "archived": False,
            "$or": [
                wb,
                a,
                u,
                {
                    "type_id": {"$nin": type_ids},
                    "date": {"$lte": expensive_cutoff_date},
                },
            ],
        }

        potentially_expired_query = {
            "archived": False,
            "date": {"$lte": inexpensive_cutoff_date, "$gt": expensive_cutoff_date},
        }

        expired_laf_items, potentially_expired_laf_items = await gather(
            fetch_expired_laf_items(expired_query),
            fetch_potentially_expired_laf_items(potentially_expired_query),
        )

        return {
            "expired": expired_laf_items,
            "potential": potentially_expired_laf_items,
        }

    if type in type_expiration_mapping:
        query = {"archived": False}
        query.update(
            await type_expiration_mapping[type](
                water_bottle_expiration, attire_expiration, umbrella_expiration, now
            )
        )

        laf_items = []
        async for laf_item in (
            laf_items_collection.find(query).sort("date", -1).limit(30)
        ):
            laf_items.append(await laf_helper(laf_item))

        return {
            "expired": laf_items,
            "potential": [],
        }

    expensive_cutoff_date, inexpensive_cutoff_date = await gather(
        datetime_time_delta(now, expensive_expiration),
        datetime_time_delta(now, inexpensive_expiration),
    )

    type_id = await get_type_id(type)
    expired_query = {
        "archived": False,
        "date": {"$lte": expensive_cutoff_date},
        "type_id": type_id,
    }
    potentially_expired_query = {
        "archived": False,
        "date": {"$lte": inexpensive_cutoff_date, "$gt": expensive_cutoff_date},
        "type_id": type_id,
    }

    expired_laf_items, potentially_expired_laf_items = await gather(
        fetch_expired_laf_items(expired_query),
        fetch_potentially_expired_laf_items(potentially_expired_query),
    )

    return {
        "expired": expired_laf_items,
        "potential": potentially_expired_laf_items,
    }


# Lost Report Queries


# Add a new lost report into to the database
async def add_lost_report(lost_report_data: dict, auth: bool) -> LostReportItem:
    type_id = await get_type_id(lost_report_data["type"])
    del lost_report_data["type"]
    now = datetime.now()
    lost_report_data["description"] = lost_report_data["description"].strip()
    lost_report_data["name"] = lost_report_data["name"].strip()
    lost_report_data["email"] = lost_report_data["email"].strip()
    lost_report_data["found"] = False
    lost_report_data["archived"] = False
    lost_report_data["created"] = now
    lost_report_data["updated"] = now
    lost_report_data["viewed"] = auth
    lost_report_data["type_id"] = type_id

    lost_report = await lost_reports_collection.insert_one(lost_report_data)
    new_lost_report = await lost_reports_collection.find_one(
        {"_id": lost_report.inserted_id}
    )
    if new_lost_report:
        return await lost_report_helper(new_lost_report)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create Lost Report",
    )


async def update_lost_report(
    lost_report_id: str, lost_report_data: dict, now: datetime
) -> bool:
    lost_report_id_bson = ObjectId(lost_report_id)
    lost_report = await lost_reports_collection.find_one({"_id": lost_report_id_bson})
    if lost_report is None:
        return False

    lost_report_data["updated"] = now
    lost_report_data["viewed"] = True
    if lost_report_data.get("type", False):
        type_id = await get_type_id(lost_report_data["type"])
        del lost_report_data["type"]
        lost_report_data["type_id"] = type_id

    updated_lost_report = await lost_reports_collection.update_one(
        {"_id": lost_report_id_bson}, {"$set": lost_report_data}
    )
    if updated_lost_report.modified_count == 1:
        return True

    return False


async def found_lost_report(lost_report_id: str) -> bool:
    now = datetime.now()

    lost_report_found = {
        "found": True,
        "archived": True,
        "returned": now,
    }

    return await update_lost_report(lost_report_id, lost_report_found, now)


async def update_lost_report_item(lost_report_id: str, lost_report_data: dict) -> bool:
    now = datetime.now()

    return await update_lost_report(lost_report_id, lost_report_data, now)


async def retrieve_new_lost_report_count() -> int:
    return await lost_reports_collection.count_documents(
        {"viewed": False, "archived": False}
    )


async def retrieve_new_lost_reports(limit: int = 30) -> list:
    lost_reports = []
    async for laf_item in (
        lost_reports_collection.find({"viewed": False, "archived": False})
        .sort("date", -1)
        .limit(limit)
    ):
        lost_reports.append(await lost_report_helper(laf_item))
    return lost_reports


async def mark_lost_report_as_viewed(lost_report_id: str) -> bool:
    now = datetime.now()
    return await update_lost_report(lost_report_id, {"viewed": True}, now)


lost_report_query_mapping = {
    "dateFilter": lambda v, lost_report_query_data: (
        {"date": {"$lte": lost_report_query_data["date"]}}
        if v == "Before"
        else {"date": {"$gte": lost_report_query_data["date"]}}
    ),
    "description": lambda v, _: {
        "description": {"$regex": re.escape(v.strip()), "$options": "i"}
    },
    "location": lambda v, _: {"location": {"$in": v}},
    "name": lambda v, _: {"name": {"$regex": re.escape(v.strip()), "$options": "i"}},
    "email": lambda v, _: {"email": {"$regex": re.escape(v.strip()), "$options": "i"}},
}


# Retrieve all relevant lost reports from the database
async def retrieve_lost_reports(
    lost_report_query_data: dict, archived: bool = False
) -> list:
    query: dict[str, Union[bool, dict, ObjectId, str]] = {"archived": archived}
    async for k, v in async_dict_itr(lost_report_query_data):
        if v is not None and k in lost_report_query_mapping:
            query.update(lost_report_query_mapping[k](v, lost_report_query_data))
        elif k == "type" and v:
            query["type_id"] = await get_type_id(v)

    lost_reports = []
    # Use .skip before limit for pagination
    async for laf_item in (
        lost_reports_collection.find(query).sort("date", -1).limit(30)
    ):
        lost_reports.append(await lost_report_helper(laf_item))
    return lost_reports


@cached(ttl=86400)
async def retrieve_laf_types() -> list[str]:
    laf_types = await laf_types_collection.find({"view": True}).to_list(length=None)
    return [laf_type["type"] for laf_type in laf_types]


async def add_laf_type(laf_type: str) -> bool:
    laf_type_added = await laf_types_collection.insert_one({"type": laf_type})
    new_laf_type = await laf_items_collection.find_one(
        {"_id": laf_type_added.inserted_id}
    )
    return new_laf_type is not None


async def delete_laf_type(laf_type: str) -> bool:
    laf_type_deleted = await laf_types_collection.delete_one({"type": laf_type})
    return laf_type_deleted.deleted_count > 0


@cached(ttl=86400)
async def retrieve_laf_locations() -> list[str]:
    laf_locations = await laf_locations_collection.distinct("location")
    return laf_locations


async def add_laf_location(laf_location: str) -> bool:
    laf_location_added = await laf_locations_collection.insert_one(
        {"location": laf_location}
    )
    new_laf_location = await laf_locations_collection.find_one(
        {"_id": laf_location_added.inserted_id}
    )
    return new_laf_location is not None


async def delete_laf_location(laf_location: str) -> bool:
    laf_location_deleted = await laf_locations_collection.delete_one(
        {"location": laf_location}
    )
    return laf_location_deleted.deleted_count > 0
