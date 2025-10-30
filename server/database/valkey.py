import sys
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from glide import GlideClient, GlideClientConfiguration, NodeAddress

from server.config import settings


async def valkey_setup(app: FastAPI) -> None:
    print("Connecting to Valkey...")
    try:
        # Configure and create the Valkey client instance
        addresses = [NodeAddress(settings.VALKEY_ADDRESS, 6379)]
        config = GlideClientConfiguration(addresses=addresses)
        client = await GlideClient.create(config)

        # Store the client instance in the application's state
        app.state.valkey_client = client
        print("Successfully connected to Valkey and client is ready.")
    except Exception as e:
        print(f"Failed to connect to Valkey: {e}")
        sys.exit(1)


async def generate_temporary_code(
    request: Request, user_email: str, expire_seconds: int = 8
) -> str:
    # Access the shared client from the application state
    client: GlideClient = request.app.state.valkey_client

    if not client:
        raise HTTPException(status_code=503, detail="Valkey service is unavailable.")

    code = str(uuid4())

    try:
        response = await client.set(code, user_email)
        if response == "OK":
            # Apply expiry after setting the key
            await client.expire(code, expire_seconds)
            return code
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set key. Valkey response: {response}",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


async def validate_code_and_get_user_email(request: Request, code: str) -> str | None:
    client: GlideClient = request.app.state.valkey_client

    if not client:
        raise HTTPException(status_code=503, detail="Valkey service is unavailable.")

    value = await client.get(code)
    if value is None:
        return None

    return value.decode("utf-8")


async def add_token_to_blacklist(
    request: Request,
    token: str,
) -> None:
    client: GlideClient = request.app.state.valkey_client

    if not client:
        raise HTTPException(status_code=503, detail="Valkey service is unavailable.")

    try:
        key = f"blacklist:{token}"
        response = await client.set(key, "1")
        if response != "OK":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add token to blacklist. Valkey response: {response}",
            )
        # Set blacklist TTL in seconds
        await client.expire(key, int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


async def is_token_blacklisted(request: Request, token: str) -> bool:
    client: GlideClient = request.app.state.valkey_client

    if not client:
        raise HTTPException(status_code=503, detail="Valkey service is unavailable.")

    value = await client.get(f"blacklist:{token}")
    return value is not None
