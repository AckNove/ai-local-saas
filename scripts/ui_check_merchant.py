# -*- coding: utf-8 -*-
"""AI-Local 商家登录 + AI 诊断细节检查"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)

    # ---- 商家登录 ----
    page.goto(BASE + '/login')
    time.sleep(0.5)
    # 检查登录表单结构
    html = page.content()
    has_user = 'username' in html
    print('login has username field:', has_user)
    # 填商家账号
    try:
        page.fill('input[placeholder*="用户名"], input[placeholder*="账号"], input[type="text"]', 'merchant')
    except Exception as e:
        print('fill user err:', e)
    page.fill('input[type="password"]', 'merchant123')
    # 打印所有按钮
    btns = page.locator('button').all_inner_texts()
    print('login buttons:', btns)
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.5)
    print('merchant login url:', page.url)
    body = page.content()
    print('has dashboard text:', '数据概览' in body)
    menus = page.locator('aside a, nav a').all_inner_texts()
    print('merchant menus:', [m.strip() for m in menus])
    # 截图
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-merchant-login.png')

    browser.close()
