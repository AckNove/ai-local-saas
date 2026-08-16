"""全局异常处理器注册。

- BizError        -> 统一 {code, message, data}
- RequestValidationError -> {code: 9000, message: "参数校验失败", data: detail}
- 其它 Exception  -> {code: 9000, message: "系统错误"}
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import BizError, ErrorCode
from app.core.responses import error


def register_exception_handlers(app: FastAPI) -> None:
    """向 FastAPI 应用注册全局异常处理器。"""

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        request, exc: RequestValidationError
    ) -> JSONResponse:
        return error(
            ErrorCode.SYSTEM_ERROR,
            "参数校验失败",
            data=exc.errors(),
            http_status=200,
        )

    @app.exception_handler(BizError)
    async def _biz_handler(request, exc: BizError) -> JSONResponse:
        return error(exc.code, exc.message, exc.data, exc.http_status)

    @app.exception_handler(Exception)
    async def _unhandled_handler(request, exc: Exception) -> JSONResponse:
        return error(ErrorCode.SYSTEM_ERROR, "系统错误", http_status=500)
