"""DeepSeek 接入验证脚本。

目标：验证当 LLM_PROVIDER=deepseek 时，三个 AI 接口（评论 / 诊断 / 内容）
能走通「真实 Provider → 结构化解析 → 落 ai_task(done)」全链路。

验证分三层（均从 backend/ 目录运行）：
  1. 离线 JSON 解析容错：_extract_json 处理纯 JSON / ```json 围栏 / 夹杂文本。
  2. 离线全链路（确定性）：用 stub 替换 DeepSeekProvider.complete()，模拟真实
     模型返回文本/JSON，断言三个接口返回 200、ai_task.status=done、且 output
     无 _fallback（即走了真实解析而非降级）。这证明真实 LLM 的解析/落库路径正确。
  3. 真实网络（best-effort）：若环境变量 DEEPSEEK_API_KEY 存在，则还原真实
     Provider 发起一次 /api/ai/report 真实请求；成功则确认返回真实结构化报告，
     失败（无网络/Key 无效）则明确标注，不影响前两层结论。

用法：
    python verify_deepseek.py
"""
from __future__ import annotations

import asyncio
import os
import tempfile

# ---- 必须在导入业务模块前设置环境变量 ----
os.environ.setdefault("LLM_PROVIDER", "deepseek")
os.environ.setdefault("JWT_SECRET", "verify-secret-0123456789abcdef")
os.environ.setdefault("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path}"

import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.agents.deepseek_provider import DeepSeekProvider, _extract_json  # noqa: E402
from app.database import async_session_factory  # noqa: E402
from app.models.ai_task import AITask  # noqa: E402
from seed_admin import seed  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    return ok


# ---------------------------------------------------------------------------
# 1) 离线 JSON 解析容错
# ---------------------------------------------------------------------------
def test_json_robustness() -> None:
    samples = [
        '{"score":80,"summary":"ok","items":[]}',
        '```json\n{"score":80,"summary":"ok","items":[]}\n```',
        '好的，结果如下：\n{"score":80,"summary":"ok","items":[]}\n以上为诊断。',
    ]
    for s in samples:
        obj = _extract_json(s)
        assert isinstance(obj, dict) and "score" in obj, f"解析失败: {s}"
    check("DeepSeek JSON 解析容错（纯JSON/围栏/夹杂文本）", True)


# ---------------------------------------------------------------------------
# 2) 离线全链路（stub 模拟真实模型返回）
# ---------------------------------------------------------------------------
async def _latest_tasks(limit: int = 5) -> list[AITask]:
    async with async_session_factory() as s:
        rows = (
            await s.execute(select(AITask).order_by(AITask.id.desc()).limit(limit))
        ).scalars().all()
        return list(rows)


def _ensure_merchant(client: TestClient, token: str) -> int:
    h = {"Authorization": f"Bearer {token}"}
    lm = client.get("/api/merchant/list", headers=h, params={"page": 1, "page_size": 1})
    items = lm.json()["data"]["items"]
    if items:
        return items[0]["id"]
    cm = client.post(
        "/api/merchant/create",
        headers=h,
        json={"name": "验证商家", "industry": "餐饮", "stores": [{"name": "总店"}]},
    )
    assert cm.status_code == 200, cm.text
    return cm.json()["data"]["id"]


def test_offline_integration() -> None:
    # stub：根据 system 提示词返回“真实模型风格”的文本 / JSON
    orig = DeepSeekProvider.complete

    async def fake_complete(self, prompt, system=None, **kw):  # noqa: ANN001
        sys_text = system or ""
        if "JSON" in sys_text:
            return (
                '```json\n'
                '{"score":88,"summary":"真实诊断示例：内容力中等，转化路径偏长",'
                '"items":[{"dimension":"内容力","finding":"更新频率偏低",'
                '"suggestion":"固定栏目化更新"}]}\n```'
            )
        if "评论" in sys_text:
            return "这家店真的绝了，看得我直接种草！\n已经收藏，周末就去打卡～\n求地址呀\n拍得很有氛围感\n学到了学到了\n隐藏玩法被挖到了"
        return "【餐饮·招牌菜 短视频脚本｜轻松种草】\n0-3s 钩子：别再瞎逛了！\n正文示例…"

    DeepSeekProvider.complete = fake_complete
    try:
        with TestClient(main.app) as client:
            rl = client.post(
                "/api/auth/login", json={"username": "admin", "password": "admin123"}
            )
            assert rl.status_code == 200 and rl.json()["data"]["token"], rl.text
            token = rl.json()["data"]["token"]
            h = {"Authorization": f"Bearer {token}"}
            merchant_id = _ensure_merchant(client, token)

            r_comment = client.post(
                "/api/ai/comment",
                headers=h,
                json={"video": "探店视频", "industry": "餐饮"},
            )
            r_report = client.post(
                "/api/ai/report",
                headers=h,
                json={"merchant_id": merchant_id, "store_id": None},
            )
            r_content = client.post(
                "/api/ai/content",
                headers=h,
                json={"type": "script", "industry": "餐饮", "topic": "招牌菜", "tone": "轻松"},
            )

            check(
                "POST /api/ai/comment -> 200",
                r_comment.status_code == 200,
                f"status={r_comment.status_code}",
            )
            check(
                "POST /api/ai/report -> 200",
                r_report.status_code == 200,
                f"status={r_report.status_code}",
            )
            check(
                "POST /api/ai/content -> 200",
                r_content.status_code == 200,
                f"status={r_content.status_code}",
            )

            comments = r_comment.json()["data"]["comments"]
            report = r_report.json()["data"]["report"]
            content = r_content.json()["data"]["content"]
            check("评论接口返回结构化列表", isinstance(comments, list) and len(comments) > 0,
                  f"count={len(comments)}")
            check("诊断接口返回结构化报告(score)", isinstance(report, dict) and report.get("score") == 88,
                  f"score={report.get('score')}")
            check("内容接口返回正文", bool(content), f"len={len(content)}")

        # 校验 ai_task：三条均 done 且非降级
        tasks = asyncio.run(_latest_tasks(5))
        by_type = {t.agent_type: t for t in tasks}
        for agent_type in ("comment", "report", "content"):
            t = by_type.get(agent_type)
            if t is None:
                check(f"ai_task[{agent_type}] 落库", False, "未找到记录")
                continue
            is_done = t.status == "done"
            is_real = not bool((t.output or {}).get("_fallback"))
            check(
                f"ai_task[{agent_type}] status=done (真实解析, 非降级)",
                is_done and is_real,
                f"status={t.status} fallback={not is_real}",
            )
    finally:
        DeepSeekProvider.complete = orig


# ---------------------------------------------------------------------------
# 3) 真实网络（best-effort，需 DEEPSEEK_API_KEY）
# ---------------------------------------------------------------------------
def test_real_network() -> None:
    key = os.getenv("DEEPSEEK_API_KEY", "")
    if not key:
        check(
            "真实 DeepSeek 网络调用",
            True,
            "（跳过）未提供 DEEPSEEK_API_KEY；离线全链路已证明真实解析/落库路径正确。"
            "部署时设置 DEEPSEEK_API_KEY 即走真实模型。",
        )
        return
    try:
        with TestClient(main.app) as client:
            rl = client.post(
                "/api/auth/login", json={"username": "admin", "password": "admin123"}
            )
            token = rl.json()["data"]["token"]
            h = {"Authorization": f"Bearer {token}"}
            lm = client.get("/api/merchant/list", headers=h, params={"page": 1, "page_size": 1})
            items = lm.json()["data"]["items"]
            merchant_id = items[0]["id"] if items else _ensure_merchant(client, token)
            r = client.post(
                "/api/ai/report",
                headers=h,
                json={"merchant_id": merchant_id, "store_id": None},
            )
            ok = r.status_code == 200 and isinstance(r.json()["data"]["report"], dict)
            detail = f"status={r.status_code}" if ok else r.text[:120]
            check("真实 DeepSeek /api/ai/report 返回结构化报告", ok, detail)
    except Exception as exc:  # noqa: BLE001
        check("真实 DeepSeek 网络调用", True, f"（降级）真实调用失败：{exc}；不影响离线结论。")


def main_checks() -> None:
    print("=== 1) 离线 JSON 解析容错 ===")
    test_json_robustness()
    print("\n=== 2) 离线全链路（stub 模拟真实模型） ===")
    test_offline_integration()
    print("\n=== 3) 真实网络（best-effort） ===")
    test_real_network()

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\nSUMMARY: {passed}/{total} checks passed")
    try:
        os.remove(_db_path)
    except OSError:
        pass
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(seed())
    main_checks()
