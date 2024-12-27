import motor.motor_asyncio

from server.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DETAILS)

database = client.apo_main

import server.database.backtest
import server.database.laf
import server.database.loanertech
from server.database.laf import laf_db_setup


async def db_setup():
    await laf_db_setup()
