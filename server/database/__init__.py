import motor.motor_asyncio

from server.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DETAILS)

database = client.apo_main
