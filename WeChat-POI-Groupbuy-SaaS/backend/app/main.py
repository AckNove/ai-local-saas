"""FastAPI 应用入口：CORS / 路由挂载 / 全局异常 / 健康检查 / 可选单服务托管 Web 后台。

API 统一前缀 /api/v1；所有响应为 {code, message, data}（见 core/responses）。

部署模式：
- 分离模式（默认）：仅挂 API，Web 后台经 CORS 独立运行（开发期 npm run dev）。
- 单服务模式：WEB_ADMIN_DIST 指向已构建的 web-admin/dist 时，后端同时托管前端
  静态资源（/assets 与 SPA 回退），前端以相对 VITE_API_BASE=/api/v1 同源调用。
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.api.v1 import (
    auth,
    catalog,
    dashboard,
    fulfillment,
    orders,
    public,
    refunds,
    tenants,
    upload,
    verification,
)

app = FastAPI(title="微信视频号 POI 团购 SaaS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

API_V1 = "/api/v1"
app.include_router(auth.router, prefix=API_V1)
app.include_router(tenants.router, prefix=API_V1)
app.include_router(catalog.router, prefix=API_V1)
app.include_router(orders.router, prefix=API_V1)
app.include_router(verification.router, prefix=API_V1)
app.include_router(refunds.router, prefix=API_V1)
app.include_router(dashboard.router, prefix=API_V1)
app.include_router(fulfillment.router, prefix=API_V1)
app.include_router(upload.router, prefix=API_V1)
app.include_router(public.router, prefix=API_V1)


# --- 图片上传目录静态托管（供套餐图文 / 商户 Logo 访问）---
_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_UPLOAD_DIR)), name="uploads")


@app.get("/api/health", tags=["health"])
async def health():
    """健康检查。"""
    from app.core.responses import ok

    return ok({"status": "ok"})


# --- 单服务部署：托管 Web 后台静态产物（dist 存在才挂载，分离模式不受影响）---
_DIST_DIR = settings.WEB_ADMIN_DIST or str(
    Path(__file__).resolve().parent.parent.parent / "web-admin" / "dist"
)
if os.path.isdir(_DIST_DIR):
    _ASSETS_DIR = os.path.join(_DIST_DIR, "assets")
    if os.path.isdir(_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="web-assets")

    _INDEX_FILE = os.path.join(_DIST_DIR, "index.html")

    @app.get("/{full_path:path}")
    async def _spa_fallback(full_path: str):
        # /api 路径交给上方 API 路由；未命中才回退到 index.html（SPA history 模式）
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not Found")
        return FileResponse(_INDEX_FILE)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVER_PORT, reload=False)
