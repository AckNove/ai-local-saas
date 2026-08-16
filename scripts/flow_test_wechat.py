# -*- coding: utf-8 -*-
"""WeChat-POI 商家上线全流程 API 级验证
流程：平台登录 → 建商户 → 建门店(未配置POI) → 门店配置地图POI → 视频号绑定 → 创建2个套餐(含图片JSON) → 上架 → 消费者浏览/下单 → 核销
"""
import sys, io, json, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'http://127.0.0.1:8001'
results = []

def call(method, path, body=None, token=None, expect=None):
    url = BASE + path
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read().decode('utf-8'))
            ok = expect is None or resp.get('code') == expect
            results.append({'step': f'{method} {path}', 'ok': ok, 'code': resp.get('code'), 'msg': resp.get('message'), 'data': resp.get('data')})
            print(f"[{'PASS' if ok else 'FAIL'}] {method} {path} -> code={resp.get('code')} msg={resp.get('message')}")
            return resp
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode('utf-8', errors='replace')
        ok = False
        results.append({'step': f'{method} {path}', 'ok': ok, 'http': e.code, 'body': body_txt[:200]})
        print(f"[FAIL] {method} {path} -> HTTP {e.code} {body_txt[:150]}")
        return None

# 1. 平台登录
login = call('POST', '/api/v1/auth/web-login', {'username': 'admin', 'password': 'admin123'}, expect=0)
if not login:
    sys.exit(1)
admin_tok = login['data']['token']

# 2. 创建商户
m = call('POST', '/api/v1/tenants/merchants', {'name': '体验测试餐饮集团', 'contact_phone': '13800000001', 'logo_url': 'https://example.com/logo.png'}, admin_tok, expect=0)
merchant_id = m['data']['id'] if m else None
print('   merchant_id =', merchant_id)

# 3. 创建门店（未配置 POI——模拟"尚未配置地图定位"）
s = call('POST', '/api/v1/tenants/stores', {'merchant_id': merchant_id, 'name': '体验测试店·天河店', 'address': '广州市天河区体育西路1号', 'phone': '020-88888888', 'business_hours': '10:00-22:00'}, admin_tok, expect=0)
store_id = s['data']['id'] if s else None
print('   store_id =', store_id, ' poi_id =', s['data']['poi_id'] if s else None)

# 4. 门店配置地图 POI（模拟地图定位上线）
p = call('PATCH', f'/api/v1/tenants/stores/{store_id}', {'poi_id': 'POI-TEST-001', 'poi_name': '体验测试店(天河店)', 'lng': 113.3214, 'lat': 23.1300}, admin_tok, expect=0)

# 5. 视频号挂载绑定（含 POI）
v = call('POST', '/api/v1/fulfillment/video-bindings', {'store_id': store_id, 'video_account_id': 'vlog_test_888', 'poi_id': 'POI-TEST-001'}, admin_tok, expect=0)

# 6. 创建套餐1（含图片）
pkg1 = call('POST', '/api/v1/catalog/packages', {
    'name': '双人火锅套餐', 'description': '含锅底+肥牛+时蔬+饮料',
    'original_price': 16800, 'group_price': 9900, 'stock': 100,
    'store_ids': [store_id],
    'images_json': json.dumps({'images': ['https://example.com/pkg1-1.jpg', 'https://example.com/pkg1-2.jpg']}),
}, admin_tok, expect=0)

# 7. 创建套餐2
pkg2 = call('POST', '/api/v1/catalog/packages', {
    'name': '四人欢聚套餐', 'description': '含锅底×2+肥牛×2+虾滑+甜品',
    'original_price': 32800, 'group_price': 19900, 'stock': 50,
    'store_ids': [store_id],
    'images_json': json.dumps({'images': ['https://example.com/pkg2-1.jpg']}),
}, admin_tok, expect=0)

# 8. 上架两个套餐
if pkg1:
    call('POST', f"/api/v1/catalog/packages/{pkg1['data']['id']}/publish", {}, admin_tok, expect=0)
if pkg2:
    call('POST', f"/api/v1/catalog/packages/{pkg2['data']['id']}/publish", {}, admin_tok, expect=0)

# 9. 消费者视角：wx-login → 浏览已上架套餐
wl = call('POST', '/api/v1/auth/wx-login', {'code': 'consumer-test-code'}, expect=0)
consumer_tok = wl['data']['token'] if wl else None
pkgs = call('GET', '/api/v1/catalog/packages', None, consumer_tok, expect=0)
if pkgs:
    print('   consumer sees published packages:', [(p['name'], p['group_price']) for p in pkgs['data']['list']])

# 10. 消费者下单 + 支付 + 核销（平台账号可跨门店核销）
if pkg1 and consumer_tok:
    pid = pkg1['data']['id']
    o = call('POST', '/api/v1/orders', {'package_id': pid, 'quantity': 1, 'store_id': store_id, 'fulfillment_type': 'dine_in'}, consumer_tok, expect=0)
    if o:
        order_no = o['data']['order']['order_no']
        call('POST', f'/api/v1/orders/{order_no}/pay-notify', {'result': 'success', 'transaction_id': 'TEST20260815A'}, expect=0)
        # 平台 admin 核销（可跨门店；verifier 仅限本店）
        od = call('GET', f'/api/v1/orders/{order_no}', None, consumer_tok, expect=0)
        if od and od['data'].get('verification_codes'):
            code = od['data']['verification_codes'][0]['code']
            call('POST', '/api/v1/verify', {'code': code}, admin_tok, expect=0)
            # 重复核销应 4001
            call('POST', '/api/v1/verify', {'code': code}, admin_tok, expect=4001)

print('\n===== SUMMARY =====')
fails = [r for r in results if not r.get('ok')]
print(f"total={len(results)} pass={len(results)-len(fails)} fail={len(fails)}")
for f in fails:
    print('FAILED:', json.dumps(f, ensure_ascii=False))
