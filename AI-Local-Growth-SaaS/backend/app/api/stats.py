"""统计路由：平台 / 商家数据概览。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sys_user import SysUser
from app.schemas.stats import StatsOverviewOut
from app.services import stats_service as svc
from app.utils.response import ok
from app.utils.rbac import get_current_user

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats/overview")
async def stats_overview(
    merchant_id: int | None = Query(None, description="admin 可不传，查看全部"),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await svc.overview(db, current_user, merchant_id)
    return ok(StatsOverviewOut(**data).model_dump())
