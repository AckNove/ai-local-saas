"""密码哈希与 JWT 签发 / 校验。

使用 bcrypt 做慢哈希（直接调用，规避 passlib 兼容告警），
使用 PyJWT 签发无状态 Bearer Token。JWT 载荷遵循架构第 7 节：
    { sub, typ, role, merchant_id, store_id, exp }
"""
from __future__ import annotations

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def hash_password(password: str) -> str:
    """bcrypt 哈希明文密码，返回 str。"""
    pwd_bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    sub: int,
    typ: str,
    role: str,
    merchant_id: int | None = None,
    store_id: int | None = None,
    expire_minutes: int | None = None,
) -> str:
    """签发 JWT。payload 携带 sub / typ / role / merchant_id / store_id / exp。"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes or settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(sub),
        "typ": typ,
        "role": role,
        "merchant_id": merchant_id,
        "store_id": store_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """解码并校验 JWT，失败时抛出 jwt.PyJWTError。"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
