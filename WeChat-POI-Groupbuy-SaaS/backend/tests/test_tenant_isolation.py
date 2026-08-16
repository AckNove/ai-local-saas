"""跨租户隔离测试：商户 A token 访问商户 B 资源须 2002。"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def test_merchant_cannot_access_other_merchant_store(api):
    token_a = await login(api.client, "merchant", "merchant123")
    store_b = api.ids["store_b_id"]
    resp = await api.client.get(
        f"/api/v1/tenants/stores/{store_b}", headers=auth_header(token_a)
    )
    assert resp.status_code == 200
    assert resp.json()["code"] == 2002  # 跨租户拒绝


async def test_merchant_cannot_access_other_merchant(api):
    token_a = await login(api.client, "merchant", "merchant123")
    merchant_b = api.ids["merchant_b_id"]
    resp = await api.client.get(
        f"/api/v1/tenants/merchants/{merchant_b}", headers=auth_header(token_a)
    )
    assert resp.json()["code"] == 2002


async def test_verifier_cannot_access_other_store(api):
    token_v = await login(api.client, "verifier", "verifier123")
    store_b = api.ids["store_b_id"]
    resp = await api.client.get(
        f"/api/v1/tenants/stores/{store_b}", headers=auth_header(token_v)
    )
    assert resp.json()["code"] == 2002


async def test_merchant_sees_own_store(api):
    token_a = await login(api.client, "merchant", "merchant123")
    resp = await api.client.get(
        "/api/v1/tenants/stores", headers=auth_header(token_a)
    )
    assert resp.json()["code"] == 0
    store_ids = [s["id"] for s in resp.json()["data"]["list"]]
    assert api.ids["store_id"] in store_ids
    assert api.ids["store_b_id"] not in store_ids
