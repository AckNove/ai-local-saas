# -*- coding: utf-8 -*-
"""WeChat web-admin 修复后 UI 回归测试"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8001'
results = []

def log(step, ok, note=''):
    results.append({'step': step, 'ok': ok, 'note': note})
    print(f"[{'PASS' if ok else 'FAIL'}] {step} - {note}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)

    # 登录
    page.goto(BASE + '/login')
    page.fill('input[placeholder*="admin"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    log('admin 登录', '/orders' in page.url, page.url)

    # 门店管理页：应能加载列表（无 404）
    page.goto(BASE + '/stores')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_404 = '404' in body or 'Request failed' in body
    rows = page.locator('table tbody tr').count()
    log('门店列表加载', not has_404, f'rows={rows}')

    # 套餐管理页
    page.goto(BASE + '/packages')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_404 = '404' in body or 'Request failed' in body
    rows = page.locator('table tbody tr').count()
    log('套餐列表加载', not has_404, f'rows={rows}')

    # 新建套餐：检查图片上传 UI（应为 URL 列表而非 JSON 手填）
    page.click('button:has-text("新建套餐")')
    time.sleep(0.5)
    modal = page.locator('.card:has(input)').inner_text()
    has_json = 'JSON' in modal
    has_add_img = '添加图片' in modal
    log('套餐图片 UI', has_add_img and not has_json, f'添加图片按钮={has_add_img} JSON手填={has_json}')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-package-fixed.png')
    page.click('button:has-text("取消")')

    # 视频号挂载页
    page.goto(BASE + '/channels')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_404 = '404' in body or 'Request failed' in body or '系统错误' in body
    log('视频号挂载页加载', not has_404, '')

    # 数据看板页
    page.goto(BASE + '/dashboard')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_404 = '404' in body or 'Request failed' in body
    log('数据看板加载', not has_404, '')

    browser.close()

print('\n===== SUMMARY =====')
fails = [r for r in results if not r['ok']]
print(f"total={len(results)} pass={len(results)-len(fails)} fail={len(fails)}")
for r in results:
    print(json.dumps(r, ensure_ascii=False))
