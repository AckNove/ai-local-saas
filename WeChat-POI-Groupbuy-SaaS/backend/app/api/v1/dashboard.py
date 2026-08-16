"""数据看板 API：商户侧指标 + 平台汇总。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok
from app.core.tenant import ROLE_CONSUMER, ROLE_PLATFORM, TenantContext, get_tenant_context, require_role
from app.services.metrics import compute_metrics

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.get("/metrics")
async def metrics_api(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
    merchant_id: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """商户看板（默认取自身 merchant_id）；平台可指定 merchant_id 或汇总。"""
    if ctx.role == ROLE_CONSUMER:
        raise BizError(ErrorCode.NO_PERMISSION)
    target = merchant_id if ctx.is_platform else ctx.merchant_id
    metrics = await compute_metrics(db, target, _parse_dt(date_from), _parse_dt(date_to))
    return ok(metrics)
