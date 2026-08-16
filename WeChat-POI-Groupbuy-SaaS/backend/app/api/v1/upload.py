"""文件上传 API：图片上传（供套餐图文、商户 Logo 等使用）。

- 单文件 multipart 上传，保存到本地上传目录 uploads/。
- 返回可直接访问的 URL 路径（由 main.py 挂载 /uploads 静态目录）。
- 生产环境建议替换为对象存储（OSS/COS），此处为本地落盘实现，零外部依赖。
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse

from app.core.tenant import (
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    TenantContext,
    require_role,
)

router = APIRouter(prefix="/upload", tags=["upload"])

# 上传目录（backend/uploads），main.py 挂载 /uploads 提供访问
_UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"

# 允许的图片扩展名与对应 MIME
_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.post("/image")
async def upload_image(
    file: UploadFile,
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    """上传单张图片，返回 { url }（相对路径，前端拼 API 基址或同源访问）。"""
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXT:
        return JSONResponse(status_code=200, content={"code": 422, "message": "仅支持 jpg/png/gif/webp 图片", "data": None})

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB 上限
        return JSONResponse(status_code=200, content={"code": 422, "message": "图片不能超过 5MB", "data": None})

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    dest = _UPLOAD_DIR / name
    dest.write_bytes(content)

    url = f"/uploads/{name}"
    return JSONResponse(status_code=200, content={"code": 0, "message": "ok", "data": {"url": url}})
