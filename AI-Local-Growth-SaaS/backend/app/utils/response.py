"""统一 API 响应封装。

所有业务接口返回统一结构：
    { "code": 0, "message": "ok", "data": {} }

code 约定：
    0   成功
    401 未认证
    403 无权限
    404 不存在
    422 参数错误
    429 限流
    500 服务器错误

列表中 data 含 items 与 total。
"""
from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def api_response(
    code: int = 0,
    message: str = "ok",
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """构造统一 JSON 响应。HTTP 状态码与业务 code 保持一致。

    data 经 jsonable_encoder 转换，确保 datetime / Pydantic 模型等可被
    标准 JSON 序列化（默认 json.dumps 无法处理带时区的 datetime）。
    """
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": jsonable_encoder(data)},
    )


def ok(data: Any = None, message: str = "ok") -> JSONResponse:
    """成功响应。"""
    return api_response(0, message, data, 200)


def unauthorized(message: str = "未认证") -> JSONResponse:
    return api_response(401, message, None, 401)


def forbidden(message: str = "无权限") -> JSONResponse:
    return api_response(403, message, None, 403)


def not_found(message: str = "资源不存在") -> JSONResponse:
    return api_response(404, message, None, 404)


def bad_request(message: str = "参数错误") -> JSONResponse:
    return api_response(422, message, None, 422)


def too_many_requests(message: str = "请求过于频繁") -> JSONResponse:
    return api_response(429, message, None, 429)


def server_error(message: str = "服务器内部错误") -> JSONResponse:
    return api_response(500, message, None, 500)


def paginated(items: Any, total: int, **extra: Any) -> dict:
    """构造列表分页 data：含 items 与 total。"""
    data: dict[str, Any] = {"items": items, "total": total}
    data.update(extra)
    return data
