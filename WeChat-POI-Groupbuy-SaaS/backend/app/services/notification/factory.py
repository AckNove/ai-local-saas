"""通知 Provider 工厂：按环境变量返回实现。"""
from __future__ import annotations

from app.core.config import settings
from app.services.notification.base import NotificationProvider
from app.services.notification.mock import MockNotificationProvider
from app.services.notification.wechat import RealWechatNotifyProvider


def get_notification_provider() -> NotificationProvider:
    """WECHAT_NOTIFY_PROVIDER=mock|real。"""
    if settings.WECHAT_NOTIFY_PROVIDER == "real":
        return RealWechatNotifyProvider()
    return MockNotificationProvider()
