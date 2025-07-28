from pymongo import AsyncMongoClient

from server.config import settings

client = AsyncMongoClient(settings.MONGO_DETAILS)

database = client.apo_main
