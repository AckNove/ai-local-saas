"""交易流程测试：下单 → Mock 支付 → 核销码生成 → 幂等回调。"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def _consumer_token(api):
    resp = await api.client.post("/api/v1/auth/wx-login", json={"code": "order_flow_consumer"})
    return resp.json()["data"]["token"]


async def _create_and_pay(api, fulfillment_type="dine_in", channel_binding_id=None):
    token = await _consumer_token(api)
    body = {
        "package_id": api.ids["package_id"],
        "store_id": api.ids["store_id"],
        "quantity": 1,
        "fulfillment_type": fulfillment_type,
    }
    if channel_binding_id is not None:
        body["channel_binding_id"] = channel_binding_id
    r = await api.client.post("/api/v1/orders", json=body, headers=auth_header(token))
    assert r.status_code == 200, r.text
    order_no = r.json()["data"]["order"]["order_no"]
    assert r.json()["data"]["pay_params"]["prepay_id"]

    p = await api.client.post(f"/api/v1/orders/{order_no}/pay-notify")
    assert p.status_code == 200, p.text
    return order_no, p.json()["data"]


async def test_order_flow_generate_codes(api):
    order_no, data = await _create_and_pay(api)
    assert data["status"] == "paid"
    assert len(data["verification_codes"]) == 1
    code = data["verification_codes"][0]["code"]

    # 幂等：重复回调不重复生成核销码
    p2 = await api.client.post(f"/api/v1/orders/{order_no}/pay-notify")
    assert len(p2.json()["data"]["verification_codes"]) == 1

    # 库存扣减：商户查看套餐 sold_count == 1
    token_m = await login(api.client, "merchant", "merchant123")
    pkg = await api.client.get(
        f"/api/v1/catalog/packages/{api.ids['package_id']}", headers=auth_header(token_m)
    )
    assert pkg.json()["data"]["sold_count"] == 1


async def test_self_pickup_flow(api):
    order_no, data = await _create_and_pay(api, fulfillment_type="self_pickup")
    assert data["status"] == "paid"
    assert data["pickup_status"] == "preparing"

    # 备餐完成
    token_m = await login(api.client, "manager", "manager123")
    up = await api.client.patch(
        f"/api/v1/orders/{order_no}/pickup",
        json={"status": "ready"},
        headers=auth_header(token_m),
    )
    assert up.json()["data"]["pickup_status"] == "ready"

    # 核销 -> 取餐
    token_v = await login(api.client, "verifier", "verifier123")
    code = up.json()["data"]["verification_codes"][0]["code"]
    v = await api.client.post(
        "/api/v1/verify", json={"code": code}, headers=auth_header(token_v)
    )
    assert v.json()["code"] == 0
    detail = await api.client.get(
        f"/api/v1/orders/{order_no}", headers=auth_header(token_m)
    )
    assert detail.json()["data"]["pickup_status"] == "picked_up"
    assert detail.json()["data"]["status"] == "fulfilled"


async def test_channel_binding_attribution(api):
    token_m = await login(api.client, "merchant", "merchant123")
    b = await api.client.post(
        "/api/v1/fulfillment/video-bindings",
        json={"store_id": api.ids["store_id"], "video_account_id": "va_123", "poi_id": "mock_poi_1001"},
        headers=auth_header(token_m),
    )
    assert b.json()["code"] == 0
    assert "groupbuy_link" in b.json()["data"]
    binding_id = b.json()["data"]["id"]

    order_no, data = await _create_and_pay(api, channel_binding_id=binding_id)
    detail = await api.client.get(
        f"/api/v1/orders/{order_no}", headers=auth_header(token_m)
    )
    assert detail.json()["data"]["source"] == "video_channel"
    assert detail.json()["data"]["channel_binding_id"] == binding_id
