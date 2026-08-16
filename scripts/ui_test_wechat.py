# -*- coding: utf-8 -*-
"""WeChat-POI web-admin 全流程体验测试（Playwright）"""
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

    # 1. 打开登录页
    page.goto(BASE + '/login')
    page.wait_for_load_state('networkidle')
    log('打开登录页', '视频号团购 SaaS' in page.content(), page.title())

    # 2. 登录 admin
    page.fill('input[placeholder*="admin"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    log('admin 登录', '/orders' in page.url or '订单' in page.content(), f'url={page.url}')

    # 3. 检查侧边栏菜单（有无商户管理/员工管理）
    menus = page.locator('nav a').all_inner_texts()
    log('侧边栏菜单', len(menus) > 0, '菜单: ' + ' | '.join(m.strip() for m in menus))

    # 4. 门店管理页 - 尝试新增门店
    page.goto(BASE + '/stores')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    page.click('button:has-text("新增门店")')
    time.sleep(0.5)
    modal_text = page.locator('.card:has(input)').inner_text() if page.locator('.card:has(input)').count() else ''
    has_poi_section = 'POI' in modal_text
    log('门店表单含 POI 配置', has_poi_section, '表单字段: ' + modal_text.replace(chr(10), ' ')[:200])
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-store-modal.png')
    page.click('button:has-text("取消")')

    # 5. 套餐管理页 - 检查图片输入方式
    page.goto(BASE + '/packages')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    page.click('button:has-text("新建套餐")')
    time.sleep(0.5)
    pkg_modal = page.locator('.card:has(input)').inner_text() if page.locator('.card:has(input)').count() else ''
    has_json_input = 'JSON' in pkg_modal
    has_upload = '上传' in pkg_modal or 'file' in (page.locator('.card input[type=file]').count() and 'file' or '')
    file_inputs = page.locator('.card input[type="file"]').count()
    log('套餐表单图片上传', file_inputs > 0, f'file输入框数={file_inputs}; 含JSON手填={"JSON" in pkg_modal}')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-package-modal.png')
    page.click('button:has-text("取消")')

    # 6. 视频号挂载页
    page.goto(BASE + '/channels')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    chan_text = page.content()
    log('视频号挂载页可访问', '视频号挂载' in chan_text, '')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-channels.png')

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
