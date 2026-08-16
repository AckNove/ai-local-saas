"""评论生成 Agent：为商家视频生成多条拟真、不重复的评论。"""
from __future__ import annotations

from app.agents.base import Agent


class CommentAgent(Agent):
    agent_type = "comment"

    def build_prompt(self, data: dict) -> tuple[str, str]:
        video = data.get("video", "")
        industry = data.get("industry", "本地生活")
        system = (
            "你是熟悉本地生活的短视频评论写手，语气真实自然、像真实用户。"
            "请直接输出评论，每条一行，不要编号、不要解释。"
        )
        prompt = (
            f"行业：{industry}\n"
            f"视频内容/链接：{video}\n\n"
            "请生成 6 条不重复、有真实感的评论，每条一行。"
        )
        return system, prompt

    async def parse(self, raw: str) -> dict:
        comments = _extract_lines(raw)
        if not comments:
            raise ValueError("无法解析评论输出")
        return {"comments": comments}

    async def mock(self, data: dict) -> dict:
        industry = data.get("industry") or "本地生活"
        topic = (data.get("video") or "").strip() or "这家店"
        templates = [
            f"这家{industry}真的绝了，{topic}看得我直接种草！",
            f"已经收藏，周末就去打卡这家{industry}～",
            f"求地址！这种{industry}也太对我胃口了吧。",
            f"博主审美在线，{topic}拍得很有氛围感。",
            f"看了好几遍，{industry}的隐藏玩法被你挖到了。",
            f"原来还能这样玩{industry}，学到了学到了。",
        ]
        return {"comments": templates}


def _extract_lines(raw: str) -> list[str]:
    """从模型文本中提取每行非空的评论，去除常见编号前缀。"""
    import re

    out: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[\d]+\.[\s\)]*", "", line)
        line = re.sub(r"^[-*•\s]+", "", line)
        if line:
            out.append(line)
    return out[:10]
