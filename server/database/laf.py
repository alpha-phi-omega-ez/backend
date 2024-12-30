import re
from asyncio import gather
from datetime import datetime, timedelta
from typing import List

from server.database import database
from server.helpers.db import async_dict_itr, datetime_time_delta

laf_items_collection = database.get_collection("laf_items_collection")
lost_reports_collection = database.get_collection("lost_reports_collection")
laf_id_collection = database.get_collection("laf_id_collection")
laf_types_collection = database.get_collection("laf_types")
laf_locations_collection = database.get_collection("laf_locations")
laf_matching_collection = database.get_collection("laf_matching")


laf_type_cache = {"datetime": datetime(1970, 1, 1), "data": []}
laf_locations_cache = {"datetime": datetime(1970, 1, 1), "data": []}


async def laf_db_setup() -> None:
    await laf_items_collection.create_index("date")
    await lost_reports_collection.create_index("date")
    await laf_items_collection.create_index([("description", "text")])
    await lost_reports_collection.create_index([("description", "text")])


# Helper functions to convert MongoDB documents to Python dictionaries
async def laf_helper(laf) -> dict:
    date = laf["date"]
    return {
        "id": laf["_id"],
        "type": laf["type"],
        "location": laf["location"],
        "date": f"{date[5:7]}/{date[8:]}/{date[:4]}",
        "description": laf["description"],
    }


async def laf_archived_helper(laf) -> dict:
    returned_date = laf["returned"]
    laf_data = await laf_helper(laf)
    laf_data["found"] = laf["found"]
    laf_data["archived"] = laf["archived"]
    laf_data["name"] = laf["name"]
    laf_data["email"] = laf["email"]
    laf_data["returned"] = (
        f"{returned_date[5:7]}/{returned_date[8:]}/{returned_date[:4]}",
    )
    return laf_data


async def lost_report_helper(lost_report) -> dict:
    date = lost_report["date"]
    return {
        "id": str(lost_report["_id"]),
        "name": lost_report["name"],
        "email": lost_report["email"],
        "type": lost_report["type"],
        "location": lost_report["location"],
        "date": f"{date[5:7]}/{date[8:]}/{date[:4]}",
        "description": lost_report["description"],
        "found": lost_report["found"],
        "archived": lost_report["archived"],
    }


async def get_next_sequence_value(sequence_name) -> int:
    result = await laf_id_collection.find_one_and_update(
        {"_id": sequence_name}, {"$inc": {"seq": 1}}, return_document=True
    )
    if result is None:
        # TODO: get the largest id in the collection and increment it by 1
        await laf_id_collection.insert_one({"_id": sequence_name, "seq": 1})
        result = {"seq": 1}
    return result["seq"]


# LAF Queries


# Add a new laf item into to the database
async def add_laf(laf_data: dict) -> dict:
    now = datetime.now()
    # Add the ID to the laf data
    laf_data["_id"] = await get_next_sequence_value("laf_id")
    laf_data["found"] = False
    laf_data["archived"] = False
    laf_data["created"] = now
    laf_data["updated"] = now
    laf_data["name"] = ""
    laf_data["email"] = ""
    laf_data["returned"] = now

    laf_item = await laf_items_collection.insert_one(laf_data)
    new_laf_item = await laf_items_collection.find_one({"_id": laf_item.inserted_id})
    return await laf_helper(new_laf_item)


async def update_laf(laf_id: str, laf_data: dict, now: datetime) -> dict | None:
    laf_item = await laf_items_collection.find_one({"_id": int(laf_id)})
    if laf_item is None:
        return None

    laf_data["updated"] = now

    updated_laf_item = await laf_items_collection.update_one(
        {"_id": int(laf_id)}, {"$set": laf_data}
    )
    if updated_laf_item.modified_count == 1:
        return await laf_helper(laf_data)

    return None


async def found_laf_item(laf_id: str, laf_found: dict) -> dict | None:
    now = datetime.now()

    laf_found["found"] = True
    laf_found["archived"] = True
    laf_found["returned"] = now

    return await update_laf(laf_id, laf_found, now)


async def update_laf_item(laf_id: str, laf_data: dict) -> dict | None:
    now = datetime.now()

    return await update_laf(laf_id, laf_data, now)


laf_item_query_mapping = {
    "dateFilter": lambda v, laf_query_data: (
        {"date": {"$lte": laf_query_data["date"]}}
        if v == "Before"
        else {"date": {"$gte": laf_query_data["date"]}}
    ),
    "location": lambda v, _: {"location": {"$in": v}},
    "type": lambda v, _: {"type": v},
    "description": lambda v, _: {
        "description": {"$regex": re.escape(v), "$options": "i"}
    },
}


# Retrieve all relevant laf items from the database
async def retrieve_laf_items(laf_query_data: dict, archived: bool = False) -> list:
    query = {"archived": archived}
    async for k, v in async_dict_itr(laf_query_data):
        if v is not None and k in laf_item_query_mapping:
            query.update(laf_item_query_mapping[k](v, laf_query_data))

    laf_items = []
    # Use .skip before limit for pagination
    async for laf_item in laf_items_collection.find(query).sort("date", -1).limit(30):
        if archived:
            laf_items.append(await laf_archived_helper(laf_item))
        else:
            laf_items.append(await laf_helper(laf_item))
    return laf_items


async def water_bottle_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, wb)
    return {
        "type": "Water Bottle",
        "date": {"$lte": cutoff_date},
    }


async def apparel_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, c)
    return {
        "type": "Apparel",
        "date": {"$lte": cutoff_date},
    }


async def umbrella_expiration_query(wb: int, c: int, u: int, now: datetime) -> dict:
    cutoff_date = await datetime_time_delta(now, u)
    return {
        "type": "Umbrella",
        "date": {"$lte": cutoff_date},
    }


type_expiration_mapping = {
    "Water Bottle": water_bottle_expiration_query,
    "Apparel": apparel_expiration_query,
    "Umbrella": umbrella_expiration_query,
}


async def fetch_expired_laf_items(expired_query: dict) -> List[dict]:
    expired_laf_items = []
    async for laf_item in laf_items_collection.find(expired_query).sort("date", -1):
        expired_laf_items.append(await laf_helper(laf_item))

    return expired_laf_items


async def fetch_potentially_expired_laf_items(
    potentially_expired_query: dict,
) -> List[dict]:
    potentially_expired_laf_items = []
    async for laf_item in laf_items_collection.find(potentially_expired_query).sort(
        "date", -1
    ):
        potentially_expired_laf_items.append(await laf_helper(laf_item))

    return potentially_expired_laf_items


async def retrieve_expired_laf(
    water_bottle_expiration: int,
    clothing_expiration: int,
    umbrella_expiration: int,
    inexpensive_expiration: int,
    expensive_expiration: int,
    type: str,
) -> dict[str, list]:
    now = datetime.now()

    if type == "All":

        wb, a, u, expensive_cutoff_date, inexpensive_cutoff_date = await gather(
            water_bottle_expiration_query(
                water_bottle_expiration,
                clothing_expiration,
                umbrella_expiration,
                now,
            ),
            apparel_expiration_query(
                water_bottle_expiration,
                clothing_expiration,
                umbrella_expiration,
                now,
            ),
            umbrella_expiration_query(
                water_bottle_expiration,
                clothing_expiration,
                umbrella_expiration,
                now,
            ),
            datetime_time_delta(now, expensive_expiration),
            datetime_time_delta(now, inexpensive_expiration),
        )

        expired_query = {
            "archived": False,
            "$or": [
                wb,
                a,
                u,
                {
                    "type": {"$nin": list(type_expiration_mapping.keys())},
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
                water_bottle_expiration, clothing_expiration, umbrella_expiration, now
            )
        )

        laf_items = []
        async for laf_item in laf_items_collection.find(query).sort("date", -1):
            laf_items.append(await laf_helper(laf_item))

        return {
            "expired": laf_items,
            "potential": [],
        }

    expensive_cutoff_date, inexpensive_cutoff_date = await gather(
        datetime_time_delta(now, expensive_expiration),
        datetime_time_delta(now, inexpensive_expiration),
    )

    expired_query = {
        "archived": False,
        "date": {"$lte": expensive_cutoff_date},
        "type": type,
    }
    potentially_expired_query = {
        "archived": False,
        "date": {"$lte": inexpensive_cutoff_date, "$gt": expensive_cutoff_date},
        "type": type,
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
async def add_lost_report(lost_report_data: dict, auth: bool) -> dict:
    now = datetime.now()
    lost_report_data["found"] = False
    lost_report_data["archived"] = False
    lost_report_data["created"] = now
    lost_report_data["updated"] = now
    lost_report_data["viewed"] = auth

    lost_report = await lost_reports_collection.insert_one(lost_report_data)
    new_lost_report = await lost_reports_collection.find_one(
        {"_id": lost_report.inserted_id}
    )
    return await lost_report_helper(new_lost_report)


async def update_lost_report(
    lost_report_id: str, lost_report_data: dict, now: datetime
) -> dict | None:
    lost_report = await lost_reports_collection.find_one({"_id": lost_report_id})
    if lost_report is None:
        return None

    lost_report_data["updated"] = now

    updated_lost_report = await lost_reports_collection.update_one(
        {"_id": lost_report_id}, {"$set": lost_report_data}
    )
    if updated_lost_report.modified_count == 1:
        return await lost_report_helper(lost_report_data)

    return None


async def found_lost_report(lost_report_id: str) -> dict | None:
    now = datetime.now()

    lost_report_found = {
        "found": True,
        "archived": True,
        "returned": now,
    }

    return await update_lost_report(lost_report_id, lost_report_found, now)


async def update_lost_report_item(
    lost_report_id: str, lost_report_data: dict
) -> dict | None:
    now = datetime.now()

    return await update_lost_report(lost_report_id, lost_report_data, now)


lost_report_query_mapping = {
    "dateFilter": lambda v, lost_report_query_data: (
        {"date": {"$lte": lost_report_query_data["date"]}}
        if v == "Before"
        else {"date": {"$gte": lost_report_query_data["date"]}}
    ),
    "description": lambda v, _: {
        "description": {"$regex": re.escape(v), "$options": "i"}
    },
    "location": lambda v, _: {"location": {"$in": v}},
    "type": lambda v, _: {"type": v},
    "name": lambda v, _: {"name": {"$regex": re.escape(v), "$options": "i"}},
    "email": lambda v, _: {"email": {"$regex": re.escape(v), "$options": "i"}},
}


# Retrieve all relevant lost reports from the database
async def retrieve_lost_reports(
    lost_report_query_data: dict, archived: bool = False
) -> list:
    query = {"archived": archived}
    async for k, v in async_dict_itr(lost_report_query_data):
        if v is not None and k in lost_report_query_mapping:
            query.update(lost_report_query_mapping[k](v, lost_report_query_data))

    lost_reports = []
    # Use .skip before limit for pagination
    async for laf_item in (
        lost_reports_collection.find(query).sort("date", -1).limit(30)
    ):
        lost_reports.append(await lost_report_helper(laf_item))
    return lost_reports


async def retrieve_laf_types() -> List[str]:
    return [
        "Apparel",
        "Books",
        "Electronics",
        "Miscellaneous",
        "Water Bottle",
        "Umbrella",
        "Jewelery",
    ]
    now = datetime.now()
    if laf_type_cache["datetime"] > now - timedelta(hours=24):
        return laf_type_cache["data"]

    laf_types = []
    async for laf_type in laf_types_collection.find():
        laf_types.append(laf_type["type"])

    laf_type_cache["datetime"] = now
    laf_type_cache["data"] = laf_types
    return laf_types


async def add_laf_type(laf_type: str) -> bool:
    laf_type_added = await laf_types_collection.insert_one({"type": laf_type})
    new_laf_type = await laf_items_collection.find_one(
        {"_id": laf_type_added.inserted_id}
    )
    return new_laf_type is not None


async def delete_laf_type(laf_type: str) -> bool:
    laf_type_deleted = await laf_types_collection.delete_one({"type": laf_type})
    return laf_type_deleted.deleted_count > 0


async def retrieve_laf_locations() -> List[str]:
    return ["Union", "Mueller", "Folsom Library", "VCC"]
    now = datetime.now()
    if laf_locations_cache["datetime"] > now - timedelta(hours=24):
        return laf_locations_cache["data"]

    laf_locations = []
    async for laf_tocation in laf_locations_collection.find():
        laf_locations.append(laf_tocation["location"])

    laf_locations_cache["datetime"] = now
    laf_locations_cache["data"] = laf_locations
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
