import motor.motor_asyncio

from server.config import get_settings  # Import settings from the appropriate module

settings = get_settings()

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DETAILS)

database = client.apo_main

import server.database.loanertech
