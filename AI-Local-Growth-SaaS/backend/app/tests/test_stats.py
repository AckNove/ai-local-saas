"""统计测试：聚合正确性、merchant 作用域、鉴权。"""
from __future__ import annotations

import app.database as database_module
from sqlalchemy import func, select

from app.models.seed_event import SeedEvent


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _setup_one_merchant_with_card_and_event(client, admin_token, name="商户"):
    mid = (
        await client.post(
            "/api/merchant/create",
            headers=_auth(admin_token),
            json={"name": name, "stores": []},
        )
    ).json()["data"]["id"]
    cid = (
        await client.post(
            "/api/seed-card/create",
            headers=_auth(admin_token),
            json={
                "merchant_id": mid,
                "name": "卡",
                "type": "二维码",
                "target_type": "video",
                "target_url": "https://example.com",
            },
        )
    ).json()["data"]["id"]
    await client.post(
        "/api/seed-card/event",
        json={"card_id": cid, "event_type": "scan", "device": "mobile"},
    )
    return mid, cid


async def test_overview_aggregation(client, admin_token):
    before = (
        await client.get("/api/stats/overview", headers=_auth(admin_token))
    ).json()["data"]
    m0, s0 = before["merchant_count"], before["scan_total"]

    await _setup_one_merchant_with_card_and_event(client, admin_token, "聚合商户")

    r = await client.get("/api/stats/overview", headers=_auth(admin_token))
    d = r.json()["data"]
    # 结构完整
    for k in (
        "merchant_count",
        "store_count",
        "card_count",
        "scan_total",
        "click_total",
        "share_total",
        "comment_total",
        "recent_events",
    ):
        assert k in d
    assert d["merchant_count"] == m0 + 1
    assert d["scan_total"] == s0 + 1
    assert any(e["event_type"] == "scan" for e in d["recent_events"])
    # 直接查库核对
    async with database_module.async_session_factory() as db:
        scan_n = (
            await db.execute(
                select(func.count())
                .select_from(SeedEvent)
                .where(SeedEvent.event_type == "scan")
            )
        ).scalar_one()
    assert scan_n == s0 + 1


async def test_overview_merchant_scope(client, admin_token, register_user, make_token):
    m1, _ = await _setup_one_merchant_with_card_and_event(client, admin_token, "S1")
    await _setup_one_merchant_with_card_and_event(client, admin_token, "S2")

    u = await register_user("merch_scope", role="merchant", merchant_id=m1)
    tok = make_token(u)
    r = await client.get("/api/stats/overview", headers=_auth(tok))
    d = r.json()["data"]
    # 仅能看到自己范围内的数据
    assert d["merchant_count"] == 1
    assert d["card_count"] == 1


async def test_overview_requires_auth(client):
    r = await client.get("/api/stats/overview")
    assert r.status_code == 401
    assert r.json()["code"] == 401
