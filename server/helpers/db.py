async def async_dict_itr(dict_data: dict):
    for k, v in dict_data.items():
        yield k, v
