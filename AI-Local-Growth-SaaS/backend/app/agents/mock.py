"""离线 Mock Provider：无需任何 API Key 即可返回结构化占位结果。"""
from __future__ import annotations

import json

from app.agents.provider import LLMProvider


class MockProvider(LLMProvider):
    """离线兜底 Provider。

    真实 Provider 不可用时由 Agent 自动降级到此处，保证 Demo 闭环。
    """

    async def complete(self, prompt: str, system: str | None = None, **kwargs) -> str:
        return (
            "（Mock 离线生成）基于输入已生成示例内容，用于演示闭环；"
            "配置 LLM_API_KEY 后将由真实模型生成。"
        )

    async def complete_json(self, prompt: str, system: str | None = None, **kwargs) -> dict:
        return {"mock": True, "prompt_excerpt": prompt[:200]}
