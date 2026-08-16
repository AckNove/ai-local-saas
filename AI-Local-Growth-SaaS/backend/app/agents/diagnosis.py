"""商家诊断 Agent：生成现状 / 机会 / 方案的网页报告。"""
from __future__ import annotations

import json

from app.agents.base import Agent


class DiagnosisAgent(Agent):
    agent_type = "report"

    def build_prompt(self, data: dict) -> tuple[str, str]:
        name = data.get("name", "该商家")
        industry = data.get("industry", "本地生活")
        store_count = data.get("store_count", 0)
        store_names = "、".join(data.get("stores", []) or [])
        system = (
            "你是资深的本地生活商家增长顾问。请输出严谨、可执行的诊断报告，"
            "严格以 JSON 返回：{\"score\": 整数(0-100), \"summary\": 字符串, "
            "\"items\": [{\"dimension\": 维度, \"finding\": 现状, \"suggestion\": 建议}]}。"
        )
        prompt = (
            f"请诊断以下商家并输出 JSON 报告：\n"
            f"商家名称：{name}\n行业：{industry}\n"
            f"门店数：{store_count}\n门店：{store_names}\n"
        )
        return system, prompt

    async def parse(self, raw: str) -> dict:
        text = raw.strip()
        # 容错：截取第一个 { 到最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        obj = json.loads(text)
        if not isinstance(obj, dict) or "score" not in obj:
            raise ValueError("诊断结果缺少必要字段")
        return {
            "score": int(obj.get("score", 70)),
            "summary": str(obj.get("summary", "")),
            "items": obj.get("items", []),
        }

    async def mock(self, data: dict) -> dict:
        industry = data.get("industry") or "本地生活"
        name = data.get("name") or "该商家"
        return {
            "score": 72,
            "summary": (
                f"【{name}（{industry}）】整体处于成长期：内容曝光在起量，但"
                "转化与私域承接仍有明显提升空间，建议优先补齐短视频节奏与落地页跳转。"
            ),
            "items": [
                {
                    "dimension": "内容力",
                    "finding": "视频更新频率偏低，缺少固定人设与栏目。",
                    "suggestion": "建立每周 3 条的稳定更新机制，固定栏目化表达。",
                },
                {
                    "dimension": "转化力",
                    "finding": "种草卡落地页到视频号的跳转路径偏长。",
                    "suggestion": "用二维码一键直达视频号，缩短转化路径。",
                },
                {
                    "dimension": "私域力",
                    "finding": "缺少用户留存与复访机制。",
                    "suggestion": "落地页增加加微信 / 社群入口，沉淀私域。",
                },
            ],
        }
