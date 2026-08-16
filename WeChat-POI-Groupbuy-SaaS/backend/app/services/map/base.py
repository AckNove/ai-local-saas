"""地图 POI Provider 抽象：门店 POI 解析/检索。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class MapProvider(ABC):
    """地图 POI 抽象基类。"""

    @abstractmethod
    async def resolve_poi(self, poi_id: str | None) -> dict:
        """解析 POI，返回 {poi_id, poi_name, address, lng, lat}。"""

    @abstractmethod
    async def search_poi(self, keyword: str) -> list[dict]:
        """按关键词检索 POI 列表。"""
