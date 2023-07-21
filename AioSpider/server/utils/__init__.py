import time
from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from utils.error_codes import *


class ErrorInfo:

    def __init__(self, status: int, msg: str, status_code: int = 400, data: list = None):
        self.status = status
        self.msg = msg
        self.status_code = 200
        self.data = data if data else []

    @property
    def to_dict(self):
        return {"status": self.status, "msg": self.msg, "data": self.data}


class CustomHTTPException(HTTPException):
    def __init__(self, error_info: ErrorInfo):
        super().__init__(status_code=error_info.status_code, detail=None)
        self.status = error_info.status
        self.msg = error_info.msg
        self.data = error_info.data


async def error_info_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        content={
            "status": exc.status, "msg": exc.msg, "data": exc.data
        },
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return to_json(StatusTags.InvalidParamsError, error_map[StatusTags.InvalidParamsError])


def to_json(status: int = error_map[StatusTags.OK], msg: str = StatusTags.OK, data: list = None):

    if data is None:
        data = []

    if isinstance(data, dict):
        data = [data]

    return JSONResponse(
        status_code=200,
        content={'status': status, 'msg': msg, 'stamp': time.time() * 1000 // 1, 'data': data}
    )


WorkSpace = Path('D:\\Project')
WorkSpace.mkdir(exist_ok=True, parents=True)
