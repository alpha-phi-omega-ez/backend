from fastapi import HTTPException, status

from server.database import database
from server.helpers.db import get_next_sequence_value

sequence_id_collection = database.get_collection("sequence_id")
loanertech_collection = database.get_collection("loanertech_collection")


def loanertech_helper(loanertech: dict) -> dict:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
        "phone": loanertech["phone"],
        "email": loanertech["email"],
        "name": loanertech["name"],
    }


def loanertech_helper_unprotected(loanertech: dict) -> dict:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
    }


# Retrieve all loaner tech items present in the database with data for unauthenticated users
async def retrieve_loanertechs_unauthenticated() -> list[dict]:
    loanertechs = []
    async for loanertech in loanertech_collection.find().sort("_id"):
        loanertechs.append(loanertech_helper_unprotected(loanertech))
    return loanertechs


# Retrieve all loaner tech items present in the database with data for authenticated users
async def retrieve_loanertechs() -> list[dict]:
    loanertechs = []
    async for loanertech in loanertech_collection.find().sort("_id"):
        loanertechs.append(loanertech_helper(loanertech))
    return loanertechs


# Add a new loanertech item into to the database
async def add_loanertech(loanertech_data: dict) -> dict:
    # Add the ID to the loanertech data
    loanertech_data["_id"] = await get_next_sequence_value(
        "loanertech_id", sequence_id_collection
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
async def retrieve_loanertech(id: int) -> dict | None:
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        return loanertech_helper(loanertech)
    return None


# Update a loanertech item with a matching ID
async def update_loanertech(id: int, data: dict) -> bool:
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        updated_loanertech = await loanertech_collection.update_one(
            {"_id": id}, {"$set": data}
        )
        if updated_loanertech:
            return True
    return False


# Delete a student from the database
async def delete_loanertech(id: int) -> bool:
    student = await loanertech_collection.find_one({"_id": id})
    if student:
        await loanertech_collection.delete_one({"_id": id})
        return True
    return False
