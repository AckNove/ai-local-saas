"""二维码生成（segno）。

生成指向落地页 /c/{slug} 的二维码，返回 PNG 字节或 data URI。
"""
from __future__ import annotations

import base64
import io

import segno


def generate_qr_png(content: str, scale: int = 8, border: int = 2) -> bytes:
    """生成二维码 PNG 字节。"""
    qr = segno.make(content, error="m")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=border)
    return buf.getvalue()


def generate_qr_data_uri(content: str, scale: int = 8, border: int = 2) -> str:
    """生成二维码 PNG 的 data URI（可直接存入字段或用于 <img src>）。"""
    png_bytes = generate_qr_png(content, scale=scale, border=border)
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"
