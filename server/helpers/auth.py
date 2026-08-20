from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyCookie

from server.config import settings
from server.database.valkey import is_token_blacklisted

temp_codes = {}

# Declared so OpenAPI/Swagger document cookie-based auth (Authorize button).
auth_cookie_scheme = APIKeyCookie(name="authToken", auto_error=False)


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


async def simple_auth_check(
    request: Request,
    token: Annotated[str | None, Security(auth_cookie_scheme)] = None,
) -> tuple[bool, str, dict | None]:
    auth_token = token if token is not None else request.cookies.get("authToken")

    if auth_token:
        try:
            payload = await validate_token(request, auth_token)
            return True, "", payload
        except jwt.ExpiredSignatureError:
            return False, "Token expired", None
        except jwt.InvalidTokenError:
            return False, "Invalid token", None
        except BlacklistedTokenException:
            return False, "User logged out", None
    return False, "No token found", None


async def required_auth(
    request: Request,
    token: Annotated[str | None, Security(auth_cookie_scheme)] = None,
) -> dict:
    authenticated, message, payload = await simple_auth_check(request, token)

    if authenticated and payload:
        return payload

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
