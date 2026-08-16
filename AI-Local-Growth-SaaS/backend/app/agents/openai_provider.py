"""OpenAI Provider（httpx 异步调用）。"""
from __future__ import annotations

import json

import httpx

from app.agents.provider import LLMProvider
from config import LLM_API_KEY, LLM_BASE_URL

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
TIMEOUT_SECONDS = 30.0


class OpenAIProvider(LLMProvider):
    """调用 OpenAI 兼容 Chat Completions 接口。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or LLM_API_KEY
        self.base_url = (base_url or LLM_BASE_URL or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL

    async def complete(self, prompt: str, system: str | None = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.8),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def complete_json(self, prompt: str, system: str | None = None, **kwargs) -> dict:
        raw = await self.complete(prompt, system, **kwargs)
        return json.loads(raw)
