"""消费者 H5 落地页路由：GET /c/{slug} 返回静态落地页。"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

# backend/app/api/h5.py -> project_root/h5/index.html
H5_INDEX = (
    Path(__file__).resolve().parent.parent.parent.parent / "h5" / "index.html"
)

router = APIRouter(tags=["h5"])


@router.get("/c/{slug}")
async def landing_page(slug: str):  # noqa: ARG001
    """返回种草卡落地页（H5 静态页）。"""
    if not H5_INDEX.exists():
        return Response("H5 页面未部署", status_code=404, media_type="text/plain")
    return FileResponse(str(H5_INDEX), media_type="text/html")
