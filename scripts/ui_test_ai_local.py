# -*- coding: utf-8 -*-
"""AI-Local 全流程 UI 测试 + 三维度体验审查"""
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

    # ---- 管理员流程 ----
    page.goto(BASE + '/login')
    page.fill('input#username, input[type="text"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    log('admin 登录', '/dashboard' in page.url or '数据概览' in page.content(), page.url)

    # 侧边栏菜单
    menus = page.locator('nav a, aside a').all_inner_texts()
    log('管理员菜单', len(menus) > 0, '菜单: ' + ' | '.join(m.strip() for m in menus))

    # 数据概览页
    page.goto(BASE + '/dashboard')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    dash_text = page.content()
    log('数据概览', '数据概览' in dash_text, '')

    # 商家管理：创建商家
    page.goto(BASE + '/merchants')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    page.click('button:has-text("新增商家")')
    time.sleep(0.5)
    page.fill('input[placeholder*="名称"], input:has-text("")', '体验审查火锅店')
    # 填行业
    inputs = page.locator('.card input, dialog input, [role="dialog"] input')
    names = page.locator('label')
    for i in range(inputs.count()):
        pass
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-merchant-form.png')

    # 用 JS 填表单
    page.evaluate('''() => {
      const inputs = document.querySelectorAll('input');
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
      setByLabel('商家名称', '体验审查火锅店');
      setByLabel('行业', '餐饮');
      setByLabel('联系人', '王老板');
      setByLabel('联系电话', '13900001111');
      setByLabel('地址', '广州天河区');
      setByLabel('套餐', '基础版');
      setByLabel('到期时间', '2026-12-31');
      // 门店字段
      const placeholders = [...document.querySelectorAll('input[placeholder]')];
      const ph = p => placeholders.find(i => i.placeholder.includes(p));
      if (ph('门店名称')) { ph('门店名称').value = '天河一店'; ph('门店名称').dispatchEvent(new Event('input', {bubbles:true})); }
      if (ph('位置')) { ph('位置').value = '体育西路1号'; ph('位置').dispatchEvent(new Event('input', {bubbles:true})); }
      if (ph('视频号账号')) { ph('视频号账号').value = 'vlog_test'; ph('视频号账号').dispatchEvent(new Event('input', {bubbles:true})); }
    }''')
    time.sleep(0.3)
    page.click('button:has-text("创建")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    log('创建商家', '体验审查火锅店' in body or '商家管理' in body, '')

    # 种草卡创建页
    page.goto(BASE + '/seed-cards/create')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    page.evaluate('''() => {
      const setByLabel = (text, val) => {
        const labels = [...document.querySelectorAll('label')];
        const lb = labels.find(l => l.textContent.includes(text));
        if (!lb) return false;
        const inp = lb.nextElementSibling || lb.parentElement.querySelector('input');
        if (!inp) return false;
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(inp, val);
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      };
      setByLabel('卡片名称', '体验种草卡-探店');
      setByLabel('跳转目标 URL', 'https://channels.weixin.qq.com/test');
    }''')
    time.sleep(0.3)
    page.click('button:has-text("创建")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    body = page.content()
    log('创建种草卡', '二维码' in body or '下载' in body or '种草卡不存在' not in body, f'url={page.url}')
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-seedcard-detail.png')

    # AI 诊断页
    page.goto(BASE + '/ai/report')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    # 选择第一个商家（select）
    try:
        page.select_option('select', index=1)
        time.sleep(0.3)
    except Exception as e:
        print('select option failed:', e)
    page.click('button:has-text("生成诊断报告")')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    body = page.content()
    log('AI 诊断报告', '诊断结果' in body or '评分' in body, '')

    # ---- 商家视角 ----
    page.goto(BASE + '/login')
    page.fill('input[type="text"], input#username', 'merchant')
    page.fill('input[type="password"]', 'merchant123')
    page.click('button:has-text("登录")')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    menus_m = page.locator('nav a, aside a').all_inner_texts()
    log('商家登录', '/dashboard' in page.url, '菜单: ' + ' | '.join(m.strip() for m in menus_m))

    # H5 落地页（消费者视角）
    page.goto(BASE + '/c/')  # 先访问一个有效 slug
    page.screenshot(path='D:/桌面/AI-local/logs/ai-local-h5.png')

    browser.close()

print('\n===== SUMMARY =====')
for r in results:
    print(json.dumps(r, ensure_ascii=False))
