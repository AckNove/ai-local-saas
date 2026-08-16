"""真实微信订阅消息 Provider 骨架。"""
from __future__ import annotations

from app.core.errors import BizError, ErrorCode
from app.services.notification.base import NotificationProvider


class RealWechatNotifyProvider(NotificationProvider):
    """微信订阅消息真实实现骨架（凭证就绪后启用）。"""

    async def notify(self, notify_type: str, payload: dict) -> bool:
        raise BizError(ErrorCode.CHANNEL_ERROR, "RealWechatNotifyProvider 未实现（占位）")
