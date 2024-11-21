from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi_sso.sso.google import GoogleSSO
from starlette import status
from starlette.requests import Request as StarletteRequest

from server.config import settings
from server.helpers.auth import (
    BlacklistedTokenException,
    blacklist_token,
    create_access_token,
    generate_temporary_code,
    validate_code_and_get_user_email,
    validate_token,
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
        print("TEST LOGIN")
        code = await generate_temporary_code("test@apoez.org")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login/callback?code={code}&redirect={redirect_url}"
        )

    with google_sso:
        login_stuff = await google_sso.get_login_redirect(
            params={"redirect": redirect_url}
        )
    return login_stuff


@router.get("/callback", response_description="Google callback")
async def google_callback(star_request: StarletteRequest, request: Request):
    redirect_url = request.query_params.get("redirect", "/")

    with google_sso:
        user = await google_sso.verify_and_process(star_request)

    if user is None or user.email is None:
        return RedirectResponse(
            url=settings.FRONTEND_URL + "login/error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    code = await generate_temporary_code(user.email)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/login/callback?code={code}&redirect={redirect_url}"
    )


@router.post("/token")
async def exchange_code_for_token(token: TokenRequest = Body(...)):
    user_email = await validate_code_and_get_user_email(token.code)
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

    secure = not settings.TESTING
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="authToken",
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=secure,  # Use HTTPS in production
        samesite="strict",  # Prevent cross-site requests
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return response


@router.post("/logout")
async def logout(request: Request, response: Response) -> JSONResponse:
    # Add the token to a blacklist or invalidation list
    token = request.cookies.get("authToken")
    if token:
        # Assuming you have a blacklist set or database table
        # Here we use a simple set for demonstration purposes
        await blacklist_token(token)
        response.delete_cookie("authToken")
        return JSONResponse(content={"message": "Logged out", "success": True})
    return JSONResponse(
        content={"message": "No token found to log out", "success": False}
    )


@router.get("/auth/check")
async def check_auth(request: Request):
    token = request.cookies.get("authToken")

    if token:
        try:
            await validate_token(token)  # Your JWT validation function
            return {"authenticated": True}
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            BlacklistedTokenException,
        ):
            return {"authenticated": False}

    return {"authenticated": False}
