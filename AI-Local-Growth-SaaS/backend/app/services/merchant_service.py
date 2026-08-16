"""商家与门店业务逻辑。

所有查询强制 merchant_id 作用域：
- merchant 角色：仅能访问 `SysUser.merchant_id` 对应的商家（及其门店）。
- admin 角色：豁免，可访问全部。
- 列表默认排除 status == 'deleted'（保留 active / disabled 以便恢复）。
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant_info import MerchantInfo
from app.models.store_info import StoreInfo
from app.models.sys_user import SysUser
from app.schemas.merchant import MerchantCreate, MerchantUpdate, StoreIn


def _scope(current_user: SysUser) -> int | None:
    """返回作用域 merchant_id；admin 返回 None（全量）。"""
    if current_user.role == "merchant":
        return current_user.merchant_id
    return None


async def create_merchant(
    db: AsyncSession, data: MerchantCreate, current_user: SysUser
) -> MerchantInfo:
    """创建商家（及初始门店）。"""
    merchant = MerchantInfo(
        name=data.name,
        industry=data.industry,
        address=data.address,
        contact=data.contact,
        phone=data.phone,
        package=data.package,
        expire_time=data.expire_time,
        status="active",
    )
    db.add(merchant)
    await db.flush()  # 获得 merchant.id
    for s in data.stores:
        db.add(
            StoreInfo(
                merchant_id=merchant.id,
                name=s.name,
                location=s.location,
                video_account=s.video_account,
                poi_status=s.poi_status,
                status="active",
            )
        )
    await db.commit()
    await db.refresh(merchant)
    return merchant


async def list_merchants(
    db: AsyncSession,
    page: int,
    size: int,
    keyword: str,
    current_user: SysUser,
) -> tuple[list[dict], int]:
    """分页列出商家（带 keyword 模糊搜索与状态过滤）。"""
    scope = _scope(current_user)
    base = select(MerchantInfo).where(MerchantInfo.status != "deleted")
    if scope is not None:
        base = base.where(MerchantInfo.id == scope)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            (MerchantInfo.name.like(like))
            | (MerchantInfo.contact.like(like))
            | (MerchantInfo.phone.like(like))
        )

    total_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    rows = (
        await db.execute(
            base.order_by(MerchantInfo.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    ).scalars().all()

    items: list[dict] = []
    for m in rows:
        store_count = await count_stores(db, m.id)
        items.append(
            {
                "id": m.id,
                "name": m.name,
                "industry": m.industry,
                "status": m.status,
                "store_count": store_count,
            }
        )
    return items, total


async def count_stores(db: AsyncSession, merchant_id: int) -> int:
    """统计某商家下未删除的门店数。"""
    stmt = select(func.count()).select_from(StoreInfo).where(
        StoreInfo.merchant_id == merchant_id, StoreInfo.status != "deleted"
    )
    return (await db.execute(stmt)).scalar_one()


async def get_merchant(
    db: AsyncSession, merchant_id: int, current_user: SysUser
) -> MerchantInfo | None:
    """获取商家详情（含门店），越权或无记录返回 None。"""
    scope = _scope(current_user)
    if scope is not None and merchant_id != scope:
        return None
    result = await db.execute(
        select(MerchantInfo).where(
            MerchantInfo.id == merchant_id, MerchantInfo.status != "deleted"
        )
    )
    return result.scalar_one_or_none()


async def get_stores(db: AsyncSession, merchant_id: int) -> list[StoreInfo]:
    """获取某商家下未删除的门店列表（供详情 / 创建响应使用）。"""
    return await _load_stores(db, merchant_id)


async def _load_stores(db: AsyncSession, merchant_id: int) -> list[StoreInfo]:
    result = await db.execute(
        select(StoreInfo)
        .where(StoreInfo.merchant_id == merchant_id, StoreInfo.status != "deleted")
        .order_by(StoreInfo.id.asc())
    )
    return list(result.scalars().all())


async def update_merchant(
    db: AsyncSession, merchant_id: int, data: MerchantUpdate, current_user: SysUser
) -> MerchantInfo | None:
    """更新商家资料（仅更新提供的字段）。"""
    merchant = await get_merchant(db, merchant_id, current_user)
    if merchant is None:
        return None
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is not None:
            setattr(merchant, field, value)
    await db.commit()
    await db.refresh(merchant)
    return merchant


async def disable_merchant(
    db: AsyncSession, merchant_id: int, disabled: bool
) -> MerchantInfo | None:
    """禁用 / 启用商家（仅置 status）。"""
    result = await db.execute(
        select(MerchantInfo).where(
            MerchantInfo.id == merchant_id, MerchantInfo.status != "deleted"
        )
    )
    merchant = result.scalar_one_or_none()
    if merchant is None:
        return None
    merchant.status = "disabled" if disabled else "active"
    await db.commit()
    await db.refresh(merchant)
    return merchant


async def delete_merchant(db: AsyncSession, merchant_id: int) -> bool:
    """软删除商家（同时软删其门店）。"""
    result = await db.execute(
        select(MerchantInfo).where(MerchantInfo.id == merchant_id)
    )
    merchant = result.scalar_one_or_none()
    if merchant is None:
        return False
    merchant.soft_delete()
    stores = await _load_stores(db, merchant_id)
    for s in stores:
        s.soft_delete()
    await db.commit()
    return True


async def create_store(
    db: AsyncSession, merchant_id: int, data: StoreIn, current_user: SysUser
) -> StoreInfo | None:
    """为商家新增门店（校验作用域）。"""
    scope = _scope(current_user)
    if scope is not None and merchant_id != scope:
        return None
    result = await db.execute(
        select(MerchantInfo).where(
            MerchantInfo.id == merchant_id, MerchantInfo.status != "deleted"
        )
    )
    if result.scalar_one_or_none() is None:
        return None
    store = StoreInfo(
        merchant_id=merchant_id,
        name=data.name,
        location=data.location,
        video_account=data.video_account,
        poi_status=data.poi_status,
        status="active",
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


async def update_store(
    db: AsyncSession, store_id: int, data: StoreIn, current_user: SysUser
) -> StoreInfo | None:
    """更新门店（校验作用域）。"""
    scope = _scope(current_user)
    result = await db.execute(
        select(StoreInfo).where(
            StoreInfo.id == store_id, StoreInfo.status != "deleted"
        )
    )
    store = result.scalar_one_or_none()
    if store is None:
        return None
    if scope is not None and store.merchant_id != scope:
        return None
    for field, value in data.model_dump().items():
        setattr(store, field, value)
    await db.commit()
    await db.refresh(store)
    return store


async def delete_store(db: AsyncSession, store_id: int, current_user: SysUser) -> bool:
    """软删除门店（校验作用域）。"""
    scope = _scope(current_user)
    result = await db.execute(select(StoreInfo).where(StoreInfo.id == store_id))
    store = result.scalar_one_or_none()
    if store is None:
        return False
    if scope is not None and store.merchant_id != scope:
        return False
    store.soft_delete()
    await db.commit()
    return True
