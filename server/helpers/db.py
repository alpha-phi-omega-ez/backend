from datetime import datetime, timedelta


async def async_dict_itr(dict_data: dict):
    for k, v in dict_data.items():
        yield k, v


async def datetime_time_delta(now: datetime, days: int) -> str:
    return (now - timedelta(days=days)).strftime("%Y-%m-%d")
