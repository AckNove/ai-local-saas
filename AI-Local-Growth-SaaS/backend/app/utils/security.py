"""密码哈希与 JWT 签发 / 校验。

使用 bcrypt 做慢哈希（直接调用，规避 passlib 兼容告警），
使用 PyJWT 签发无状态 Bearer Token。
"""
from __future__ import annotations

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from config import JWT_EXPIRE_MINUTES, JWT_SECRET


def hash_password(password: str) -> str:
    """bcrypt 哈希明文密码，返回 str。"""
    pwd_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_id: int,
    role: str,
    merchant_id: int | None = None,
) -> str:
    """签发 JWT。payload 携带 sub / role / mid（merchant_id），并设置过期时间。"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "mid": merchant_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """解码并校验 JWT，失败时抛出 jwt.PyJWTError。"""
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
