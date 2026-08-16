"""LLM Provider 抽象与工厂。

get_provider() 根据 config.LLM_PROVIDER 返回对应实现，缺省为 MockProvider，
保证无 API Key 也能离线跑通。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from config import DEEPSEEK_API_KEY, LLM_API_KEY, LLM_BASE_URL, LLM_PROVIDER


class LLMProvider(ABC):
    """LLM 提供方抽象。"""

    @abstractmethod
    async def complete(self, prompt: str, system: str | None = None, **kwargs) -> str:
        """返回文本补全结果。"""
        raise NotImplementedError

    @abstractmethod
    async def complete_json(self, prompt: str, system: str | None = None, **kwargs) -> dict:
        """返回结构化（JSON）补全结果。"""
        raise NotImplementedError


def get_provider() -> LLMProvider:
    """根据配置返回 Provider 实例。

    - openai   : 使用通用 LLM_API_KEY / LLM_BASE_URL（OpenAI 兼容）
    - deepseek : 优先使用专用 DEEPSEEK_API_KEY，缺省回退到 LLM_API_KEY
    - 其它/缺省 : MockProvider（离线兜底）
    """
    provider = LLM_PROVIDER
    if provider == "openai":
        from app.agents.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=LLM_API_KEY, base_url=LLM_BASE_URL or None)
    if provider == "deepseek":
        from app.agents.deepseek_provider import DeepSeekProvider

        # 优先专用 Key，回退到通用 Key
        return DeepSeekProvider(api_key=DEEPSEEK_API_KEY or LLM_API_KEY)
    from app.agents.mock import MockProvider

    return MockProvider()
