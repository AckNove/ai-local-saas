"""小程序端公开接口：无需登录，通过 merchant_code 拉取商家品牌配置与套餐。

设计（单商户小程序模式）：
- 每个商家一个小程序，小程序 config.js 里写死该商家的 MERCHANT_CODE。
- 小程序启动时调 /public/config?code=xxx 拿到品牌信息（店名/logo/电话）与已上架套餐。
- 无需 JWT，顾客浏览无需登录；下单时再走 wx-login。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.responses import ok
from app.models.catalog import GroupBuyPackage, PackageStore
from app.models.tenant import Merchant, Store

router = APIRouter(prefix="/public", tags=["public"])


async def _store_ids(db: AsyncSession, pkg_id: int) -> list[int]:
    rows = (await db.scalars(
        select(PackageStore.store_id).where(PackageStore.package_id == pkg_id)
    )).all()
    return list(rows)


@router.get("/config")
async def public_config(
    code: str = Query(..., description="商家标识 merchant_code"),
    db: AsyncSession = Depends(get_db),
):
    """按商家标识返回品牌配置 + 门店 + 已上架套餐。小程序端用。"""
    merchant = await db.scalar(
        select(Merchant).where(
            Merchant.merchant_code == code, Merchant.deleted_at.is_(None)
        )
    )
    if merchant is None:
        return ok({"merchant": None, "stores": [], "packages": []})

    stores = list((await db.scalars(
        select(Store).where(Store.merchant_id == merchant.id, Store.deleted_at.is_(None))
    )).all())

    packages = list((await db.scalars(
        select(GroupBuyPackage).where(
            GroupBuyPackage.merchant_id == merchant.id,
            GroupBuyPackage.status == "published",
            GroupBuyPackage.deleted_at.is_(None),
        ).order_by(GroupBuyPackage.id.desc())
    )).all())

    pkg_list = []
    for p in packages:
        pkg_list.append(
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "original_price": p.original_price,
                "group_price": p.group_price,
                "stock": p.stock,
                "sold_count": p.sold_count,
                "images_json": p.images_json,
                "store_ids": await _store_ids(db, p.id),
            }
        )

    return ok(
        {
            "merchant": {
                "id": merchant.id,
                "name": merchant.name,
                "logo_url": merchant.logo_url,
                "contact_phone": merchant.contact_phone,
                "merchant_code": merchant.merchant_code,
            },
            "stores": [
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "phone": s.phone,
                    "business_hours": s.business_hours,
                    "poi_name": s.poi_name,
                }
                for s in stores
            ],
            "packages": pkg_list,
        }
    )
