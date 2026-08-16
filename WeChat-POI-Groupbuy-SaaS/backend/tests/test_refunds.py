"""退款流程测试：申请退款（库存回滚 + 状态机）与金额/权限校验。

补充现有测试未覆盖的关键路径：refunds 接口（app/api/v1/refunds.py）。
依赖 test_order_flow 中的下单→支付闭环（此处内联最小实现，避免跨文件耦合）。
"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def _consumer_token(api):
    resp = await api.client.post("/api/v1/auth/wx-login", json={"code": "refund_consumer"})
    return resp.json()["data"]["token"]


async def _create_and_pay(api, fulfillment_type="dine_in"):
    token = await _consumer_token(api)
    r = await api.client.post(
        "/api/v1/orders",
        json={
            "package_id": api.ids["package_id"],
            "store_id": api.ids["store_id"],
            "quantity": 1,
            "fulfillment_type": fulfillment_type,
        },
        headers=auth_header(token),
    )
    assert r.status_code == 200, r.text
    order_no = r.json()["data"]["order"]["order_no"]
    await api.client.post(f"/api/v1/orders/{order_no}/pay-notify")
    return order_no, token


async def test_apply_refund_happy_path_and_stock_rollback(api):
    order_no, token = await _create_and_pay(api)
    total = 8000  # 套餐 group_price=8000, quantity=1

    resp = await api.client.post(
        "/api/v1/refunds",
        json={"order_no": order_no, "amount": total, "reason": "不想要了"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["status"] == "succeeded"
    assert body["data"]["amount"] == total
    refund_no = body["data"]["refund_no"]
    assert refund_no.startswith("RF")

    # 订单状态 -> refunded
    detail = await api.client.get(
        f"/api/v1/orders/{order_no}", headers=auth_header(token)
    )
    assert detail.json()["data"]["status"] == "refunded"

    # 库存回滚：sold_count 回到 0
    token_m = await login(api.client, "merchant", "merchant123")
    pkg = await api.client.get(
        f"/api/v1/catalog/packages/{api.ids['package_id']}", headers=auth_header(token_m)
    )
    assert pkg.json()["data"]["sold_count"] == 0

    # 重复退款被拒（已存在退款单）-> REFUND_FAILED(5002)
    dup = await api.client.post(
        "/api/v1/refunds",
        json={"order_no": order_no, "amount": total},
        headers=auth_header(token),
    )
    assert dup.json()["code"] == 5002  # REFUND_FAILED

    # 退款单查询
    q = await api.client.get(
        f"/api/v1/refunds/{refund_no}", headers=auth_header(token)
    )
    assert q.json()["data"]["refund_no"] == refund_no


async def test_refund_rejects_over_amount_and_wrong_state(api):
    order_no, token = await _create_and_pay(api)

    # 退款金额超过订单总额 -> REFUND_FAILED(5002)
    over = await api.client.post(
        "/api/v1/refunds",
        json={"order_no": order_no, "amount": 999999},
        headers=auth_header(token),
    )
    assert over.json()["code"] == 5002

    # 未支付订单不可退款（用新下单不支付）
    token2 = await _consumer_token(api)
    r = await api.client.post(
        "/api/v1/orders",
        json={
            "package_id": api.ids["package_id"],
            "store_id": api.ids["store_id"],
            "quantity": 1,
        },
        headers=auth_header(token2),
    )
    pending_no = r.json()["data"]["order"]["order_no"]
    pending_refund = await api.client.post(
        "/api/v1/refunds",
        json={"order_no": pending_no, "amount": 8000},
        headers=auth_header(token2),
    )
    assert pending_refund.json()["code"] == 3002  # ORDER_STATUS_INVALID
