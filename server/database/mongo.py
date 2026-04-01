import logging
import sys

from fastapi import FastAPI, Request
from pymongo import AsyncMongoClient

from server.config import settings

logger = logging.getLogger(__name__)


async def mongo_setup(app: FastAPI) -> None:
    logger.info("Connecting to MongoDB...")
    try:
        client = AsyncMongoClient(settings.MONGO_DETAILS)
        database = client.apo_main

        # Verify connection with ping
        await client.admin.command("ping")
        logger.info("MongoDB Connection Successful")

        app.state.mongo_client = client
        app.state.mongo_database = database
        logger.info("Successfully connected to MongoDB and client is ready.")
    except Exception as e:
        logger.exception("Failed to connect to MongoDB: %s", e)
        sys.exit(1)


async def mongo_shutdown(app: FastAPI) -> None:
    if hasattr(app.state, "mongo_client") and app.state.mongo_client:
        logger.info("Closing MongoDB connection...")
        await app.state.mongo_client.close()
        logger.info("MongoDB connection closed.")


def get_database(request: Request):
    return request.app.state.mongo_database
