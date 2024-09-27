from bson.objectid import ObjectId

from server.database import database

loanertech_collection = database.get_collection("loanertech_collection")


def loanertech_helper(loanertech) -> dict:
    return {
        "id": str(loanertech["_id"]),
        "in_office": loanertech["in_office"],
        "description": loanertech["description"],
        "phone": loanertech["phone"],
        "email": loanertech["email"],
    }


# Retrieve all students present in the database
async def retrieve_loanertechs():
    loanertechs = []
    async for loanertech in loanertech_collection.find():
        loanertechs.append(loanertech_helper(loanertech))
    return loanertechs


# Add a new student into to the database
async def add_loanertech(loanertech_data: dict) -> dict:
    loanertech = await loanertech_collection.insert_one(loanertech_data)
    new_loanertech = await loanertech_collection.find_one(
        {"_id": loanertech.inserted_id}
    )
    return loanertech_helper(new_loanertech)


# Retrieve a student with a matching ID
async def retrieve_loanertech(id: str):
    student = await loanertech_collection.find_one({"_id": ObjectId(id)})
    if student:
        return loanertech_helper(student)


# Update a student with a matching ID
async def update_loanertech(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    student = await loanertech_collection.find_one({"_id": ObjectId(id)})
    if student:
        updated_student = await loanertech_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_student:
            return True
        return False


# Delete a student from the database
async def delete_loanertech(id: str):
    student = await loanertech_collection.find_one({"_id": ObjectId(id)})
    if student:
        await loanertech_collection.delete_one({"_id": ObjectId(id)})
        return True
