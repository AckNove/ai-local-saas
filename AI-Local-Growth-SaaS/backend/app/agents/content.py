"""内容生成 Agent：生成视频脚本 / 营销文案草稿（不自动发布）。"""
from __future__ import annotations

from app.agents.base import Agent
from app.models.video_content import VideoContent


class ContentAgent(Agent):
    agent_type = "content"

    def build_prompt(self, data: dict) -> tuple[str, str]:
        ctype = data.get("type", "script")
        industry = data.get("industry", "本地生活")
        topic = data.get("topic", "")
        tone = data.get("tone") or "轻松种草"
        kind = "短视频脚本" if ctype == "script" else "营销文案"
        system = (
            "你是本地生活行业的短视频内容策划，输出可直接使用的草稿（不自动发布）。"
            "内容要口语化、有钩子、适合视频号。"
        )
        prompt = (
            f"请为以下需求生成一份{kind}：\n行业：{industry}\n"
            f"主题：{topic}\n语气风格：{tone}\n"
            "请直接输出内容正文。"
        )
        return system, prompt

    async def parse(self, raw: str) -> dict:
        content = raw.strip()
        if not content:
            raise ValueError("内容生成为空")
        return {"content": content}

    async def mock(self, data: dict) -> dict:
        ctype = data.get("type", "script")
        industry = data.get("industry") or "本地生活"
        topic = data.get("topic") or "今日推荐"
        tone = data.get("tone") or "轻松种草"
        if ctype == "script":
            content = (
                f"【{industry}·{topic} 短视频脚本｜{tone}】\n\n"
                "0-3s 钩子：别再瞎逛了！这家店我替你踩过坑。\n"
                "3-15s 卖点：环境、招牌、性价比三连击，镜头给特写。\n"
                "15-30s 体验：真实探店过程，口播带情绪。\n"
                "30-45s 行动：扫码或点主页直达，限时福利记得冲。\n"
                "（AI 生成草稿，发布前请人工核对。）"
            )
        else:
            content = (
                f"【{industry}·{topic} 文案｜{tone}】\n\n"
                f"在{industry}里，{topic}才是隐藏王者。\n"
                "环境舒服、出品稳定、人均友好——工作日也能轻松约。\n"
                "点击下方/扫码直达，先把这波福利锁定。\n"
                "（AI 生成草稿，发布前请人工核对。）"
            )
        return {"content": content}

    async def persist(self, result: dict, data: dict) -> None:
        """将生成脚本 / 文案写入 video_content 表。"""
        title = data.get("topic") or (data.get("type") or "content")
        content = VideoContent(
            merchant_id=int(data.get("merchant_id", 0) or 0),
            title=str(title)[:255],
            url="",
            category=str(data.get("type", "script")),
        )
        self.db.add(content)
        await self.db.commit()
