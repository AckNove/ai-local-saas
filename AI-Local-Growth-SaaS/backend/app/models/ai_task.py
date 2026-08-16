"""AI 任务表（每次 AI 调用落库，状态机 pending→running→done/failed）。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, utc_now


class AITask(Base):
    """AI 调用任务记录。

    status 经历 pending → running → done / failed，失败也留痕，便于排查与计费。
    input / output 使用 JSON 类型（方言无关），存储结构化数据。
    """

    __tablename__ = "ai_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_type: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True, comment="comment/report/content"
    )
    input: Mapped[dict] = mapped_column(JSON, nullable=False, comment="调用入参（结构化）")
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="调用结果（结构化）")
    status: Mapped[str] = mapped_column(
        String(16), default="pending", nullable=False, index=True,
        comment="pending/running/done/failed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AITask id={self.id} type={self.agent_type} status={self.status}>"
