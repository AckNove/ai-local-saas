"""Mock 地图 Provider：返回固定 POI，无需腾讯地图 Key。"""
from __future__ import annotations

from app.services.map.base import MapProvider

_FIXED_POI = {
    "poi_id": "mock_poi_1001",
    "poi_name": "示例门店（Mock POI）",
    "address": "北京市朝阳区示例路 1 号",
    "lng": 116.397428,
    "lat": 39.90923,
}


class MockMapProvider(MapProvider):
    """模拟腾讯/微信地图：固定返回同一 POI。"""

    async def resolve_poi(self, poi_id: str | None) -> dict:
        return dict(_FIXED_POI)

    async def search_poi(self, keyword: str) -> list[dict]:
        return [dict(_FIXED_POI)]
