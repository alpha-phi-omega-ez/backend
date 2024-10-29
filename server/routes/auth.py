from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi_sso.sso.google import GoogleSSO
from jwt import encode as jwt_encode
from starlette import status
from starlette.requests import Request

from server.config import get_settings
from server.models.auth import TokenRequest

settings = get_settings()

google_sso = GoogleSSO(
    settings.GOOGLE_CLIENT_ID,
    settings.GOOGLE_CLIENT_SECRET,
    settings.BACKEND_URL + "/callback",
)

router = APIRouter()

temp_codes = {}


async def generate_temporary_code(user_email: str) -> str:
    # Generate a unique temporary code
    code = str(uuid4())
    expires_at = datetime.now() + timedelta(seconds=5)  # expires in 5 seconds
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


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt_encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.get("/login", response_description="Initiate login with Google url")
async def google_login() -> RedirectResponse:
    with google_sso:
        login_stuff = await google_sso.get_login_redirect()
    return login_stuff


@router.get("/callback", response_description="Google callback")
async def google_callback(request: Request, response: Response):
    with google_sso:
        user = await google_sso.verify_and_process(request)

    if user is None or user.email is None:
        return RedirectResponse(
            url=settings.FRONTEND_URL + "login/error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    code = await generate_temporary_code(user.email)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login/callback?code={code}")


@router.post("/token")
async def exchange_code_for_token(token: TokenRequest = Body(...)):
    user_email = await validate_code_and_get_user_email(token.code)
    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid code")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={
            "sub": user_email,
            "datetime": datetime.now().strftime("%A %B %d %Y %H %M %S %f %j"),
        },
        expires_delta=access_token_expires,
    )
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}
