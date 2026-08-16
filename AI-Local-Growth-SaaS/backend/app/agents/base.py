"""Agent 抽象基类：统一编排 AI 调用并落 `ai_task`。

生命周期：pending → running → done / failed。
- 使用 MockProvider 时直接走内置 mock 逻辑。
- 使用真实 Provider 时调用 complete() 并 parse()；任何异常自动降级到 mock。
- 成功后可经 persist() 钩子落业务数据（如 ContentAgent 写入 video_content）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.mock import MockProvider
from app.agents.provider import LLMProvider
from app.models.ai_task import AITask


class Agent(ABC):
    """AI 代理基类。"""

    agent_type: str = "base"

    def __init__(self, provider: LLMProvider, db: AsyncSession) -> None:
        self.provider = provider
        self.db = db

    @abstractmethod
    def build_prompt(self, data: dict) -> tuple[str, str]:
        """构造 (system, prompt)。"""
        raise NotImplementedError

    @abstractmethod
    async def parse(self, raw: str) -> dict:
        """将模型原始输出解析为结构化结果。"""
        raise NotImplementedError

    @abstractmethod
    async def mock(self, data: dict) -> dict:
        """离线模板生成（无 Key 兜底）。"""
        raise NotImplementedError

    async def persist(self, result: dict, data: dict) -> None:
        """成功后的持久化钩子（默认无操作）。"""
        return None

    async def run(self, data: dict) -> tuple[dict, int]:
        """执行 Agent 并返回 (result, task_id)。

        任何失败都会将 ai_task.status 置为 failed 并重新抛出。
        """
        task = AITask(
            agent_type=self.agent_type, input=data, status="pending", output=None
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        task_id = task.id

        try:
            task.status = "running"
            await self.db.commit()

            if isinstance(self.provider, MockProvider):
                result = await self.mock(data)
            else:
                system, prompt = self.build_prompt(data)
                try:
                    raw = await self.provider.complete(prompt, system)
                    result = await self.parse(raw)
                except Exception:
                    result = await self.mock(data)
                    result = {**result, "_fallback": True}

            task.status = "done"
            task.output = result
            await self.db.commit()
            await self.persist(result, data)
            return result, task_id
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.output = {"error": str(exc)}
            await self.db.commit()
            raise
