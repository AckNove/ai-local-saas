# -*- coding: utf-8 -*-
"""WeChat web-admin 终极 UI 流程：完整商家上线（浏览器真实操作）"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8001'
results = []

def log(step, ok, note=''):
    results.append({'step': step, 'ok': ok, 'note': note})
    print(f"[{'PASS' if ok else 'FAIL'}] {step} - {note}")

def set_by_label(page, text, val):
    return page.evaluate('''([text, val]) => {
      const labels = [...document.querySelectorAll('label')];
      const lb = labels.find(l => l.textContent.includes(text));
      if (!lb) return false;
      const inp = lb.nextElementSibling || lb.parentElement.querySelector('input');
      if (!inp) return false;
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(inp, val);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }''', [text, val])

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

    # 1. 新建商户
    page.goto(BASE + '/merchants')
    page.wait_for_load_state('networkidle')
    time.sleep(0.8)
    page.click('button:has-text("新增商户")')
    time.sleep(0.5)
    set_by_label(page, '商户名称', '浏览器全流程餐厅')
    set_by_label(page, '联系电话', '13800003333')
    page.click('.fixed button:has-text("保存")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    log('浏览器新建商户', '浏览器全流程餐厅' in body, '')

    # 2. 新建门店（含商户下拉）
    page.goto(BASE + '/stores')
    page.wait_for_load_state('networkidle')
    time.sleep(0.8)
    page.click('button:has-text("新增门店")')
    time.sleep(0.5)
    # 选第一个商户（下拉默认已选第一个）
    set_by_label(page, '门店名称', '全流程旗舰店')
    set_by_label(page, '地址', '广州市越秀区北京路10号')
    set_by_label(page, '电话', '020-12345678')
    set_by_label(page, '营业时间', '10:00-22:00')
    set_by_label(page, 'POI 名称', '全流程旗舰店(北京路店)')
    set_by_label(page, 'POI ID', 'POI-UI-888')
    set_by_label(page, '经度 lng', '113.2680')
    set_by_label(page, '纬度 lat', '23.1291')
    page.click('.fixed button:has-text("保存")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.2)
    body = page.content()
    log('浏览器新建门店+POI', '全流程旗舰店' in body, '')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-store-created.png')

    # 3. 视频号绑定
    page.goto(BASE + '/channels')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    # 选门店（默认第一个）
    try:
        page.select_option('select', index=1)
    except Exception:
        pass
    page.fill('input[placeholder*="vlog"]', 'vlog_ui_test')
    page.click('button:has-text("绑定")')
    page.wait_for_load_state('networkidle')
    time.sleep(1.2)
    body = page.content()
    log('浏览器视频号绑定', 'vlog_ui_test' in body, '')
    page.screenshot(path='D:/桌面/AI-local/logs/wechat-channel-bound.png')

    browser.close()

print('\n===== SUMMARY =====')
fails = [r for r in results if not r['ok']]
print(f"total={len(results)} pass={len(results)-len(fails)} fail={len(fails)}")
for r in results:
    print(json.dumps(r, ensure_ascii=False))
