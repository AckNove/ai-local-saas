"""租户资源 CRUD：商户 / 门店 / 员工，全程注入 TenantContext 隔离。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import BizError, ErrorCode
from app.core.responses import ok, paginate
from app.core.security import hash_password
from app.core.tenant import (
    ROLE_MERCHANT,
    ROLE_PLATFORM,
    ROLE_STORE_MANAGER,
    ROLE_VERIFIER,
    TenantContext,
    get_tenant_context,
    require_role,
    tenant_filter,
)
from app.models.tenant import Merchant, Staff, Store
from app.schemas.tenant import (
    MerchantCreate,
    MerchantOut,
    MerchantUpdate,
    StaffCreate,
    StaffOut,
    StaffUpdate,
    StoreCreate,
    StoreOut,
    StoreUpdate,
)

router = APIRouter(prefix="/tenants", tags=["tenants"])


async def _owned_or_404(db: AsyncSession, model, pk: int, ctx: TenantContext):
    """按 id 加载资源；不存在 2001；跨商户 2002。"""
    obj = await db.scalar(select(model).where(model.id == pk))
    if obj is None or getattr(obj, "deleted_at", None) is not None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND)
    if not ctx.is_platform and getattr(obj, "merchant_id", None) != ctx.merchant_id:
        raise BizError(ErrorCode.CROSS_TENANT_DENIED)
    return obj


# ---------------- Merchant ----------------
@router.get("/merchants")
async def list_merchants(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT)),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Merchant)
    if ctx.is_merchant:
        stmt = stmt.where(Merchant.id == ctx.merchant_id)
    else:
        stmt = stmt.where(Merchant.deleted_at.is_(None))
    count_stmt = select(Merchant)
    if ctx.is_merchant:
        count_stmt = count_stmt.where(Merchant.id == ctx.merchant_id)
    else:
        count_stmt = count_stmt.where(Merchant.deleted_at.is_(None))
    total = int(await db.scalar(select(func.count()).select_from(count_stmt.subquery())) or 0)
    stmt = stmt.order_by(Merchant.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([_merchant_out(m) for m in rows], total, page, page_size))


@router.post("/merchants")
async def create_merchant(
    body: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM)),
):
    merchant = Merchant(name=body.name, logo_url=body.logo_url, contact_phone=body.contact_phone)
    if body.merchant_code:
        exists = await db.scalar(select(Merchant).where(Merchant.merchant_code == body.merchant_code))
        if exists is not None:
            raise BizError(ErrorCode.ORDER_STATUS_INVALID, "商家标识已存在，请换一个")
        merchant.merchant_code = body.merchant_code
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return ok(_merchant_out(merchant))


@router.get("/merchants/{merchant_id}")
async def get_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT)),
):
    m = await _owned_or_404(db, Merchant, merchant_id, ctx)
    return ok(_merchant_out(m))


@router.patch("/merchants/{merchant_id}")
async def update_merchant(
    merchant_id: int, body: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT)),
):
    m = await _owned_or_404(db, Merchant, merchant_id, ctx)
    if body.merchant_code is not None and body.merchant_code != m.merchant_code:
        exists = await db.scalar(select(Merchant).where(Merchant.merchant_code == body.merchant_code))
        if exists is not None:
            raise BizError(ErrorCode.ORDER_STATUS_INVALID, "商家标识已存在，请换一个")
    for f in ("name", "logo_url", "contact_phone", "merchant_code", "status"):
        v = getattr(body, f)
        if v is not None:
            setattr(m, f, v)
    await db.commit()
    return ok(_merchant_out(m))


@router.delete("/merchants/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM)),
):
    m = await _owned_or_404(db, Merchant, merchant_id, ctx)
    m.soft_delete()
    await db.commit()
    return ok({"deleted": True})


# ---------------- Store ----------------
@router.get("/stores")
async def list_stores(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER)),
    merchant_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    if ctx.is_staff:
        target_merchant = ctx.merchant_id
        target_store = ctx.store_id
    elif ctx.is_merchant:
        target_merchant = ctx.merchant_id
        target_store = None
    else:
        target_merchant = merchant_id
        target_store = None

    stmt = select(Store).where(Store.deleted_at.is_(None))
    if target_merchant is not None:
        stmt = stmt.where(Store.merchant_id == target_merchant)
    if target_store is not None:
        stmt = stmt.where(Store.id == target_store)
    total = int(await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
    stmt = stmt.order_by(Store.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([_store_out(s) for s in rows], total, page, page_size))


@router.post("/stores")
async def create_store(
    body: StoreCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    merchant_id = ctx.merchant_id if ctx.is_merchant or ctx.is_staff else body.merchant_id
    if merchant_id is None:
        raise BizError(ErrorCode.ORDER_STATUS_INVALID, "平台创建门店需指定 merchant_id")
    if await db.scalar(select(Merchant).where(Merchant.id == merchant_id)) is None:
        raise BizError(ErrorCode.RESOURCE_NOT_FOUND, "商户不存在")
    store = Store(
        merchant_id=merchant_id, name=body.name, address=body.address, phone=body.phone,
        business_hours=body.business_hours, poi_id=body.poi_id, poi_name=body.poi_name,
        lng=body.lng, lat=body.lat,
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return ok(_store_out(store))


@router.get("/stores/{store_id}")
async def get_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER, ROLE_VERIFIER)),
):
    s = await _owned_or_404(db, Store, store_id, ctx)
    return ok(_store_out(s))


@router.patch("/stores/{store_id}")
async def update_store(
    store_id: int, body: StoreUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    s = await _owned_or_404(db, Store, store_id, ctx)
    for f in ("name", "address", "phone", "business_hours", "poi_id", "poi_name", "lng", "lat"):
        v = getattr(body, f)
        if v is not None:
            setattr(s, f, v)
    await db.commit()
    return ok(_store_out(s))


@router.delete("/stores/{store_id}")
async def delete_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    s = await _owned_or_404(db, Store, store_id, ctx)
    s.soft_delete()
    await db.commit()
    return ok({"deleted": True})


# ---------------- Staff ----------------
@router.get("/staff")
async def list_staff(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
    store_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Staff).where(Staff.deleted_at.is_(None))
    if ctx.is_staff:
        stmt = stmt.where(Staff.merchant_id == ctx.merchant_id, Staff.store_id == ctx.store_id)
    elif ctx.is_merchant:
        stmt = stmt.where(Staff.merchant_id == ctx.merchant_id)
    if store_id is not None and ctx.is_platform:
        stmt = stmt.where(Staff.store_id == store_id)
    total = int(await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
    stmt = stmt.order_by(Staff.id.desc()).limit(page_size).offset((page - 1) * page_size)
    rows = list((await db.scalars(stmt)).all())
    return ok(paginate([_staff_out(s) for s in rows], total, page, page_size))


@router.post("/staff")
async def create_staff(
    body: StaffCreate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    store = await _owned_or_404(db, Store, body.store_id, ctx)
    if body.role not in ("store_manager", "verifier"):
        raise BizError(ErrorCode.NO_PERMISSION, "角色须为 store_manager/verifier")
    staff = Staff(
        merchant_id=store.merchant_id, store_id=store.id, name=body.name,
        role=body.role, username=body.username, phone=body.phone, openid=body.openid,
        password_hash=hash_password(body.password) if body.password else None,
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return ok(_staff_out(staff))


@router.get("/staff/{staff_id}")
async def get_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    s = await _owned_or_404(db, Staff, staff_id, ctx)
    return ok(_staff_out(s))


@router.patch("/staff/{staff_id}")
async def update_staff(
    staff_id: int, body: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    s = await _owned_or_404(db, Staff, staff_id, ctx)
    for f in ("name", "role", "store_id", "phone", "openid", "is_active"):
        v = getattr(body, f)
        if v is not None:
            setattr(s, f, v)
    await db.commit()
    return ok(_staff_out(s))


@router.delete("/staff/{staff_id}")
async def delete_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(require_role(ROLE_PLATFORM, ROLE_MERCHANT, ROLE_STORE_MANAGER)),
):
    s = await _owned_or_404(db, Staff, staff_id, ctx)
    s.soft_delete()
    await db.commit()
    return ok({"deleted": True})


# ---------------- 序列化助手 ----------------
def _merchant_out(m: Merchant) -> dict:
    return MerchantOut(
        id=m.id, name=m.name, logo_url=m.logo_url, contact_phone=m.contact_phone,
        merchant_code=m.merchant_code,
        status=m.status, created_at=_iso(m.created_at),
    ).model_dump()


def _store_out(s: Store) -> dict:
    return StoreOut(
        id=s.id, merchant_id=s.merchant_id, name=s.name, address=s.address, phone=s.phone,
        business_hours=s.business_hours, poi_id=s.poi_id, poi_name=s.poi_name,
        lng=s.lng, lat=s.lat, created_at=_iso(s.created_at),
    ).model_dump()


def _staff_out(s: Staff) -> dict:
    return StaffOut(
        id=s.id, merchant_id=s.merchant_id, store_id=s.store_id, name=s.name, role=s.role,
        username=s.username, phone=s.phone, openid=s.openid, is_active=s.is_active,
        created_at=_iso(s.created_at),
    ).model_dump()


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None
