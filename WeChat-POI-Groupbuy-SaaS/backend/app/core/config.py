"""全局配置：基于 pydantic-settings 从环境变量加载，禁止硬编码。

所有配置项均可通过 .env 或系统环境变量覆盖。默认值保证本地零依赖即可运行。
Mock 开关控制微信支付 / 地图 POI / 通知三类外部能力，凭证到位改 `=real` 即生效。
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置。

    读取顺序（后者覆盖前者）：内置默认值 → 系统环境变量 → .env 文件。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- 数据库 ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # --- 鉴权 ---
    JWT_SECRET: str = "change-me"
    JWT_EXPIRE_MINUTES: int = 1440

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- 服务端口（避免与同机其他服务冲突，如旧项目占用 8000）---
    SERVER_PORT: int = 8000

    # --- Web 后台静态产物目录（单服务部署时由后端托管；留空自动取 ../web-admin/dist）---
    WEB_ADMIN_DIST: str = ""

    # --- 微信/地图/通知 Provider 开关（mock | real）---
    WECHAT_PAY_PROVIDER: str = "mock"
    MAP_POI_PROVIDER: str = "mock"
    WECHAT_NOTIFY_PROVIDER: str = "mock"

    # --- 微信小程序凭证（留空即走 mock）---
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""

    # --- 微信支付凭证 ---
    WXPAY_MCH_ID: str = ""
    WXPAY_API_KEY: str = ""
    WXPAY_CERT_PATH: str = ""

    # --- 腾讯地图 Key ---
    MAP_KEY: str = ""

    # --- 业务参数 ---
    COMMISSION_RATE: float = 0.0  # 平台抽佣比例（默认 0，仅预留数据位）
    PAY_TIMEOUT_MINUTES: int = 15  # 下单后未支付自动关闭时长
    VERIFY_CODE_EXPIRE_DAYS: int = 30  # 核销码有效期（天）
    SLOT_CAPACITY: int = 20  # 每个门店「时段」可预约上限（测试可改小）


settings = Settings()
