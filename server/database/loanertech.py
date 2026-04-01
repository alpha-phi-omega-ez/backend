from fastapi import HTTPException, Request, status

from server.helpers.db import get_next_sequence_value
from server.helpers.sanitize import reject_mongo_operators
from server.models.loanertech import LoanerTechItem, LoanerTechItemUnauthorized


def loanertech_helper(loanertech: dict) -> LoanerTechItem:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
        "phone": loanertech["phone"],
        "email": loanertech["email"],
        "name": loanertech["name"],
    }


def loanertech_helper_unprotected(loanertech: dict) -> LoanerTechItemUnauthorized:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
    }


# Retrieve all loaner tech items present in the database with data
# for unauthenticated users
async def retrieve_loanertechs_unauthenticated(
    request: Request,
) -> list[LoanerTechItemUnauthorized]:
    loanertech_collection = request.app.state.mongo_database.get_collection(
        "loanertech_collection"
    )
    loanertechs = []
    async for loanertech in loanertech_collection.find().sort("_id"):
        loanertechs.append(loanertech_helper_unprotected(loanertech))
    return loanertechs


# Retrieve all loaner tech items present in the database with
# data for authenticated users
async def retrieve_loanertechs(request: Request) -> list[LoanerTechItem]:
    loanertech_collection = request.app.state.mongo_database.get_collection(
        "loanertech_collection"
    )
    loanertechs = []
    async for loanertech in loanertech_collection.find().sort("_id"):
        loanertechs.append(loanertech_helper(loanertech))
    return loanertechs


# Add a new loanertech item into to the database
async def add_loanertech(request: Request, loanertech_data: dict) -> LoanerTechItem:
    reject_mongo_operators(loanertech_data)
    database = request.app.state.mongo_database
    sequence_id_collection = database.get_collection("sequence_id")
    loanertech_collection = database.get_collection("loanertech_collection")

    loanertech_data["_id"] = await get_next_sequence_value(
        "loanertech_id",
        sequence_id_collection,
        loanertech_collection,
    )
    loanertech_data["in_office"] = True
    loanertech_data["phone"] = ""
    loanertech_data["email"] = ""
    loanertech_data["name"] = ""

    loanertech = await loanertech_collection.insert_one(loanertech_data)
    new_loanertech = await loanertech_collection.find_one(
        {"_id": loanertech.inserted_id}
    )
    if new_loanertech:
        return loanertech_helper(new_loanertech)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create Loanertech",
    )


# Retrieve a loanertech item with a matching ID
async def retrieve_loanertech(request: Request, id: int) -> LoanerTechItem | None:
    loanertech_collection = request.app.state.mongo_database.get_collection(
        "loanertech_collection"
    )
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        return loanertech_helper(loanertech)
    return None


# Update a loanertech item with a matching ID
async def update_loanertech(request: Request, id: int, data: dict) -> bool:
    if len(data) < 1:
        return False
    reject_mongo_operators(data)
    loanertech_collection = request.app.state.mongo_database.get_collection(
        "loanertech_collection"
    )
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        updated_loanertech = await loanertech_collection.update_one(
            {"_id": id}, {"$set": data}
        )
        if updated_loanertech:
            return True
    return False


# Delete a loanertech item from the database
async def delete_loanertech(request: Request, id: int) -> bool:
    loanertech_collection = request.app.state.mongo_database.get_collection(
        "loanertech_collection"
    )
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        await loanertech_collection.delete_one({"_id": id})
        return True
    return False
