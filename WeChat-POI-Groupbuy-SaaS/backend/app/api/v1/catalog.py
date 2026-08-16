"""团购套餐 API：CRUD + 上架/下架（金额单位：分）。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok, paginate
from app.core.tenant import (
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    TenantContext,
    get_tenant_context,
    require_role,
    tenant_filter,
)
from app.models.catalog import GroupBuyPackage, PackageStore
from app.schemas.catalog import PackageCreate, PackageOut, PackageUpdate

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "时间格式应为 ISO 8601") from exc


async def _store_ids_of(db: AsyncSession, package_id: int) -> list[int]:
    rows = (await db.scalars(
        select(PackageStore.store_id).where(PackageStore.package_id == package_id)
    )).all()
    return list(rows)


async def _package_out(db: AsyncSession, p: GroupBuyPackage) -> dict:
    return PackageOut(
        id=p.id, merchant_id=p.merchant_id, name=p.name, description=p.description,
        original_price=p.original_price, group_price=p.group_price, stock=p.stock,
        sold_count=p.sold_count, valid_from=_iso(p.valid_from), valid_to=_iso(p.valid_to),
        status=p.status, images_json=p.images_json,
        store_ids=await _store_ids_of(db, p.id), created_at=_iso(p.created_at),
    ).model_dump()


@router.get("/packages")
async def list_packages(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
    store_id: int | None = Query(None),
    merchant_id: int | None = Query(None),
    keyword: str | None = Query(None, description="套餐名模糊搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """C 端/后台套餐列表。默认仅返回 published（C 端）；后台可看本商户全部。"""
    show_all = ctx.role in (ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)
    stmt = select(GroupBuyPackage).where(GroupBuyPackage.deleted_at.is_(None))
    if show_all:
        stmt = tenant_filter(stmt, GroupBuyPackage, ctx)
        if merchant_id is not None and ctx.is_platform:
            stmt = stmt.where(GroupBuyPackage.merchant_id == merchant_id)
    else:
        stmt = stmt.where(GroupBuyPackage.status == "published")

    if store_id is not None:
        stmt = stmt.join(PackageStore, PackageStore.package_id == GroupBuyPackage.id).where(
            PackageStore.store_id == store_id
        )
    if keyword:
        stmt = stmt.where(GroupBuyPackage.name.like(f"%{keyword}%"))

    total = int(await db.scalar(
        select(func.count()).select_from(stmt.subquery())
    ) or 0)
    stmt = stmt.order_by(GroupBuyPackage.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([await _package_out(db, p) for p in rows], total, page, page_size))


@router.post("/packages")
async def create_package(
    body: PackageCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_PLATFORM)),
):
    if ctx.is_consumer:
        raise BizError(ErrorCode.NO_PERMISSION)
    if ctx.is_platform:
        merchant_id = await _merchant_of_first_store(db, body.store_ids)
    else:
        merchant_id = ctx.merchant_id
    package = GroupBuyPackage(
        merchant_id=merchant_id if merchant_id is not None else _merchant_of_first_store(db, body.store_ids),
        name=body.name, description=body.description, original_price=body.original_price,
        group_price=body.group_price, stock=body.stock, valid_from=_parse_dt(body.valid_from),
        valid_to=_parse_dt(body.valid_to), status="draft", images_json=body.images_json,
    )
    db.add(package)
    await db.flush()
    await _sync_store_links(db, package.id, body.store_ids)
    await db.commit()
    await db.refresh(package)
    return ok(await _package_out(db, package))


async def _merchant_of_first_store(db: AsyncSession, store_ids: list[int]) -> int:
    if not store_ids:
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "需指定适用门店")
    from app.models.tenant import Store

    store = await db.scalar(select(Store).where(Store.id == store_ids[0]))
    if store is None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "门店不存在")
    return store.merchant_id


async def _sync_store_links(db: AsyncSession, package_id: int, store_ids: list[int]) -> None:
    await db.execute(
        PackageStore.__table__.delete().where(PackageStore.package_id == package_id)
    )
    for sid in store_ids or []:
        db.add(PackageStore(package_id=package_id, store_id=sid))


@router.get("/packages/{package_id}")
async def get_package(
    package_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    p = await db.scalar(select(GroupBuyPackage).where(GroupBuyPackage.id == package_id))
    if p is None or p.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND)
    if not ctx.is_platform and ctx.role in (ROLE_MERCHANT, ROLE_STORE_MANAGER) and p.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    return ok(await _package_out(db, p))


@router.patch("/packages/{package_id}")
async def update_package(
    package_id: int, body: PackageUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_PLATFORM)),
):
    p = await db.scalar(select(GroupBuyPackage).where(GroupBuyPackage.id == package_id))
    if p is None or p.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND)
    if not ctx.is_platform and p.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    for f in ("name", "description", "original_price", "group_price", "stock", "images_json"):
        v = getattr(body, f)
        if v is not None:
            setattr(p, f, v)
    if body.valid_from is not None:
        p.valid_from = _parse_dt(body.valid_from)
    if body.valid_to is not None:
        p.valid_to = _parse_dt(body.valid_to)
    if body.store_ids is not None:
        await _sync_store_links(db, p.id, body.store_ids)
    await db.commit()
    return ok(await _package_out(db, p))


@router.post("/packages/{package_id}/publish")
async def publish_package(
    package_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_PLATFORM)),
):
    p = await db.scalar(select(GroupBuyPackage).where(GroupBuyPackage.id == package_id))
    if p is None or p.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND)
    if not ctx.is_platform and p.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    p.status = "published"
    await db.commit()
    return ok(await _package_out(db, p))


@router.post("/packages/{package_id}/off-shelf")
async def off_shelf_package(
    package_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_PLATFORM)),
):
    p = await db.scalar(select(GroupBuyPackage).where(GroupBuyPackage.id == package_id))
    if p is None or p.deleted_at is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND)
    if not ctx.is_platform and p.merchant_id != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    p.status = "off_shelf"
    await db.commit()
    return ok(await _package_out(db, p))


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None
