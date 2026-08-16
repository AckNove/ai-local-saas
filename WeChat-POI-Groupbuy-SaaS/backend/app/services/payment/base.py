"""支付 Provider 抽象。

统一接口：create_prepay（下单获取支付参数）、refund（退款）。
Mock / Real 实现可互换，业务代码仅依赖本抽象。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.order import Order


class PaymentProvider(ABC):
    """支付渠道抽象基类。"""

    @abstractmethod
    async def create_prepay(self, order: Order) -> dict:
        """创建预支付，返回前端拉起支付所需的 pay_params 字典。"""

    @abstractmethod
    async def refund(self, order: Order, amount: int) -> str:
        """发起退款，返回渠道退款单号 channel_refund_id。"""
