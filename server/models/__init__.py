from typing import Any


def ResponseModel(data: Any, message: str, authed: bool = False) -> dict[str, Any]:
    return {
        "data": data,
        "code": 200,
        "message": message,
        "loggedIn": authed,
    }


def ErrorResponseModel(error: str, code: int, message: str) -> dict[str, Any]:
    return {"error": error, "code": code, "message": message}
