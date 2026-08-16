"""AI 接口路由：评论 / 诊断报告 / 内容生成。

三个接口均经 Agent 落 ai_task（pending→running→done/failed）。
无 LLM_API_KEY 时由 MockProvider 返回结构化结果。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.comment import CommentAgent
from app.agents.content import ContentAgent
from app.agents.diagnosis import DiagnosisAgent
from app.agents.provider import get_provider
from app.database import get_db
from app.models.sys_user import SysUser
from app.schemas.ai import CommentIn, ContentIn, ReportIn
from app.services import merchant_service as merchant_svc
from app.utils.response import not_found, ok
from app.utils.rbac import get_current_user

router = APIRouter(prefix="/api", tags=["ai"])


@router.post("/ai/comment")
async def ai_comment(
    body: CommentIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = CommentAgent(get_provider(), db)
    result, task_id = await agent.run(
        {"video": body.video, "industry": body.industry}
    )
    result.pop("_fallback", None)
    return ok({"comments": result.get("comments", []), "task_id": task_id})


@router.post("/ai/report")
async def ai_report(
    body: ReportIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    merchant = await merchant_svc.get_merchant(db, body.merchant_id, current_user)
    if merchant is None:
        return not_found("商家不存在或无权限")
    stores = await merchant_svc.get_stores(db, merchant.id)
    context = {
        "merchant_id": merchant.id,
        "store_id": body.store_id,
        "name": merchant.name,
        "industry": merchant.industry,
        "store_count": len(stores),
        "stores": [s.name for s in stores],
    }
    agent = DiagnosisAgent(get_provider(), db)
    result, task_id = await agent.run(context)
    result.pop("_fallback", None)
    return ok({"report": result, "task_id": task_id})


@router.post("/ai/content")
async def ai_content(
    body: ContentIn,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    merchant_id = current_user.merchant_id if current_user.merchant_id else 0
    agent = ContentAgent(get_provider(), db)
    result, task_id = await agent.run(
        {
            "type": body.type,
            "industry": body.industry,
            "topic": body.topic,
            "tone": body.tone,
            "merchant_id": merchant_id,
        }
    )
    result.pop("_fallback", None)
    return ok({"content": result.get("content", ""), "task_id": task_id})
