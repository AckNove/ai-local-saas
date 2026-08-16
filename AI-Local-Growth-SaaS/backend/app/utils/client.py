"""客户端信息解析：设备类型、来源页。"""
from __future__ import annotations


def parse_device(user_agent: str | None) -> str:
    """根据 User-Agent 粗略判断设备类型：mobile / tablet / desktop。"""
    ua = (user_agent or "").lower()
    if "iphone" in ua or "android" in ua and "mobile" in ua:
        return "mobile"
    if "iphone" in ua or "android" in ua:
        return "mobile"
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    return "desktop"


def parse_referer(referer: str | None) -> str:
    """返回来源页字符串（截断避免过长）。"""
    if not referer:
        return ""
    return referer[:512]
