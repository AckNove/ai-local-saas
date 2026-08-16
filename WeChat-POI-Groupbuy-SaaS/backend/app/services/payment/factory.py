"""支付 Provider 工厂：按环境变量返回实现。"""
from __future__ import annotations

from app.core.config import settings
from app.services.payment.base import PaymentProvider
from app.services.payment.mock import MockPaymentProvider
from app.services.payment.wechat import RealWechatPayProvider


def get_payment_provider() -> PaymentProvider:
    """WECHAT_PAY_PROVIDER=mock|real。"""
    if settings.WECHAT_PAY_PROVIDER == "real":
        return RealWechatPayProvider()
    return MockPaymentProvider()
