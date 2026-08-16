"""全局配置：从环境变量加载，禁止硬编码。

所有配置项均可通过 .env 或系统环境变量覆盖。默认值保证本地零依赖即可运行。
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env（若存在）。backend/ 运行时 cwd 通常为 backend/，
# 同时向上查找一级，兼容在仓库根目录启动的情况。
load_dotenv()
ROOT_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(ROOT_ENV):
    load_dotenv(ROOT_ENV, override=False)


def _as_int(value: str | None, default: int) -> int:
    """将环境变量安全转为 int，失败时回退默认值。"""
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _as_list(value: str | None, default: list[str]) -> list[str]:
    """将逗号分隔的字符串转为列表，过滤空白。"""
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


# --- 数据库 ---
# 默认 SQLite（零依赖）；生产经 DATABASE_URL 切 PostgreSQL。
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

# --- AI / LLM ---
# 可选值：mock（默认，离线兜底） / openai / deepseek
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock").lower()
# 通用 API Key（OpenAI 等 OpenAI 兼容服务使用）
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
# 通用 Base URL（OpenAI 兼容服务可指定；DeepSeek/OpenAI 有内置默认值）
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
# DeepSeek 专用 Key（不硬编码；缺省回退到 LLM_API_KEY）
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

# --- 鉴权 ---
JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_EXPIRE_MINUTES: int = _as_int(os.getenv("JWT_EXPIRE_MINUTES"), 1440)

# --- CORS ---
CORS_ORIGINS: list[str] = _as_list(os.getenv("CORS_ORIGINS"), ["*"])

# --- 公开访问基址（用于生成二维码落地页绝对 URL）---
PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

# --- 服务端口（仅用于提示与脚本）---
APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT: int = _as_int(os.getenv("APP_PORT"), 8000)
