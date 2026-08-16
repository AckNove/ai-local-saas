"""种草卡路由：CRUD、二维码、事件上报、公开落地页数据。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from config import PUBLIC_BASE_URL
from app.database import get_db
from app.models.seed_card import SeedCard
from app.models.sys_user import SysUser
from app.schemas.seed_card import SeedCardCreate, SeedCardOut, SeedCardSummary, SeedEventIn
from app.services import seed_card_service as svc
from app.utils.client import parse_device, parse_referer
from app.utils.qrcode import generate_qr_png
from app.utils.response import bad_request, not_found, ok, paginated
from app.utils.rbac import get_current_user

router = APIRouter(prefix="/api", tags=["seed-card"])

_ALLOWED_EVENTS = {"scan", "click", "share", "comment"}


def _to_out(card: SeedCard) -> SeedCardOut:
    return SeedCardOut(
        id=card.id,
        merchant_id=card.merchant_id,
        name=card.name,
        slug=card.slug,
        type=card.type,
        target_type=card.target_type,
        target_url=card.target_url,
        nfc_id=card.nfc_id,
        qr_code=card.qr_code,
        status=card.status,
        created_at=card.created_at,
    )


def _to_summary(card: SeedCard) -> SeedCardSummary:
    return SeedCardSummary(
        id=card.id,
        merchant_id=card.merchant_id,
        name=card.name,
        slug=card.slug,
        type=card.type,
        target_type=card.target_type,
        target_url=card.target_url,
        status=card.status,
        created_at=card.created_at,
    )


@router.post("/seed-card/create")
async def create_seed_card(
    body: SeedCardCreate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await svc.create_seed_card(db, body, current_user)
    return ok(_to_out(card).model_dump())


@router.get("/seed-card/list")
async def list_seed_cards(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    merchant_id: int | None = Query(None),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 注意：静态路由 /seed-card/list 必须声明在 /seed-card/{card_id} 之前，
    # 否则 "list" 会被路径参数 card_id 捕获。
    cards, total = await svc.list_seed_cards(db, page, size, merchant_id, current_user)
    items = [_to_summary(c).model_dump() for c in cards]
    return ok(paginated(items, total))


@router.get("/seed-card/{card_id}")
async def get_seed_card(
    card_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await svc.get_seed_card(db, card_id, current_user)
    if card is None:
        return not_found("种草卡不存在或无权限")
    return ok(_to_out(card).model_dump())


@router.get("/seed-card/{card_id}/qrcode")
async def get_qrcode(
    card_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """返回种草卡二维码 PNG（指向 /c/{slug}）。"""
    card = await svc.get_seed_card(db, card_id, current_user)
    if card is None:
        return not_found("种草卡不存在或无权限")
    landing_url = f"{PUBLIC_BASE_URL.rstrip('/')}/c/{card.slug}"
    png = generate_qr_png(landing_url)
    return Response(content=png, media_type="image/png")


@router.post("/seed-card/event")
async def create_event(
    body: SeedEventIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """公开事件上报（来自 H5，无需登录）。"""
    if body.event_type not in _ALLOWED_EVENTS:
        return bad_request("event_type 必须是 scan/click/share/comment 之一")
    # 校验卡片存在（按 id 查询 active 卡片）
    from sqlalchemy import select

    result = await db.execute(
        select(SeedCard).where(SeedCard.id == body.card_id, SeedCard.status == "active")
    )
    card = result.scalar_one_or_none()
    if card is None:
        return bad_request("种草卡不存在")

    device = body.device or parse_device(request.headers.get("user-agent"))
    referer = body.referer or parse_referer(request.headers.get("referer"))
    event = await svc.record_event(db, body, device, referer)
    return ok({"ok": True, "event_id": event.id})


@router.get("/seed-card/public/{slug}")
async def public_card(slug: str, db: AsyncSession = Depends(get_db)):
    """公开获取卡片信息（H5 落地页使用，无需登录）。"""
    card = await svc.get_card_by_slug(db, slug)
    if card is None:
        return not_found("种草卡不存在")
    # 附带商家行业/地址/电话/门店信息，供落地页展示，提升消费者信任
    industry = "本地生活"
    merchant_name = ""
    address = ""
    phone = ""
    from sqlalchemy import select

    from app.models.merchant_info import MerchantInfo
    from app.models.store_info import StoreInfo

    merchant = await db.scalar(
        select(MerchantInfo).where(MerchantInfo.id == card.merchant_id)
    )
    if merchant is not None:
        industry = merchant.industry or "本地生活"
        merchant_name = merchant.name
        address = merchant.address or ""
        phone = merchant.phone or ""

    # 门店信息（取第一个 active 门店，用于展示"到店"信息）
    store_name = ""
    store_location = ""
    store = await db.scalar(
        select(StoreInfo)
        .where(StoreInfo.merchant_id == card.merchant_id, StoreInfo.status == "active")
        .order_by(StoreInfo.id)
        .limit(1)
    )
    if store is not None:
        store_name = store.name
        store_location = store.location or ""

    return ok(
        {
            "id": card.id,
            "name": card.name,
            "target_url": card.target_url,
            "target_type": card.target_type,
            "type": card.type,
            "industry": industry,
            "merchant_name": merchant_name,
            "address": address,
            "phone": phone,
            "store_name": store_name,
            "store_location": store_location,
        }
    )


@router.get("/seed-card/public/{slug}/review")
async def public_review(slug: str, db: AsyncSession = Depends(get_db)):
    """公开获取 AI 好评文案（H5 落地页"复制好评"使用，无需登录）。

    返回多条拟真好评，供顾客一键复制后到视频号/小红书粘贴发布。
    使用 CommentAgent 生成（无 Key 时自动降级 mock 模板）。
    """
    card = await svc.get_card_by_slug(db, slug)
    if card is None:
        return not_found("种草卡不存在")

    from sqlalchemy import select

    from app.agents.comment import CommentAgent
    from app.agents.provider import get_provider
    from app.models.merchant_info import MerchantInfo

    merchant = await db.scalar(
        select(MerchantInfo).where(MerchantInfo.id == card.merchant_id)
    )
    industry = merchant.industry if merchant and merchant.industry else "本地生活"

    provider = get_provider()
    agent = CommentAgent(provider, db)
    result, _task_id = await agent.run(
        {
            "video": card.target_url or card.name,
            "industry": industry,
        }
    )
    comments = result.get("comments", [])
    return ok(
        {
            "card_id": card.id,
            "industry": industry,
            "comments": comments[:6],
        }
    )
