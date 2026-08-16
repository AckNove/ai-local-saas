# -*- coding: utf-8 -*-
"""AI-Local 商家视角体验测试"""
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
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.set_default_timeout(10000)

    # 商家登录
    page.goto(BASE + '/login')
    page.fill('#username', 'merchant')
    page.fill('#password', 'merchant123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.5)
    log('商家登录', '/dashboard' in page.url, f'url={page.url}')
    menus = page.locator('aside a, nav a').all_inner_texts()
    log('商家菜单', len(menus) > 0, '菜单: ' + ' | '.join(m.strip() for m in menus))
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-merchant-dashboard.png')

    # 商家数据概览（应只显示自己名下数据）
    body = page.content()
    log('商家数据概览', '数据概览' in body and '仅展示您名下数据' in body, '')

    # 商家能否访问商家管理（应受限：只能看自己的，不能删）
    page.goto(BASE + '/merchants')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_delete = '删除' in body
    log('商家访问商家管理', not has_delete, f'含删除按钮={has_delete}')
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-merchant-merchants.png')

    # 商家创建种草卡（应锁定在自己商家）
    page.goto(BASE + '/seed-cards/create')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    sel_disabled = page.evaluate('''() => {
      const sel = document.querySelector('select');
      return sel ? sel.disabled : null;
    }''')
    log('商家种草卡-商家下拉锁定', sel_disabled is True, f'select disabled={sel_disabled}')

    # 商家 AI 工具页
    page.goto(BASE + '/ai/comment')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    body = page.content()
    log('商家 AI 评论页', 'AI 评论' in body or '评论生成' in body, '')

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
