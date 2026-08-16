"""履约测试：预约订座时段库存（6001 满额 / 取消回收）+ 自提状态机。"""
from __future__ import annotations

from app.core.config import settings

from tests.conftest import auth_header, login


async def _consumer_token(api):
    return (await api.client.post(
        "/api/v1/auth/wx-login", json={"code": "fulfillment_consumer"}
    )).json()["data"]["token"]


async def test_reservation_slot_full_and_recycle(api):
    settings.SLOT_CAPACITY = 1  # 该时段仅可约 1 桌
    token = await _consumer_token(api)
    base = {
        "store_id": api.ids["store_id"],
        "reserve_date": "2030-01-01",
        "time_slot": "18:00-19:00",
        "party_size": 2,
    }
    r1 = await api.client.post("/api/v1/fulfillment/reservations", json=base, headers=auth_header(token))
    assert r1.json()["code"] == 0
    rid = r1.json()["data"]["id"]

    # 第二桌应满额
    r2 = await api.client.post("/api/v1/fulfillment/reservations", json=base, headers=auth_header(token))
    assert r2.json()["code"] == 6001

    # 取消回收库存
    token_m = await login(api.client, "manager", "manager123")
    c = await api.client.patch(
        f"/api/v1/fulfillment/reservations/{rid}",
        json={"status": "cancelled"},
        headers=auth_header(token_m),
    )
    assert c.json()["data"]["status"] == "cancelled"

    # 取消后该时段可再约
    r3 = await api.client.post("/api/v1/fulfillment/reservations", json=base, headers=auth_header(token))
    assert r3.json()["code"] == 0
    settings.SLOT_CAPACITY = 20


async def test_reservation_confirm_arrive(api):
    token = await _consumer_token(api)
    base = {
        "store_id": api.ids["store_id"],
        "reserve_date": "2030-02-02",
        "time_slot": "19:00-20:00",
        "party_size": 4,
    }
    rid = (await api.client.post(
        "/api/v1/fulfillment/reservations", json=base, headers=auth_header(token)
    )).json()["data"]["id"]
    token_m = await login(api.client, "manager", "manager123")
    conf = await api.client.patch(
        f"/api/v1/fulfillment/reservations/{rid}",
        json={"status": "confirmed"},
        headers=auth_header(token_m),
    )
    assert conf.json()["data"]["status"] == "confirmed"
    arr = await api.client.patch(
        f"/api/v1/fulfillment/reservations/{rid}",
        json={"status": "arrived"},
        headers=auth_header(token_m),
    )
    assert arr.json()["data"]["status"] == "arrived"


async def test_reservation_illegal_transition(api):
    token = await _consumer_token(api)
    rid = (await api.client.post(
        "/api/v1/fulfillment/reservations",
        json={"store_id": api.ids["store_id"], "reserve_date": "2030-03-03",
              "time_slot": "20:00-21:00", "party_size": 1},
        headers=auth_header(token),
    )).json()["data"]["id"]
    token_m = await login(api.client, "manager", "manager123")
    # pending 直接 arrived 非法
    bad = await api.client.patch(
        f"/api/v1/fulfillment/reservations/{rid}",
        json={"status": "arrived"},
        headers=auth_header(token_m),
    )
    assert bad.json()["code"] == 6003
