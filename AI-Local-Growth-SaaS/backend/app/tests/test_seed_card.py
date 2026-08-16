"""种草卡测试：创建、查询、列表、二维码、公开事件上报、越权作用域。"""
from __future__ import annotations

import app.database as database_module
from sqlalchemy import func, select

from app.models.seed_card import SeedCard
from app.models.seed_event import SeedEvent


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_merchant(client, token, name="商户"):
    return (
        await client.post(
            "/api/merchant/create",
            headers=_auth(token),
            json={"name": name, "industry": "零售", "stores": []},
        )
    ).json()["data"]["id"]


async def _create_card(client, token, merchant_id, name="开业卡"):
    return await client.post(
        "/api/seed-card/create",
        headers=_auth(token),
        json={
            "merchant_id": merchant_id,
            "name": name,
            "type": "二维码",
            "target_type": "video",
            "target_url": "https://example.com/v",
        },
    )


async def test_create_seed_card(client, admin_token):
    mid = await _create_merchant(client, admin_token)
    r = await _create_card(client, admin_token, mid, "开业卡")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["slug"]
    assert d["qr_code"].startswith("data:image/png;base64,")
    assert d["status"] == "active"


async def test_get_seed_card(client, admin_token):
    mid = await _create_merchant(client, admin_token)
    cid = (await _create_card(client, admin_token, mid)).json()["data"]["id"]
    r = await client.get(f"/api/seed-card/{cid}", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["data"]["id"] == cid


async def test_list_seed_card(client, admin_token):
    mid = await _create_merchant(client, admin_token)
    await _create_card(client, admin_token, mid)
    r = await client.get("/api/seed-card/list", headers=_auth(admin_token))
    assert r.status_code == 200
    d = r.json()["data"]
    assert "items" in d and "total" in d
    assert d["total"] >= 1


async def test_qrcode_png(client, admin_token):
    mid = await _create_merchant(client, admin_token)
    cid = (await _create_card(client, admin_token, mid)).json()["data"]["id"]
    r = await client.get(
        f"/api/seed-card/{cid}/qrcode", headers=_auth(admin_token)
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 0


async def test_public_event_records(client, admin_token):
    mid = await _create_merchant(client, admin_token)
    cid = (await _create_card(client, admin_token, mid)).json()["data"]["id"]
    # 公开上报（无需 token）
    r = await client.post(
        "/api/seed-card/event",
        json={
            "card_id": cid,
            "event_type": "scan",
            "device": "mobile",
            "referer": "https://example.com",
        },
    )
    assert r.status_code == 200
    assert r.json()["data"]["ok"] is True
    # 事件已落库
    async with database_module.async_session_factory() as db:
        n = (
            await db.execute(
                select(func.count())
                .select_from(SeedEvent)
                .where(SeedEvent.card_id == cid)
            )
        ).scalar_one()
    assert n == 1


async def test_event_invalid_type_422(client):
    r = await client.post(
        "/api/seed-card/event",
        json={"card_id": 999, "event_type": "hack"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == 422


async def test_merchant_card_scope(client, admin_token, register_user, make_token):
    # admin 建两个商家
    m1 = await _create_merchant(client, admin_token, "卡商1")
    m2 = await _create_merchant(client, admin_token, "卡商2")
    c1 = (await _create_card(client, admin_token, m1, "卡1")).json()["data"]["id"]
    await _create_card(client, admin_token, m2, "卡2")
    # 商家用户归属 m1
    u = await register_user("merch_card", role="merchant", merchant_id=m1)
    tok = make_token(u)
    h = _auth(tok)
    # 只能看到自己的卡
    r = await client.get("/api/seed-card/list", headers=h)
    ids = [c["id"] for c in r.json()["data"]["items"]]
    assert c1 in ids
    assert len(ids) == 1
    # 看不到他人卡详情
    r2 = await client.get(f"/api/seed-card/{c1}", headers=h)
    assert r2.status_code == 200
