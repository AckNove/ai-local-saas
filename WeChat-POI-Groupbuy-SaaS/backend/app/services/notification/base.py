"""通知 Provider 抽象：备餐完成 / 预约提醒等。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class NotificationProvider(ABC):
    """通知渠道抽象基类。"""

    @abstractmethod
    async def notify(self, notify_type: str, payload: dict) -> bool:
        """发送通知，返回是否成功。notify_type 如 ready/pickup/reservation。"""
