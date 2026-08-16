"""管理后台端到端 UI 自动化测试（Playwright + 截图）。

覆盖核心路径：
  1. 登录
  2. 数据概览（关键页面渲染）
  3. 创建商家
  4. 创建种草卡
  5. 生成二维码（落地页二维码渲染）
  6. AI 评论生成
  7. 其余关键页面渲染（商家管理 / 种草卡管理 / AI 诊断 / AI 内容）

运行：
  D:/DeliveryOptimization/miniconda/python.exe tests/ui/e2e_admin.py
前置：后端 uvicorn 已在 http://127.0.0.1:8000 运行（同源托管前端）。
产物：
  tests/ui/screenshots/*.png
  tests/ui/report.json
  tests/ui/report.md
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

HERE = os.path.dirname(os.path.abspath(__file__))
SHOT_DIR = os.path.join(HERE, "screenshots")
REPORT_JSON = os.path.join(HERE, "report.json")
REPORT_MD = os.path.join(HERE, "report.md")

os.makedirs(SHOT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 用例结果收集
# ---------------------------------------------------------------------------
results: list[dict] = []


def record(name: str, passed: bool, detail: str, screenshot: str | None = None) -> None:
    results.append(
        {
            "case": name,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
            "screenshot": os.path.relpath(screenshot, HERE) if screenshot else None,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    print(f"[{'PASS' if passed else 'FAIL'}] {name} - {detail}")


def shot(page, name: str) -> str:
    path = os.path.join(SHOT_DIR, f"{name}.png")
    try:
        page.screenshot(path=path, full_page=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  ! 截图失败 {name}: {exc}")
        return ""
    return path


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main() -> int:
    stamp = int(time.time())
    merchant_name = f"E2E商家_{stamp}"
    card_name = f"E2E种草卡_{stamp}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.set_default_timeout(20000)

        try:
            # ---------------- 1. 登录 ----------------
            try:
                page.goto(f"{BASE_URL}/login", wait_until="networkidle")
                page.wait_for_selector("#username", timeout=10000)
                page.fill("#username", ADMIN_USER)
                page.fill("#password", ADMIN_PASS)
                page.get_by_role("button", name="登录").click()
                page.wait_for_url("**/dashboard", timeout=15000)
                s = shot(page, "01_login_dashboard")
                record("登录", True, "已使用 admin 登录并跳转 /dashboard", s)
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "01_login_fail")
                record("登录", False, f"登录或跳转失败: {exc}", s)
                # 后续用例依赖登录态，提前终止
                browser.close()
                return _finalize()

            # ---------------- 2. 数据概览渲染 ----------------
            try:
                # 已在 /dashboard；确认侧边栏与主体渲染
                page.wait_for_selector("aside", timeout=10000)
                sidebar_ok = (
                    page.locator("aside").get_by_role("link", name="数据概览").count() > 0
                )
                login_btn_gone = page.get_by_role("button", name="登录", exact=True).count() == 0
                on_dashboard = "/dashboard" in page.url
                ok = sidebar_ok and login_btn_gone and on_dashboard
                s = shot(page, "02_dashboard")
                record(
                    "数据概览渲染",
                    ok,
                    "侧边栏与主体已渲染，登录按钮已消失" if ok else "仪表盘渲染异常",
                    s,
                )
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "02_dashboard_fail")
                record("数据概览渲染", False, f"渲染校验失败: {exc}", s)

            # ---------------- 3. 创建商家 ----------------
            try:
                page.locator("aside").get_by_role("link", name="商家管理").click()
                page.wait_for_selector("h1:text('商家管理')", timeout=10000)
                page.get_by_role("button", name="新增商家").click()
                dialog = page.locator('[role="dialog"]')
                dialog.wait_for(timeout=8000)
                # 第一个输入框即「商家名称 *」
                dialog.locator("input").first.fill(merchant_name)
                dialog.get_by_role("button", name="创建").click()
                # 等待弹窗关闭且新商家出现在列表
                page.wait_for_selector(f"text={merchant_name}", timeout=12000)
                s = shot(page, "03_merchant_created")
                record("创建商家", True, f"已创建商家「{merchant_name}」并出现在列表", s)
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "03_merchant_fail")
                record("创建商家", False, f"创建商家失败: {exc}", s)

            # ---------------- 4. 创建种草卡 ----------------
            try:
                page.locator("aside").get_by_role("link", name="种草卡管理").click()
                page.wait_for_selector("h1:text('种草卡管理')", timeout=10000)
                page.get_by_role("button", name="创建种草卡").click()
                page.wait_for_selector("h1:text('创建种草卡')", timeout=10000)
                # 所属商家（第一个 select）按名称选择
                sel = page.locator("select").first
                sel.wait_for(timeout=8000)
                page.locator(
                    f"select option:has-text('{merchant_name}')"
                ).first.wait_for(state="attached", timeout=10000)
                sel.select_option(label=merchant_name)
                page.get_by_placeholder("如：门店A-探店种草").fill(card_name)
                page.get_by_role("button", name="创建").click()
                # 创建成功后跳转详情页 /seed-cards/{id}
                page.wait_for_url("**/seed-cards/*", timeout=15000)
                s = shot(page, "04_seedcard_created")
                record("创建种草卡", True, f"已创建种草卡「{card_name}」并跳转详情页", s)
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "04_seedcard_fail")
                record("创建种草卡", False, f"创建种草卡失败: {exc}", s)

            # ---------------- 5. 生成二维码 ----------------
            try:
                # 详情页自动加载二维码（img alt=种草卡二维码）
                img = page.locator('img[alt="种草卡二维码"]')
                img.wait_for(state="visible", timeout=15000)
                s = shot(page, "05_qrcode")
                record("生成二维码", True, "种草卡二维码已成功渲染（PNG）", s)
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "05_qrcode_fail")
                record("生成二维码", False, f"二维码未渲染: {exc}", s)

            # ---------------- 6. AI 评论生成 ----------------
            try:
                page.locator("aside").get_by_role("link", name="AI 评论生成").click()
                page.wait_for_selector("h1:text('AI 评论生成')", timeout=10000)
                page.get_by_placeholder("粘贴视频号链接，或描述视频内容").fill(
                    "一段探店短视频：本地火锅店新品牛油锅底上线，氛围热闹"
                )
                page.get_by_role("button", name="生成评论").click()
                # 等待结果卡片出现（含「生成结果」）
                try:
                    page.wait_for_selector("text=生成结果", timeout=60000)
                    s = shot(page, "06_ai_comment")
                    record("AI 评论生成", True, "AI 已返回评论结果并渲染结果卡片", s)
                except PWTimeout:
                    s = shot(page, "06_ai_comment_timeout")
                    record(
                        "AI 评论生成",
                        False,
                        "点击生成后 60s 内未出现结果（LLM 可能不可达/超时）",
                        s,
                    )
            except Exception as exc:  # noqa: BLE001
                s = shot(page, "06_ai_comment_fail")
                record("AI 评论生成", False, f"AI 评论生成流程异常: {exc}", s)

            # ---------------- 7. 其余关键页面渲染 ----------------
            extra_pages = [
                ("AI 诊断报告", "ai/report"),
                ("AI 内容生成", "ai/content"),
                ("商家管理", "merchants"),
                ("种草卡管理", "seed-cards"),
            ]
            for label, route in extra_pages:
                try:
                    page.goto(f"{BASE_URL}/{route}", wait_until="load")
                    page.wait_for_selector("h1", timeout=10000)
                    on_login = page.url.rstrip("/").endswith("/login") or page.locator(
                        "input#username"
                    ).count() > 0
                    rendered = (not on_login) and page.locator("h1").count() > 0
                    s = shot(page, f"07_page_{route.replace('/', '_')}")
                    record(
                        f"页面渲染::{label}",
                        rendered,
                        f"{label} 页面已渲染" if rendered else f"{label} 被重定向到登录页",
                        s,
                    )
                except Exception as exc:  # noqa: BLE001
                    s = shot(page, f"07_page_{route.replace('/', '_')}_fail")
                    record(f"页面渲染::{label}", False, f"{label} 渲染异常: {exc}", s)

        finally:
            browser.close()

    return _finalize()


def _finalize() -> int:
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": BASE_URL,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "cases": results,
    }
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    lines = [
        "# 管理后台 UI 自动化测试报告",
        "",
        f"- 生成时间：{summary['generated_at']}",
        f"- 测试地址：{BASE_URL}",
        f"- 用例总数：**{len(results)}**　通过：**{passed}**　失败：**{failed}**",
        "",
        "## 用例明细",
        "",
        "| 用例 | 结果 | 说明 | 截图 |",
        "| --- | --- | --- | --- |",
    ]
    for r in results:
        shot_cell = f"[截图]({r['screenshot']})" if r["screenshot"] else "-"
        lines.append(
            f"| {r['case']} | {r['status']} | {r['detail']} | {shot_cell} |"
        )
    lines += ["", "## 结论", ""]
    if failed == 0:
        lines.append("✅ 全部核心路径通过，管理后台可正常使用。")
    else:
        lines.append(f"⚠️ 存在 {failed} 个失败用例，请查看上方明细与截图。")
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n>>> 报告已生成：{REPORT_MD}")
    print(f">>> 通过 {passed} / 失败 {failed} / 共 {len(results)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
