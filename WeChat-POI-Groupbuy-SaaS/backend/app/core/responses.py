"""统一 API 响应封装。

所有接口返回：
    { "code": 0, "message": "ok", "data": {} }

列表接口 data 形如：
    { "list": [...], "total": N, "page": 1, "page_size": 20 }
"""
from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "ok") -> JSONResponse:
    """成功响应（code=0）。"""
    return JSONResponse(
        status_code=200,
        content={"code": 0, "message": message, "data": jsonable_encoder(data)},
    )


def error(
    code: int,
    message: str,
    data: Any = None,
    http_status: int = 200,
) -> JSONResponse:
    """业务错误响应（code 非 0）。"""
    return JSONResponse(
        status_code=http_status,
        content={"code": code, "message": message, "data": jsonable_encoder(data)},
    )


def paginate(items: Any, total: int, page: int = 1, page_size: int = 20) -> dict:
    """构造列表分页 data：{list, total, page, page_size}。"""
    return {
        "list": jsonable_encoder(items),
        "total": total,
        "page": page,
        "page_size": page_size,
    }
