"""AI 接口测试：Mock 结构化返回、ai_task 落库 status=done、鉴权。"""
from __future__ import annotations

import app.database as database_module
from sqlalchemy import func, select

from app.models.ai_task import AITask
from app.models.video_content import VideoContent


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_comment_mock(client, admin_token):
    r = await client.post(
        "/api/ai/comment",
        headers=_auth(admin_token),
        json={"video": "https://example.com/v", "industry": "餐饮"},
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert isinstance(d["comments"], list) and len(d["comments"]) > 0
    assert isinstance(d["task_id"], int)
    # ai_task 落库且 done
    async with database_module.async_session_factory() as db:
        task = (
            await db.execute(select(AITask).where(AITask.id == d["task_id"]))
        ).scalar_one()
    assert task.status == "done"
    assert task.agent_type == "comment"


async def test_report_mock(client, admin_token):
    mid = (
        await client.post(
            "/api/merchant/create",
            headers=_auth(admin_token),
            json={"name": "m", "stores": []},
        )
    ).json()["data"]["id"]
    r = await client.post(
        "/api/ai/report", headers=_auth(admin_token), json={"merchant_id": mid}
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert isinstance(d["report"]["score"], int)
    assert isinstance(d["report"]["items"], list)
    async with database_module.async_session_factory() as db:
        task = (
            await db.execute(select(AITask).where(AITask.id == d["task_id"]))
        ).scalar_one()
    assert task.status == "done"
    assert task.agent_type == "report"


async def test_content_mock_writes_video(client, admin_token):
    r = await client.post(
        "/api/ai/content",
        headers=_auth(admin_token),
        json={"type": "script", "industry": "餐饮", "topic": "招牌菜"},
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert isinstance(d["content"], str) and len(d["content"]) > 0
    async with database_module.async_session_factory() as db:
        task = (
            await db.execute(select(AITask).where(AITask.id == d["task_id"]))
        ).scalar_one()
        n = (await db.execute(select(func.count()).select_from(VideoContent))).scalar_one()
    assert task.status == "done"
    assert task.agent_type == "content"
    assert n >= 1


async def test_ai_requires_auth(client):
    r = await client.post(
        "/api/ai/comment", json={"video": "x", "industry": "餐饮"}
    )
    assert r.status_code == 401
    assert r.json()["code"] == 401
