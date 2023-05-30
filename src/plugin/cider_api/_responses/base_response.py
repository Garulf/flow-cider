from typing import TypedDict


class BaseResponse(TypedDict):
    status: int
    data: dict
    message: str
    type: str
