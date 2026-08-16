"""商家与门店路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sys_user import SysUser
from app.schemas.merchant import (
    DisableIn,
    MerchantCreate,
    MerchantOut,
    MerchantUpdate,
    StoreIn,
    StoreOut,
)
from app.services import merchant_service as svc
from app.utils.response import bad_request, forbidden, not_found, ok, paginated
from app.utils.rbac import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["merchant"])


def _to_merchant_out(merchant, stores) -> MerchantOut:
    stores_out = [
        StoreOut(
            id=s.id,
            merchant_id=s.merchant_id,
            name=s.name,
            location=s.location,
            video_account=s.video_account,
            poi_status=s.poi_status,
            status=s.status,
        )
        for s in stores
    ]
    return MerchantOut(
        id=merchant.id,
        name=merchant.name,
        industry=merchant.industry,
        address=merchant.address,
        contact=merchant.contact,
        phone=merchant.phone,
        package=merchant.package,
        expire_time=merchant.expire_time,
        status=merchant.status,
        created_at=merchant.created_at,
        stores=stores_out,
    )


@router.post("/merchant/create")
async def create_merchant(
    body: MerchantCreate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    merchant = await svc.create_merchant(db, body, current_user)
    stores = await svc.get_stores(db, merchant.id)
    out = _to_merchant_out(merchant, stores)
    return ok(out.model_dump())


@router.get("/merchant/list")
async def list_merchants(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    keyword: str = Query("", description="名称/联系人/电话模糊搜索"),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await svc.list_merchants(db, page, size, keyword, current_user)
    return ok(paginated(items, total))


@router.get("/merchant/{merchant_id}")
async def get_merchant(
    merchant_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    merchant = await svc.get_merchant(db, merchant_id, current_user)
    if merchant is None:
        return not_found("商家不存在")
    stores = await svc.get_stores(db, merchant.id)
    return ok(_to_merchant_out(merchant, stores).model_dump())


@router.put("/merchant/{merchant_id}")
async def update_merchant(
    merchant_id: int,
    body: MerchantUpdate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    merchant = await svc.update_merchant(db, merchant_id, body, current_user)
    if merchant is None:
        return not_found("商家不存在或无权限")
    stores = await svc.get_stores(db, merchant.id)
    return ok(_to_merchant_out(merchant, stores).model_dump())


@router.post("/merchant/{merchant_id}/disable")
async def disable_merchant(
    merchant_id: int,
    body: DisableIn,
    _: SysUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    merchant = await svc.disable_merchant(db, merchant_id, body.disabled)
    if merchant is None:
        return not_found("商家不存在")
    return ok({"id": merchant.id, "status": merchant.status})


@router.delete("/merchant/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    _: SysUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    ok_del = await svc.delete_merchant(db, merchant_id)
    if not ok_del:
        return not_found("商家不存在")
    return ok({"id": merchant_id, "status": "deleted"})


@router.post("/merchant/{merchant_id}/store")
async def create_store(
    merchant_id: int,
    body: StoreIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    store = await svc.create_store(db, merchant_id, body, current_user)
    if store is None:
        return forbidden("商家不存在或无权限")
    return ok(_store_out(store))


@router.put("/store/{store_id}")
async def update_store(
    store_id: int,
    body: StoreIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    store = await svc.update_store(db, store_id, body, current_user)
    if store is None:
        return not_found("门店不存在或无权限")
    return ok(_store_out(store))


@router.delete("/store/{store_id}")
async def delete_store(
    store_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok_del = await svc.delete_store(db, store_id, current_user)
    if not ok_del:
        return not_found("门店不存在或无权限")
    return ok({"id": store_id, "status": "deleted"})


def _store_out(store) -> dict:
    return StoreOut(
        id=store.id,
        merchant_id=store.merchant_id,
        name=store.name,
        location=store.location,
        video_account=store.video_account,
        poi_status=store.poi_status,
        status=store.status,
    ).model_dump()
