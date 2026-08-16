"""种草卡业务逻辑：创建（生成 slug + 二维码）、查询、事件写入。"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import PUBLIC_BASE_URL
from app.models.seed_card import SeedCard
from app.models.seed_event import SeedEvent
from app.models.sys_user import SysUser
from app.schemas.seed_card import SeedCardCreate, SeedEventIn
from app.utils.qrcode import generate_qr_data_uri
from app.utils.slug import generate_unique_slug


def _scope(current_user: SysUser) -> int | None:
    if current_user.role == "merchant":
        return current_user.merchant_id
    return None


async def _slug_exists(db: AsyncSession, slug: str) -> bool:
    stmt = select(func.count()).select_from(SeedCard).where(SeedCard.slug == slug)
    return (await db.execute(stmt)).scalar_one() > 0


async def create_seed_card(
    db: AsyncSession, data: SeedCardCreate, current_user: SysUser
) -> SeedCard:
    """创建种草卡：生成唯一 slug 与二维码（指向 /c/{slug}）。"""
    scope = _scope(current_user)
    # 商家角色只能为自己的商家建卡
    merchant_id = data.merchant_id
    if scope is not None:
        merchant_id = scope

    slug = await generate_unique_slug(lambda s: _slug_exists(db, s))
    landing_url = f"{PUBLIC_BASE_URL.rstrip('/')}/c/{slug}"
    qr_code = generate_qr_data_uri(landing_url)

    card = SeedCard(
        merchant_id=merchant_id,
        name=data.name,
        slug=slug,
        type=data.type,
        target_type=data.target_type,
        target_url=data.target_url,
        nfc_id=data.nfc_id,
        qr_code=qr_code,
        status="active",
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def get_seed_card(
    db: AsyncSession, card_id: int, current_user: SysUser
) -> SeedCard | None:
    """获取种草卡详情（校验作用域）。"""
    scope = _scope(current_user)
    result = await db.execute(
        select(SeedCard).where(
            SeedCard.id == card_id, SeedCard.status == "active"
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        return None
    if scope is not None and card.merchant_id != scope:
        return None
    return card


async def get_card_by_slug(db: AsyncSession, slug: str) -> SeedCard | None:
    """按 slug 获取公开卡片（H5 落地页用，无需登录，仅返回 active）。"""
    result = await db.execute(
        select(SeedCard).where(
            SeedCard.slug == slug, SeedCard.status == "active"
        )
    )
    return result.scalar_one_or_none()


async def list_seed_cards(
    db: AsyncSession,
    page: int,
    size: int,
    merchant_id: int | None,
    current_user: SysUser,
) -> tuple[list[SeedCard], int]:
    """分页列出种草卡（校验作用域）。"""
    scope = _scope(current_user)
    base = select(SeedCard).where(SeedCard.status == "active")
    if scope is not None:
        base = base.where(SeedCard.merchant_id == scope)
    if merchant_id is not None:
        base = base.where(SeedCard.merchant_id == merchant_id)

    total = (
        await db.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await db.execute(
            base.order_by(SeedCard.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    ).scalars().all()
    return list(rows), total


async def record_event(
    db: AsyncSession, data: SeedEventIn, device: str, referer: str
) -> SeedEvent:
    """写入一条互动事件（只追加，不删除）。"""
    event = SeedEvent(
        card_id=data.card_id,
        event_type=data.event_type,
        device=device,
        referer=referer,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
