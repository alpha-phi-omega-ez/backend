from server.database import database

loanertech_collection = database.get_collection("loanertech_collection")
loanertech_id_collection = database.get_collection("loanertech_id_collection")


def loanertech_helper(loanertech) -> dict:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
        "phone": loanertech["phone"],
        "email": loanertech["email"],
        "name": loanertech["name"],
    }


def loanertech_helper_unprotected(loanertech) -> dict:
    return {
        "id": loanertech["_id"],
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
    }


async def get_next_sequence_value(sequence_name) -> int:
    result = await loanertech_id_collection.find_one_and_update(
        {"_id": sequence_name}, {"$inc": {"seq": 1}}, return_document=True
    )
    if result is None:
        await loanertech_id_collection.insert_one({"_id": sequence_name, "seq": 1})
        result = {"seq": 1}
    return result["seq"]


# Retrieve all loaner tech items present in the database with data for unauthenticated users
async def retrieve_loanertechs_unauthenticated():
    loanertechs = []
    async for loanertech in loanertech_collection.find():
        loanertechs.append(loanertech_helper_unprotected(loanertech))
    return loanertechs


# Retrieve all loaner tech items present in the database with data for authenticated users
async def retrieve_loanertechs():
    loanertechs = []
    async for loanertech in loanertech_collection.find():
        loanertechs.append(loanertech_helper(loanertech))
    return loanertechs


# Add a new loanertech item into to the database
async def add_loanertech(loanertech_data: dict) -> dict:
    # Add the ID to the loanertech data
    loanertech_data["_id"] = await get_next_sequence_value("loanertechid")
    loanertech_data["in_office"] = True
    loanertech_data["phone"] = ""
    loanertech_data["email"] = ""
    loanertech_data["name"] = ""

    loanertech = await loanertech_collection.insert_one(loanertech_data)
    new_loanertech = await loanertech_collection.find_one(
        {"_id": loanertech.inserted_id}
    )
    return loanertech_helper(new_loanertech)


# Retrieve a loanertech item with a matching ID
async def retrieve_loanertech(id: int):
    loanertech = await loanertech_collection.find_one({"_id": id})
    if loanertech:
        return loanertech_helper(loanertech)
    return None


# Update a loanertech item with a matching ID
async def update_loanertech(id: int, data: dict):
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
async def delete_loanertech(id: int):
    student = await loanertech_collection.find_one({"_id": id})
    if student:
        await loanertech_collection.delete_one({"_id": id})
        return True
    return False
