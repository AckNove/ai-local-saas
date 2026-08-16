# -*- coding: utf-8 -*-
"""WeChat web-admin 完整商家上线 UI 流程测试（含新增商户/员工管理页）"""
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

    # 1. 侧边栏菜单（应含商户管理/员工管理）
    menus = page.locator('nav a').all_inner_texts()
    menu_text = ' '.join(m.strip() for m in menus)
    log('菜单含商户/员工管理', '商户管理' in menu_text and '员工管理' in menu_text, menu_text.replace(chr(10),' '))

    # 2. 商户管理页：新建商户
    page.goto(BASE + '/merchants')
    page.wait_for_load_state('networkidle')
    time.sleep(0.8)
    page.click('button:has-text("新增商户")')
    time.sleep(0.5)
    page.fill('.card input[placeholder*="集团"], .card input:not([type])', 'UI流程测试餐饮')
    # 用 label 定位填表单
    page.evaluate('''() => {
      const labels = [...document.querySelectorAll('label')];
      const setByLabel = (text, val) => {
        const lb = labels.find(l => l.textContent.includes(text));
        if (!lb) return false;
        const inp = lb.nextElementSibling || lb.parentElement.querySelector('input');
        if (!inp) return false;
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(inp, val);
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      };
      setByLabel('商户名称', 'UI流程测试餐饮');
      setByLabel('Logo URL', 'https://example.com/logo.png');
      setByLabel('联系电话', '13800002222');
    }''')
    time.sleep(0.3)
    page.click('button:has-text("保存")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    log('新建商户', 'UI流程测试餐饮' in body, '')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-merchant-manage.png')

    # 3. 员工管理页
    page.goto(BASE + '/staff')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    has_404 = '404' in body or 'Request failed' in body
    log('员工管理页加载', not has_404, f'rows={page.locator("table tbody tr").count()}')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-staff-manage.png')

    # 4. 门店管理页（确认含商户下拉）
    page.goto(BASE + '/stores')
    page.wait_for_load_state('networkidle')
    time.sleep(0.8)
    page.click('button:has-text("新增门店")')
    time.sleep(0.5)
    modal = page.locator('.card:has(input)').inner_text()
    has_merchant_sel = '所属商户' in modal
    log('门店表单含所属商户下拉', has_merchant_sel, '')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-store-modal2.png')
    page.click('button:has-text("取消")')

    browser.close()

print('\n===== SUMMARY =====')
fails = [r for r in results if not r['ok']]
print(f"total={len(results)} pass={len(results)-len(fails)} fail={len(fails)}")
for r in results:
    print(json.dumps(r, ensure_ascii=False))
