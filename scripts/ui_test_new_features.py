# -*- coding: utf-8 -*-
"""验证套餐图片上传 UI + H5 好评复制功能"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

results = []
def log(step, ok, note=''):
    results.append({'step': step, 'ok': ok, 'note': note})
    print(f"[{'PASS' if ok else 'FAIL'}] {step} - {note}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # --- WeChat 套餐图片上传 UI ---
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)
    page.goto('http://127.0.0.1:8001/login')
    page.fill('input[placeholder*="admin"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    page.goto('http://127.0.0.1:8001/packages')
    page.wait_for_load_state('networkidle')
    time.sleep(0.8)
    page.click('button:has-text("新建套餐")')
    time.sleep(0.6)
    # 检查上传按钮存在
    modal = page.locator('.fixed').first.inner_text()
    has_upload = '上传图片' in modal
    log('套餐表单含"上传图片"按钮', has_upload, '')
    # 检查 file input
    file_count = page.locator('input[type="file"]').count()
    log('存在文件选择输入框', file_count > 0, f'count={file_count}')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-upload-ui.png')
    page.click('button:has-text("取消")')

    # --- AI-Local H5 好评复制 ---
    page2 = browser.new_page(viewport={'width': 390, 'height': 844})
    page2.set_default_timeout(10000)
    page2.goto('http://127.0.0.1:8000/c/IA6m6Enf')
    page2.wait_for_load_state('networkidle')
    time.sleep(3)  # 等好评异步加载
    body = page2.content()
    has_review = '好评' in body or '复制' in body
    log('H5 落地页含好评区', has_review, '')
    text = page2.inner_text('body')
    log('落地页展示好评文案', '复制好评' in text, text[:300])
    # 点击复制
    try:
        page2.click('button:has-text("复制好评")')
        time.sleep(0.5)
        btn_text = page2.locator('button:has-text("已复制")').count()
        log('复制按钮点击后反馈', btn_text > 0, '')
    except Exception as e:
        log('复制按钮可点击', False, str(e)[:80])
    page2.screenshot(path='D:/桌面/AI-local/logs/ai-local-h5-review.png')

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
