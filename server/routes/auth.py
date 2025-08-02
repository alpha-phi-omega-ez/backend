from datetime import datetime, timedelta
from typing import Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi_sso.sso.google import GoogleSSO
from starlette import status

from server.config import settings
from server.database.valkey import (
    add_token_to_blacklist,
    generate_temporary_code,
    validate_code_and_get_user_email,
)
from server.helpers.auth import (
    create_access_token,
    simple_auth_check,
)
from server.models.auth import TokenRequest

google_sso = GoogleSSO(
    settings.GOOGLE_CLIENT_ID,
    settings.GOOGLE_CLIENT_SECRET,
    settings.BACKEND_URL + "/callback",
)

router = APIRouter()


@router.get("/login", response_description="Initiate login with Google url")
async def google_login(request: Request) -> RedirectResponse:
    redirect_url = request.query_params.get("redirect", "/")

    if settings.TESTING:
        print("TEST LOGIN, this should not be used in production!")
        code = await generate_temporary_code(request, "test@apoez.org")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login/callback?code={code}&redirect={redirect_url}"
        )

    async with google_sso:
        login_stuff = await google_sso.get_login_redirect(
            params={"redirect": redirect_url}
        )
    return login_stuff


@router.get("/callback", response_description="Google callback")
async def google_callback(request: Request) -> RedirectResponse:
    redirect_url = request.query_params.get("redirect", "/")

    async with google_sso:
        user = await google_sso.verify_and_process(request)

    if user is None or user.email is None:
        return RedirectResponse(
            url=settings.FRONTEND_URL + "login/error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    code = await generate_temporary_code(request, user.email)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/login/callback?code={code}&redirect={redirect_url}"
    )


@router.post("/token", response_description="Exchange code for token")
async def exchange_code_for_token(
    request: Request, token: TokenRequest = Body(...)
) -> JSONResponse:
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

    secure = not settings.TESTING  # READD FOR PRODUCTION
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="authToken",
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=secure,  # Use HTTPS in production
        samesite="strict",  # Prevent cross-site requests
        max_age=max_age,  # Expire cookie after n seconds
    )
    return response


@router.post("/logout", response_description="Logout")
async def logout(request: Request, response: Response) -> JSONResponse:
    # Add the token to a blacklist or invalidation list
    token = request.cookies.get("authToken")
    if token:
        # Assuming you have a blacklist set or database table
        # Here we use a simple set for demonstration purposes
        await add_token_to_blacklist(request, token)
        response.delete_cookie("authToken")
        return JSONResponse(content={"message": "Logged out", "success": True})
    return JSONResponse(
        content={"message": "No token found to log out", "success": False}
    )


@router.get("/auth/check", response_description="Check if user is authenticated")
async def check_auth(
    auth: Tuple[bool, str, dict | None] = Depends(simple_auth_check),
) -> JSONResponse:
    return JSONResponse({"authenticated": auth[0]})
