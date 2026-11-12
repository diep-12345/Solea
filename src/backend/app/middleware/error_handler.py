import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # 1. Xử lý lỗi HTTP: 400, 401, 403, 404...
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail)
            },
            headers=exc.headers
        )

    # 2. Xử lý lỗi dữ liệu đầu vào
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Dữ liệu đầu vào không hợp lệ",
                "errors": jsonable_encoder(exc.errors())
            }
        )

    # 3. Xử lý lỗi hệ thống không dự kiến
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):
        logger.exception("Lỗi hệ thống: %s", exc)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Đã xảy ra lỗi hệ thống"
            }
        )