from datetime import datetime, timedelta
from typing import Annotated, Tuple
from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    Security,
)
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from httpx import ConnectError, ConnectTimeout
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from starlette import status

from server.config import settings
from server.database.valkey import (
    add_token_to_blacklist,
    generate_temporary_code,
    validate_code_and_get_user_email,
)
from server.helpers.auth import (
    auth_cookie_scheme,
    create_access_token,
    simple_auth_check,
)
from server.helpers.sanitize import sanitize_redirect_path
from server.models.auth import (
    AuthCheckResponse,
    LogoutResponse,
    MessageResponse,
    TokenRequest,
)

google_sso = GoogleSSO(
    settings.GOOGLE_CLIENT_ID,
    settings.GOOGLE_CLIENT_SECRET,
    settings.BACKEND_URL + "/callback",
)

router = APIRouter()

_REDIRECT_HEADERS = {
    "Location": {
        "description": "Redirect URL",
        "schema": {"type": "string"},
    }
}

_SET_COOKIE_HEADER = {
    "Set-Cookie": {
        "description": "Sets httponly `authToken` session cookie",
        "schema": {"type": "string"},
    }
}


def _frontend_login_callback_url(code: str, redirect: str) -> str:
    safe_redirect = sanitize_redirect_path(redirect)
    query = urlencode({"code": code, "redirect": safe_redirect})
    return f"{settings.FRONTEND_URL}/login/callback?{query}"


@router.get(
    "/login",
    response_description="Initiate login with Google url",
    response_class=RedirectResponse,
    responses={
        302: {
            "description": "Redirect to Google OAuth",
            "headers": _REDIRECT_HEADERS,
        }
    },
    status_code=status.HTTP_302_FOUND,
)
async def google_login(
    request: Request,
    redirect: str = Query(
        "/",
        description="Frontend path to return to after successful login",
    ),
) -> RedirectResponse:
    safe_redirect = sanitize_redirect_path(redirect)

    if settings.TESTING:
        print("TEST LOGIN, this should not be used in production!")
        code = await generate_temporary_code(request, "test@apoez.org")
        return RedirectResponse(url=_frontend_login_callback_url(code, safe_redirect))

    async with google_sso:
        login_stuff = await google_sso.get_login_redirect(
            params={"redirect": safe_redirect}
        )
    return login_stuff


@router.get(
    "/callback",
    response_description="Google callback",
    response_class=RedirectResponse,
    responses={
        302: {
            "description": "Redirect to frontend with temporary login code",
            "headers": _REDIRECT_HEADERS,
        },
        400: {
            "description": "Redirect to frontend login error page",
            "headers": _REDIRECT_HEADERS,
        },
    },
    status_code=status.HTTP_302_FOUND,
)
async def google_callback(
    request: Request,
    redirect: str = Query(
        "/",
        description="Frontend path to return to after successful login",
    ),
) -> RedirectResponse:
    try:
        async with google_sso:
            user = await google_sso.verify_and_process(request)
    except (ConnectTimeout, InvalidGrantError, ConnectError):
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login/error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if user is None or user.email is None:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login/error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    code = await generate_temporary_code(request, user.email)
    return RedirectResponse(url=_frontend_login_callback_url(code, redirect))


@router.post(
    "/token",
    response_description="Exchange code for token",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "Login successful; authToken cookie is set",
            "model": MessageResponse,
            "headers": _SET_COOKIE_HEADER,
        }
    },
)
async def exchange_code_for_token(
    request: Request,
    response: Response,
    token: TokenRequest = Body(...),
) -> MessageResponse:
    user_email = await validate_code_and_get_user_email(request, token.code)
    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid code")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={
            "email": user_email,
            "datetime": datetime.now().strftime("%A %B %d %Y %H %M %S %f %j"),
        },
        expires_delta=access_token_expires,
    )

    secure = not settings.TESTING  # Use HTTPS in production
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key="authToken",
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=secure,  # Use HTTPS in production
        samesite="strict",  # Prevent cross-site requests
        max_age=max_age,  # Expire cookie after n seconds
    )
    return MessageResponse(message="Login successful")


@router.post(
    "/logout",
    response_description="Logout",
    response_model=LogoutResponse,
)
async def logout(
    request: Request,
    response: Response,
    token: Annotated[str | None, Security(auth_cookie_scheme)] = None,
) -> LogoutResponse:
    # Add the token to a blacklist or invalidation list
    auth_token = token if token is not None else request.cookies.get("authToken")
    if auth_token:
        # Assuming you have a blacklist set or database table
        # Here we use a simple set for demonstration purposes
        await add_token_to_blacklist(request, auth_token)
        response.delete_cookie("authToken")
        return LogoutResponse(message="Logged out", success=True)
    return LogoutResponse(message="No token found to log out", success=False)


@router.get(
    "/auth/check",
    response_description="Check if user is authenticated",
    response_model=AuthCheckResponse,
)
async def check_auth(
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check),
) -> AuthCheckResponse:
    return AuthCheckResponse(authenticated=auth[0])
