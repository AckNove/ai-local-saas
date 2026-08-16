"""租户与 RBAC 模型：平台运营 / 商户 / 商户主账号 / 门店 / 员工 / 消费者。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, SoftDeleteMixin, utc_now
from app.core.tenant import ROLE_VERIFIER


class PlatformOperator(Base, SoftDeleteMixin):
    """平台运营方账号（SaaS 拥有者/运营团队）。"""

    __tablename__ = "platform_operator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="登录名"
    )
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="bcrypt 哈希")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PlatformOperator id={self.id} username={self.username}>"


class Merchant(Base, SoftDeleteMixin):
    """商户（连锁/多门店品牌主体）。"""

    __tablename__ = "merchant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="商户名称")
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # 小程序商家标识：每个商家一个小程序，小程序端通过该 code 拉取本商家品牌配置与套餐
    merchant_code: Mapped[str | None] = mapped_column(
        String(32), unique=True, index=True, nullable=True, comment="小程序商家标识（唯一短码）"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False, comment="active/disabled"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    stores: Mapped[list["Store"]] = relationship(back_populates="merchant")


class MerchantUser(Base, SoftDeleteMixin):
    """商户主账号（merchant_owner 角色登录用）。"""

    __tablename__ = "merchant_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="登录名"
    )
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="bcrypt 哈希")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class Store(Base, SoftDeleteMixin):
    """门店：绑定地图 POI，是履约与核销的最小单元。"""

    __tablename__ = "store"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="门店名称")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    business_hours: Mapped[str | None] = mapped_column(String(128), nullable=True)
    poi_id: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="地图 POI ID")
    poi_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    merchant: Mapped["Merchant"] = relationship(back_populates="stores")


class Staff(Base, SoftDeleteMixin):
    """门店员工：store_manager（店长）/ verifier（核销员）。

    注：为支持 web/小程序登录，扩展 username + password_hash（超出类图，
    属合理 RBAC 登录必要字段）；openid 用于微信侧扫码核销身份关联。
    """

    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("merchant.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True, comment="登录名（web/小程序）"
    )
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="bcrypt 哈希")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="姓名/昵称")
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20), default=ROLE_VERIFIER, nullable=False,
        comment="store_manager/verifier",
    )
    openid: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="微信 openid")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class Consumer(Base, SoftDeleteMixin):
    """C 端消费者（微信用户）。"""

    __tablename__ = "consumer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    unionid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
