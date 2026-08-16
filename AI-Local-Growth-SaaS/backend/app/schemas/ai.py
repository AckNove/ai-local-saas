"""AI 接口 Schema。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class CommentIn(BaseModel):
    video: str = Field(..., min_length=1, description="视频链接或描述文本")
    industry: str = Field(default="", description="行业")


class CommentOut(BaseModel):
    comments: list[str] = Field(default_factory=list)
    task_id: int


class ReportIn(BaseModel):
    merchant_id: int = Field(..., description="商家 id")
    store_id: int | None = Field(default=None, description="门店 id（可选）")


class ReportItem(BaseModel):
    dimension: str
    finding: str
    suggestion: str


class ReportOut(BaseModel):
    report: "ReportData"
    task_id: int


class ReportData(BaseModel):
    score: int
    summary: str
    items: list[ReportItem] = Field(default_factory=list)


class ContentIn(BaseModel):
    type: str = Field(default="script", description="script/copy")
    industry: str = Field(default="", description="行业")
    topic: str = Field(..., min_length=1, description="主题")
    tone: str | None = Field(default=None, description="语气风格（可选）")


class ContentOut(BaseModel):
    content: str
    task_id: int


ReportOut.model_rebuild()
