from typing import Any


def ResponseModel(data: Any, message: str) -> dict[str, Any]:
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error: str, code: int, message: str) -> dict[str, Any]:
    return {"error": error, "code": code, "message": message}
