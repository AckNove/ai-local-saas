"""Mock 支付 Provider：离线恒成功，无需任何微信凭证。"""
from __future__ import annotations

import time
import uuid

from app.models.order import Order
from app.services.payment.base import PaymentProvider


class MockPaymentProvider(PaymentProvider):
    """模拟微信 JSAPI 支付：生成假 prepay_id，退款返回假渠道单号。"""

    async def create_prepay(self, order: Order) -> dict:
        prepay_id = "mock_prepay_" + uuid.uuid4().hex[:16]
        return {
            "prepay_id": prepay_id,
            "nonce_str": uuid.uuid4().hex[:8],
            "time_stamp": str(int(time.time())),
            "sign": "mock_sign",
            "order_no": order.order_no,
        }

    async def refund(self, order: Order, amount: int) -> str:
        return "mock_refund_" + uuid.uuid4().hex[:16]
