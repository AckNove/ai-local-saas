"""数据看板测试：指标公式断言（GMV / 核销率 / 内容引流占比）。"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def _consumer_token(api):
    return (await api.client.post(
        "/api/v1/auth/wx-login", json={"code": "dashboard_consumer"}
    )).json()["data"]["token"]


async def _order_and_verify(api, channel_binding_id=None):
    token = await _consumer_token(api)
    body = {"package_id": api.ids["package_id"], "store_id": api.ids["store_id"], "quantity": 1}
    if channel_binding_id:
        body["channel_binding_id"] = channel_binding_id
    r = await api.client.post("/api/v1/orders", json=body, headers=auth_header(token))
    order_no = r.json()["data"]["order"]["order_no"]
    p = await api.client.post(f"/api/v1/orders/{order_no}/pay-notify")
    code = p.json()["data"]["verification_codes"][0]["code"]
    token_v = await login(api.client, "verifier", "verifier123")
    await api.client.post("/api/v1/verify", json={"code": code}, headers=auth_header(token_v))
    return p.json()["data"]


async def test_merchant_metrics(api):
    data = await _order_and_verify(api)
    token_m = await login(api.client, "merchant", "merchant123")
    m = await api.client.get("/api/v1/dashboard/metrics", headers=auth_header(token_m))
    assert m.json()["code"] == 0
    metrics = m.json()["data"]
    assert metrics["gmv"] == data["total_amount"]      # GMV = 已支付总额
    assert metrics["paid_orders"] == 1
    assert metrics["sales_volume"] == 1
    assert metrics["verified_count"] == 1
    assert metrics["verify_rate"] == 1.0                # 核销率 = 已核销/需核销


async def test_platform_metrics_aggregate(api):
    await _order_and_verify(api)
    token_p = await login(api.client, "admin", "admin123")
    m = await api.client.get("/api/v1/dashboard/metrics", headers=auth_header(token_p))
    assert m.json()["code"] == 0
    assert m.json()["data"]["gmv"] == 8000
    assert m.json()["data"]["paid_orders"] == 1


async def test_video_channel_rate(api):
    token_m = await login(api.client, "merchant", "merchant123")
    b = await api.client.post(
        "/api/v1/fulfillment/video-bindings",
        json={"store_id": api.ids["store_id"], "video_account_id": "va_dash", "poi_id": "mock_poi_1001"},
        headers=auth_header(token_m),
    )
    binding_id = b.json()["data"]["id"]
    await _order_and_verify(api, channel_binding_id=binding_id)

    m = await api.client.get("/api/v1/dashboard/metrics", headers=auth_header(token_m))
    metrics = m.json()["data"]
    assert metrics["video_channel_rate"] == 1.0
    assert metrics["paid_orders"] == 1
