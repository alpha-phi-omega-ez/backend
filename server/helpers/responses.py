from typing import Any


def Response(data: Any, message: str) -> dict[str, Any]:
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponse(error: str, code: int, message: str) -> dict[str, Any]:
    return {"error": error, "code": code, "message": message}
