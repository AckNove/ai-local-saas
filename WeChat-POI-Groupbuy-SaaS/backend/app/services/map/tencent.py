"""真实腾讯地图 Provider 骨架（凭证就绪后启用）。"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.errors import BizError, ErrorCode
from app.services.map.base import MapProvider


class RealTencentMapProvider(MapProvider):
    """腾讯地图 POI 检索/解析骨架。"""

    def _ensure_config(self) -> None:
        if not settings.MAP_KEY:
            raise BizError(ErrorCode.CHANNEL_ERROR, "地图 Key 未配置（MAP_KEY）")

    async def resolve_poi(self, poi_id: str | None) -> dict:
        self._ensure_config()
        # 真实流程：调用腾讯地图 POI 详情 API。
        raise BizError(ErrorCode.CHANNEL_ERROR, "RealTencentMapProvider 未实现（占位）")

    async def search_poi(self, keyword: str) -> list[dict]:
        self._ensure_config()
        raise BizError(ErrorCode.CHANNEL_ERROR, "RealTencentMapProvider 未实现（占位）")
