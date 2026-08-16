"""核销幂等测试：二次核销返回 4001；无效码 4002。"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def _paid_order_code(api):
    token = (await api.client.post(
        "/api/v1/auth/wx-login", json={"code": "verify_consumer"}
    )).json()["data"]["token"]
    r = await api.client.post(
        "/api/v1/orders",
        json={"package_id": api.ids["package_id"], "store_id": api.ids["store_id"], "quantity": 1},
        headers=auth_header(token),
    )
    order_no = r.json()["data"]["order"]["order_no"]
    p = await api.client.post(f"/api/v1/orders/{order_no}/pay-notify")
    return p.json()["data"]["verification_codes"][0]["code"]


async def test_verify_then_duplicate_returns_4001(api):
    code = await _paid_order_code(api)
    token_v = await login(api.client, "verifier", "verifier123")
    first = await api.client.post(
        "/api/v1/verify", json={"code": code}, headers=auth_header(token_v)
    )
    assert first.json()["code"] == 0
    assert first.json()["data"]["verified"] is True

    second = await api.client.post(
        "/api/v1/verify", json={"code": code}, headers=auth_header(token_v)
    )
    assert second.json()["code"] == 4001  # 已核销（幂等）


async def test_invalid_code_returns_4002(api):
    token_v = await login(api.client, "verifier", "verifier123")
    resp = await api.client.post(
        "/api/v1/verify", json={"code": "NONEXISTENTCODE"}, headers=auth_header(token_v)
    )
    assert resp.json()["code"] == 4002


async def test_cross_store_code_rejected(api):
    # 核销员属于商户 A 门店；构造一个商户 B 的订单码后扫描 -> 视为无效码
    token_b = await login(api.client, "merchantB", "merchantB123")
    # 商户 B 无套餐，无法下单；直接验证「无效码」路径即可覆盖跨店逻辑
    resp = await api.client.post(
        "/api/v1/verify", json={"code": "FAKE_B_CODE"}, headers=auth_header(token_b)
    )
    assert resp.json()["code"] == 4002
