"""Unit tests for server.helpers.auth."""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException, Request, status

from server.helpers.auth import (
    BlacklistedTokenException,
    create_access_token,
    required_auth,
    simple_auth_check,
    validate_token,
)


def _request_with_cookie(token: str | None) -> MagicMock:
    request = MagicMock(spec=Request)
    cookies: dict[str, str] = {}
    if token is not None:
        cookies["authToken"] = token
    request.cookies.get = MagicMock(
        side_effect=lambda key, default=None: cookies.get(key, default)
    )
    return request


def test_validate_token_blacklisted_raises() -> None:
    async def _run() -> None:
        request = _request_with_cookie("tok")
        with patch(
            "server.helpers.auth.is_token_blacklisted",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with pytest.raises(BlacklistedTokenException):
                await validate_token(request, "tok")

    asyncio.run(_run())


def test_validate_token_decodes_and_returns_payload() -> None:
    async def _run() -> None:
        request = _request_with_cookie("tok")
        expected = {"sub": "user1"}
        with (
            patch(
                "server.helpers.auth.is_token_blacklisted",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "server.helpers.auth.jwt.decode", return_value=expected
            ) as mock_decode,
        ):
            with patch("server.helpers.auth.settings") as mock_settings:
                mock_settings.SECRET_KEY = "secret"
                mock_settings.ALGORITHM = "HS256"
                result = await validate_token(request, "tok")
        assert result == expected
        mock_decode.assert_called_once_with("tok", "secret", algorithms=["HS256"])

    asyncio.run(_run())


def test_create_access_token_with_expires_delta() -> None:
    async def _run() -> str:
        fixed_now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        delta = timedelta(hours=2)
        with patch("server.helpers.auth.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.timedelta = timedelta
            mock_dt.timezone = timezone
            with patch("server.helpers.auth.settings") as mock_settings:
                mock_settings.SECRET_KEY = "x" * 32
                mock_settings.ALGORITHM = "HS256"
                return await create_access_token({"sub": "u1"}, expires_delta=delta)

    token = asyncio.run(_run())
    payload = jwt.decode(
        token,
        "x" * 32,
        algorithms=["HS256"],
        options={"verify_exp": False},
    )
    assert payload["sub"] == "u1"
    fixed_now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert payload["exp"] == int((fixed_now + timedelta(hours=2)).timestamp())


def test_create_access_token_default_expiry_about_15_minutes() -> None:
    async def _run() -> str:
        fixed_now = datetime(2025, 6, 1, 10, 30, 0, tzinfo=timezone.utc)
        with patch("server.helpers.auth.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.timedelta = timedelta
            mock_dt.timezone = timezone
            with patch("server.helpers.auth.settings") as mock_settings:
                mock_settings.SECRET_KEY = "x" * 32
                mock_settings.ALGORITHM = "HS256"
                return await create_access_token({"sub": "u2"})

    token = asyncio.run(_run())
    payload = jwt.decode(
        token,
        "x" * 32,
        algorithms=["HS256"],
        options={"verify_exp": False},
    )
    fixed_now = datetime(2025, 6, 1, 10, 30, 0, tzinfo=timezone.utc)
    expected_exp = int((fixed_now + timedelta(minutes=15)).timestamp())
    assert payload["exp"] == expected_exp


def test_simple_auth_check_no_cookie() -> None:
    async def _run() -> None:
        request = _request_with_cookie(None)
        ok, msg, payload = await simple_auth_check(request)
        assert ok is False
        assert msg == "No token found"
        assert payload is None

    asyncio.run(_run())


def test_simple_auth_check_success() -> None:
    async def _run() -> None:
        request = _request_with_cookie("good")
        with patch(
            "server.helpers.auth.validate_token",
            new_callable=AsyncMock,
            return_value={"sub": "x"},
        ):
            ok, msg, payload = await simple_auth_check(request)
        assert ok is True
        assert msg == ""
        assert payload == {"sub": "x"}

    asyncio.run(_run())


def test_simple_auth_check_expired_token() -> None:
    async def _run() -> None:
        request = _request_with_cookie("expired")
        with patch(
            "server.helpers.auth.validate_token",
            new_callable=AsyncMock,
            side_effect=jwt.ExpiredSignatureError(),
        ):
            ok, msg, payload = await simple_auth_check(request)
        assert ok is False
        assert msg == "Token expired"
        assert payload is None

    asyncio.run(_run())


def test_simple_auth_check_invalid_token() -> None:
    async def _run() -> None:
        request = _request_with_cookie("bad")
        with patch(
            "server.helpers.auth.validate_token",
            new_callable=AsyncMock,
            side_effect=jwt.InvalidTokenError(),
        ):
            ok, msg, payload = await simple_auth_check(request)
        assert ok is False
        assert msg == "Invalid token"
        assert payload is None

    asyncio.run(_run())


def test_simple_auth_check_blacklisted() -> None:
    async def _run() -> None:
        request = _request_with_cookie("bl")
        with patch(
            "server.helpers.auth.validate_token",
            new_callable=AsyncMock,
            side_effect=BlacklistedTokenException(),
        ):
            ok, msg, payload = await simple_auth_check(request)
        assert ok is False
        assert msg == "User logged out"
        assert payload is None

    asyncio.run(_run())


def test_required_auth_returns_payload() -> None:
    async def _run() -> None:
        request = _request_with_cookie("ok")
        with patch(
            "server.helpers.auth.simple_auth_check",
            new_callable=AsyncMock,
            return_value=(True, "", {"sub": "admin"}),
        ):
            result = await required_auth(request)
        assert result == {"sub": "admin"}

    asyncio.run(_run())


@pytest.mark.parametrize(
    "authenticated,message,payload",
    [
        (False, "No token found", None),
        (True, "", None),
    ],
    ids=["unauthenticated", "authenticated_but_no_payload"],
)
def test_required_auth_raises_401(
    authenticated: bool,
    message: str,
    payload: dict | None,
) -> None:
    async def _run() -> None:
        request = _request_with_cookie("x")
        with patch(
            "server.helpers.auth.simple_auth_check",
            new_callable=AsyncMock,
            return_value=(authenticated, message, payload),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await required_auth(request)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == message

    asyncio.run(_run())
