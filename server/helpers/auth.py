from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, Request, status

from server.config import settings

temp_codes = {}
blacklisted_tokens = set()


class BlacklistedTokenException(Exception):
    pass


async def generate_temporary_code(user_email: str) -> str:
    # Generate a unique temporary code
    code = str(uuid4())
    expires_at = datetime.now() + timedelta(seconds=8)  # expires in 8 seconds
    temp_codes[code] = {"email": user_email, "expires_at": expires_at}
    return code


async def validate_code_and_get_user_email(code: str) -> str | None:
    token_data = temp_codes.get(code, {})
    if not token_data:
        return None

    user_email = token_data.get("email", None)
    expire = token_data.get("expires_at", None)

    if user_email and expire and expire > datetime.now():
        # If found, delete the code to prevent reuse
        del temp_codes[code]
        return user_email
    elif expire:
        # If the code has expired, delete it
        del temp_codes[code]

    return None


async def validate_token(token: str) -> dict:
    if token in blacklisted_tokens:
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


async def blacklist_token(token: str) -> None:
    blacklisted_tokens.add(token)


async def simple_auth_check(request: Request) -> tuple[bool, str, dict | None]:
    token = request.cookies.get("authToken")

    if token:
        try:
            payload = await validate_token(token)
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
