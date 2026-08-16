"""Mock 通知 Provider：直接返回成功，不发真实订阅消息。"""
from __future__ import annotations

from app.services.notification.base import NotificationProvider


class MockNotificationProvider(NotificationProvider):
    """模拟微信订阅消息：恒成功。"""

    async def notify(self, notify_type: str, payload: dict) -> bool:
        return True
