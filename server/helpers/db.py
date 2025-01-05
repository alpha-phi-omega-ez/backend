from datetime import datetime, timedelta


async def async_dict_itr(dict_data: dict):
    for k, v in dict_data.items():
        yield k, v


async def datetime_time_delta(now: datetime, days: int) -> str:
    return (now - timedelta(days=days)).strftime("%Y-%m-%d")


async def get_next_sequence_value(sequence_name, sequence_id_collection) -> int:
    result = await sequence_id_collection.find_one_and_update(
        {"_id": sequence_name}, {"$inc": {"seq": 1}}, return_document=True
    )
    if result is None:
        await sequence_id_collection.insert_one({"_id": sequence_name, "seq": 1})
        result = {"seq": 1}
    return result["seq"]
