"""DeepSeek Provider（httpx 异步调用，国内可达，推荐真实后端）。

- 默认 Base URL：https://api.deepseek.com
- 默认模型：deepseek-chat
- complete_json() 对模型输出做容错解析：去除 ```json 围栏、截取首个
  JSON 对象/数组，确保真实 LLM 返回结构化数据时可被稳定解析；失败时
  抛出 ValueError，由 Agent 基类自动降级到 Mock。
"""
from __future__ import annotations

import json
import re

import httpx

from app.agents.provider import LLMProvider
from config import DEEPSEEK_API_KEY, LLM_API_KEY, LLM_BASE_URL

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
TIMEOUT_SECONDS = 30.0


def _extract_json(raw: str) -> dict:
    """从模型文本中稳健提取 JSON 对象（或数组）。

    处理常见情况：
    1. 被 ```json ... ``` 代码围栏包裹
    2. 前后有说明性文本，JSON 嵌在其中
    3. 直接是 JSON

    提取失败抛出 ValueError，交由上层降级。
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("模型返回为空，无法解析 JSON")

    # 1) 优先去除 markdown 代码围栏
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    # 2) 截取第一个 { 到最后一个 }（对象）
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # 3) 退而求其次尝试数组
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # 4) 全文直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"无法从模型输出解析 JSON: {exc}") from exc


class DeepSeekProvider(LLMProvider):
    """调用 DeepSeek Chat Completions 接口。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        # 优先使用传入 key，再回退到专用/通用环境变量（不硬编码）
        self.api_key = api_key or DEEPSEEK_API_KEY or LLM_API_KEY
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
        return _extract_json(raw)
