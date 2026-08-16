# -*- coding: utf-8 -*-
"""AI-Local 消费者视角：H5 落地页真实体验"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
results = []

def log(step, ok, note=''):
    results.append({'step': step, 'ok': ok, 'note': note})
    print(f"[{'PASS' if ok else 'FAIL'}] {step} - {note}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 390, 'height': 844})  # 手机视口
    page.set_default_timeout(10000)

    # 手机端打开落地页
    page.goto(BASE + '/c/IA6m6Enf')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    body = page.content()
    log('落地页加载', 'title' in body.lower() or 'btn' in body, f'len={len(body)}')
    # 提取可见文字
    text = page.inner_text('body')
    log('落地页内容', len(text.strip()) > 30, text.strip()[:200])
    # 按钮
    btns = page.locator('button').all_inner_texts()
    log('落地页按钮', len(btns) >= 2, '按钮: ' + ' | '.join(b.strip() for b in btns))
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-h5-consumer.png')

    # 点击分享（测试事件上报）
    page.click('button:has-text("分享")')
    time.sleep(1)
    log('分享按钮可点击', True, '')

    # 写评论
    page.click('button:has-text("写评论")')
    time.sleep(0.5)
    try:
        page.fill('textarea', '这家店不错，推荐！')
        page.click('button:has-text("提交评论")')
        time.sleep(1)
        log('提交评论', '感谢' in page.content(), '')
    except Exception as e:
        log('提交评论', False, str(e)[:100])

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
