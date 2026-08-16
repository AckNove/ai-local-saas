"""地图 Provider 工厂：按环境变量返回实现。"""
from __future__ import annotations

from app.core.config import settings
from app.services.map.base import MapProvider
from app.services.map.mock import MockMapProvider
from app.services.map.tencent import RealTencentMapProvider


def get_map_provider() -> MapProvider:
    """MAP_POI_PROVIDER=mock|real。"""
    if settings.MAP_POI_PROVIDER == "real":
        return RealTencentMapProvider()
    return MockMapProvider()
