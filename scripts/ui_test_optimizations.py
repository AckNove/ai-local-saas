# -*- coding: utf-8 -*-
"""验证本轮优化：趋势图 + 搜索框 + H5商家信息 + 商家我的门店"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

results = []
def log(step, ok, note=''):
    results.append({'step': step, 'ok': ok, 'note': note})
    print(f"[{'PASS' if ok else 'FAIL'}] {step} - {note}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # --- AI-Local admin 数据概览趋势 ---
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)
    page.goto('http://127.0.0.1:8000/login')
    page.fill('#username', 'admin')
    page.fill('#password', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.5)
    body = page.content()
    has_trend = '近 7 天互动趋势' in body
    log('admin 数据概览含趋势图', has_trend, '')
    page.screenshot(path='D:/桌面/AI-local/logs/opt-ai-dashboard-trend.png')

    # --- AI-Local 商家"我的门店" ---
    page.goto('http://127.0.0.1:8000/login')
    page.fill('#username', 'merchant')
    page.fill('#password', 'merchant123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.5)
    body = page.content()
    has_store = '我的门店' in body
    log('商家数据概览含"我的门店"', has_store, '')
    page.screenshot(path='D:/桌面/AI-local/logs/opt-ai-merchant-stores.png')

    # --- AI-Local H5 商家信息 ---
    page2 = browser.new_page(viewport={'width': 390, 'height': 844})
    page2.set_default_timeout(10000)
    page2.goto('http://127.0.0.1:8000/c/IA6m6Enf')
    page2.wait_for_load_state('networkidle')
    time.sleep(3)
    txt = page2.inner_text('body')
    has_shop = ('地址' in txt) or ('电话' in txt)
    log('H5 落地页含商家信息', has_shop, txt[:200])
    page2.screenshot(path='D:/桌面/AI-local/logs/opt-ai-h5-shopinfo.png')

    # --- WeChat 套餐搜索框 ---
    page3 = browser.new_page(viewport={'width': 1440, 'height': 900})
    page3.set_default_timeout(10000)
    page3.goto('http://127.0.0.1:8001/login')
    page3.fill('input[placeholder*="admin"]', 'admin')
    page3.fill('input[type="password"]', 'admin123')
    page3.click('button:has-text("登录")')
    page3.wait_for_load_state('networkidle')
    time.sleep(1)
    page3.goto('http://127.0.0.1:8001/packages')
    page3.wait_for_load_state('networkidle')
    time.sleep(1)
    has_search = page3.locator('input[placeholder*="套餐名称"]').count() > 0
    log('套餐管理含搜索框', has_search, '')
    # 搜索"双人"
    page3.fill('input[placeholder*="套餐名称"]', '双人')
    time.sleep(1.5)
    rows = page3.locator('table tbody tr').count()
    log('套餐搜索"双人"过滤', rows > 0, f'rows={rows}')

    # --- WeChat 订单搜索框 ---
    page3.goto('http://127.0.0.1:8001/orders')
    page3.wait_for_load_state('networkidle')
    time.sleep(1)
    has_osearch = page3.locator('input[placeholder*="订单号"]').count() > 0
    log('订单管理含搜索框', has_osearch, '')

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
