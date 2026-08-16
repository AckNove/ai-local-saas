# -*- coding: utf-8 -*-
"""调试商户创建表单"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8001'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)

    page.goto(BASE + '/login')
    page.fill('input[placeholder*="admin"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    page.goto(BASE + '/merchants')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    print('page text snippet:', page.inner_text('body')[:300])
    print('buttons:', page.locator('button').all_inner_texts())
    page.click('button:has-text("新增商户")')
    time.sleep(0.8)
    # 检查弹窗结构
    labels = page.locator('label').all_inner_texts()
    print('modal labels:', labels)
    inputs = page.locator('.fixed input').count()
    print('modal inputs:', inputs)
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-merchant-modal-debug.png')
    browser.close()
