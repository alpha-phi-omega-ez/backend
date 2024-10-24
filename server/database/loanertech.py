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
    }


async def get_next_sequence_value(sequence_name) -> int:
    # TODO: create initialize db script and add this
    # await loanertech_id_collection.insert_one({"_id": "loanertechid", "seq": 1})
    result = await loanertech_id_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        return_document=True
    )
    return result["seq"]


# Retrieve all students present in the database
async def retrieve_loanertechs():
    loanertechs = []
    async for loanertech in loanertech_collection.find():
        loanertechs.append(loanertech_helper(loanertech))
    return loanertechs


# Add a new student into to the database
async def add_loanertech(loanertech_data: dict) -> dict:
    # Add the ID to the loanertech data
    loanertech_data["_id"] = await get_next_sequence_value("loanertechid")
    loanertech_data["in_office"] = True
    loanertech_data["phone"] = ""
    loanertech_data["email"] = ""

    loanertech = await loanertech_collection.insert_one(loanertech_data)
    new_loanertech = await loanertech_collection.find_one(
        {"_id": loanertech.inserted_id}
    )
    return loanertech_helper(new_loanertech)


# Retrieve a student with a matching ID
async def retrieve_loanertech(id: int):
    student = await loanertech_collection.find_one({"_id": id})
    if student:
        return loanertech_helper(student)
    return None


# Update a student with a matching ID
async def update_loanertech(id: int, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    student = await loanertech_collection.find_one({"_id": id})
    if student:
        updated_student = await loanertech_collection.update_one(
            {"_id": id}, {"$set": data}
        )
        if updated_student:
            return True
    return False


# Delete a student from the database
async def delete_loanertech(id: int):
    student = await loanertech_collection.find_one({"_id": id})
    if student:
        await loanertech_collection.delete_one({"_id": id})
        return True
    return False
