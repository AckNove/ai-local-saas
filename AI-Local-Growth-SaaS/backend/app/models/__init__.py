"""数据模型聚合导入，便于 `from app.models import *` 与建表。"""
from __future__ import annotations

from app.models.ai_task import AITask
from app.models.merchant_info import MerchantInfo
from app.models.seed_card import SeedCard
from app.models.seed_event import SeedEvent
from app.models.store_info import StoreInfo
from app.models.sys_user import SysUser
from app.models.video_content import VideoContent

__all__ = [
    "SysUser",
    "MerchantInfo",
    "StoreInfo",
    "SeedCard",
    "SeedEvent",
    "VideoContent",
    "AITask",
]
