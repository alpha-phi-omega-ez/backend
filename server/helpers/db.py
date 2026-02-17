from datetime import datetime, timedelta


async def async_dict_itr(dict_data: dict):
    for k, v in dict_data.items():
        yield k, v


async def datetime_time_delta(now: datetime, days: int) -> str:
    return (now - timedelta(days=days)).strftime("%Y-%m-%d")


async def get_next_sequence_value(
    sequence_name,
    sequence_id_collection,
    check_collection=None,
) -> int:
    """
    Get the next value for the given sequence. Ensures the returned ID does not already
    exist in that collection, and corrects the sequence if it was out of sync
    (e.g. due to manual inserts).
    """
    while True:
        result = await sequence_id_collection.find_one_and_update(
            {"_id": sequence_name}, {"$inc": {"seq": 1}}, return_document=True
        )
        if result is None:
            await sequence_id_collection.insert_one({"_id": sequence_name, "seq": 1})
            result = {"seq": 1}
        value = result["seq"]

        existing = await check_collection.find_one({"_id": value})
        if existing is None:
            return value  # Unique ID found

        # Duplicate: sequence is behind. Correct it to max(_id) + 1 so we
        # don't hand out this value again and future calls are safe.
        max_doc = await check_collection.find_one(
            sort=[("_id", -1)], projection={"_id": 1}
        )
        max_id = max_doc["_id"] if max_doc else 0
        await sequence_id_collection.update_one(
            {"_id": sequence_name},
            {"$max": {"seq": max_id}},
        )
        # Loop to get the next value (sequence is now corrected)
