"""FastAPI 应用入口。

职责：
- 创建 app、配置 CORS
- 挂载 /api 路由（认证 / 商家 / 种草卡 / AI / 统计）
- 提供消费者 H5 落地页 GET /c/{slug} 与 /h5 静态资源
- 可选托管 frontend/dist（目录存在时）
- 启动时 Base.metadata.create_all 建表
- 统一错误响应（HTTPException / 校验错误 → {code,message,data}）
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import ai, auth, h5, merchant, seed_card, stats
from config import CORS_ORIGINS
from app.database import init_db
from app.utils.response import api_response

# 项目根（backend/ 的上一级），h5 与 frontend 均位于此
ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
H5_DIR = PROJECT_ROOT / "h5"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 启动时建表（幂等）
    await init_db()
    yield


app = FastAPI(
    title="AI 本地商家增长 SaaS",
    version="1.0.0",
    description="管理员 / 商家后台 API + 消费者 H5 落地页",
    lifespan=lifespan,
)

# --- CORS ---
_allow_origins = list(CORS_ORIGINS)
_allow_regex = None
if "*" in _allow_origins:
    _allow_regex = ".*"
    _allow_origins = []
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_origin_regex=_allow_regex,
    allow_credentials=False if _allow_regex else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API 路由 ---
app.include_router(auth.router)
app.include_router(merchant.router)
app.include_router(seed_card.router)
app.include_router(ai.router)
app.include_router(stats.router)

# --- H5 落地页路由（须在任何 /{path} 兜底之前注册）---
app.include_router(h5.router)

# --- H5 静态资源（app.js / style.css）---
if H5_DIR.exists():
    app.mount("/h5", StaticFiles(directory=str(H5_DIR)), name="h5")

# --- 系统健康检查（须在 SPA 兜底之前注册，避免被 /{full_path:path} 吞掉）---
@app.get("/api/health", tags=["system"])
async def health():
    return api_response(0, "ok", {"status": "up"}, 200)


# --- 前端后台构建产物（可选，目录存在才挂载）---
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="front-assets")

    @app.get("/{full_path:path}")
    async def spa_index(full_path: str):  # noqa: ARG001
        """SPA 兜底：未匹配路径返回前端 index.html。

        排除后端路由前缀（/api、/c、/h5、/assets），避免拦截 API、H5 落地页
        与静态资源；同时保证 /api/health 等兜底路由不被覆盖。
        """
        if full_path.startswith(("api/", "c/", "h5", "assets")):
            return api_response(404, "not found", None, 404)
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index), media_type="text/html")
        return api_response(404, "not found", None, 404)


# --- 统一异常处理 ---
_CODE_BY_STATUS = {401: 401, 403: 403, 404: 404, 422: 422, 429: 429, 500: 500}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):  # noqa: ANN001
    code = _CODE_BY_STATUS.get(exc.status_code, exc.status_code)
    return api_response(code, exc.detail, None, exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):  # noqa: ANN001
    return api_response(422, "参数错误", exc.errors(), 422)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):  # noqa: ANN001
    return api_response(500, "服务器内部错误", None, 500)


if __name__ == "__main__":
    import uvicorn

    from config import APP_HOST, APP_PORT

    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=False)
