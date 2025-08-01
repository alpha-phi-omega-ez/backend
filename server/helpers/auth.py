from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request, status

from server.config import settings
from server.database.valkey import is_token_blacklisted

temp_codes = {}


class BlacklistedTokenException(Exception):
    pass


async def validate_token(request: Request, token: str) -> dict:
    if await is_token_blacklisted(request, token):
        raise BlacklistedTokenException

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    return payload


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def simple_auth_check(request: Request) -> tuple[bool, str, dict | None]:
    token = request.cookies.get("authToken")

    if token:
        try:
            payload = await validate_token(request, token)
            return True, "", payload
        except jwt.ExpiredSignatureError:
            return False, "Token expired", None
        except jwt.InvalidTokenError:
            return False, "Invalid token", None
        except BlacklistedTokenException:
            return False, "User logged out", None
    return False, "No token found", None


async def required_auth(request: Request) -> dict:
    authenticated, message, payload = await simple_auth_check(request)

    if authenticated and payload:
        return payload

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
