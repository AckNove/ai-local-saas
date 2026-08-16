"""真实微信支付 Provider（JSAPI）。

凭证就绪（WECHAT_PAY_PROVIDER=real 且 mchid/api_key 配置）后启用。
下列为真实对接骨架：统一下单、回调验签、退款。未配置凭证时方法会抛出
BizError(CHANNEL_ERROR)，业务不阻塞。
"""
from __future__ import annotations

import hashlib
import time
import uuid

import httpx

from app.core.config import settings
from app.core.errors import BizError, ErrorCode
from app.models.order import Order
from app.services.payment.base import PaymentProvider


class RealWechatPayProvider(PaymentProvider):
    """微信支付 v3（JSAPI）真实实现骨架。"""

    def _ensure_config(self) -> None:
        if not (settings.WXPAY_MCH_ID and settings.WXPAY_API_KEY):
            raise BizError(
                ErrorCode.CHANNEL_ERROR,
                "微信支付凭证未配置（WXPAY_MCH_ID / WXPAY_API_KEY）",
            )

    async def create_prepay(self, order: Order) -> dict:
        self._ensure_config()
        # 真实流程：调用微信统一下单 API，返回 JSAPI 拉起参数（prepay_id 等）。
        # 此处仅占位，凭证到位后填充 httpx 请求与签名。
        url = "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi"
        # payload = {...}
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(url, json=payload, headers=...)
        # return resp.json()
        raise BizError(ErrorCode.CHANNEL_ERROR, "RealWechatPayProvider 未实现（占位）")

    async def refund(self, order: Order, amount: int) -> str:
        self._ensure_config()
        # 真实流程：调用微信退款 API，返回 channel_refund_id。
        raise BizError(ErrorCode.CHANNEL_ERROR, "RealWechatPayProvider 未实现（占位）")
