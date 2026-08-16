"""商家与门店测试：CRUD、禁用、软删、RBAC 作用域。"""
from __future__ import annotations


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_merchant(client, token, name, industry="餐饮", stores=None):
    payload = {
        "name": name,
        "industry": industry,
        "address": "addr",
        "contact": "c",
        "phone": "1",
    }
    if stores is not None:
        payload["stores"] = stores
    return await client.post(
        "/api/merchant/create", headers=_auth(token), json=payload
    )


async def test_create_merchant_with_stores(client, admin_token):
    r = await _create_merchant(
        client,
        admin_token,
        "火锅店",
        stores=[{"name": "总店", "location": "a", "video_account": "v"}],
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["id"]
    assert d["stores"]
    assert d["stores"][0]["name"] == "总店"
    assert d["status"] == "active"


async def test_list_merchant(client, admin_token):
    await _create_merchant(client, admin_token, "店A")
    r = await client.get("/api/merchant/list", headers=_auth(admin_token))
    assert r.status_code == 200
    d = r.json()["data"]
    assert "items" in d and "total" in d
    assert d["total"] >= 1


async def test_get_merchant(client, admin_token):
    mid = (await _create_merchant(client, admin_token, "店B")).json()["data"]["id"]
    r = await client.get(f"/api/merchant/{mid}", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["data"]["id"] == mid


async def test_update_merchant(client, admin_token):
    mid = (await _create_merchant(client, admin_token, "店C")).json()["data"]["id"]
    r = await client.put(
        f"/api/merchant/{mid}",
        headers=_auth(admin_token),
        json={"contact": "新联系人"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["contact"] == "新联系人"


async def test_disable_merchant(client, admin_token):
    mid = (await _create_merchant(client, admin_token, "店D")).json()["data"]["id"]
    r = await client.post(
        f"/api/merchant/{mid}/disable",
        headers=_auth(admin_token),
        json={"disabled": True},
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "disabled"
    r2 = await client.post(
        f"/api/merchant/{mid}/disable",
        headers=_auth(admin_token),
        json={"disabled": False},
    )
    assert r2.json()["data"]["status"] == "active"


async def test_soft_delete_merchant(client, admin_token):
    mid = (await _create_merchant(client, admin_token, "店E")).json()["data"]["id"]
    r = await client.delete(f"/api/merchant/{mid}", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "deleted"
    # 详情 404
    r2 = await client.get(f"/api/merchant/{mid}", headers=_auth(admin_token))
    assert r2.status_code == 404
    # 列表不出现
    r3 = await client.get("/api/merchant/list", headers=_auth(admin_token))
    ids = [m["id"] for m in r3.json()["data"]["items"]]
    assert mid not in ids


async def test_merchant_rbac_scope(client, admin_token, register_user, make_token):
    m1 = (await _create_merchant(client, admin_token, "M1")).json()["data"]["id"]
    m2 = (await _create_merchant(client, admin_token, "M2")).json()["data"]["id"]
    u = await register_user("merch1", role="merchant", merchant_id=m1)
    tok = make_token(u)
    h = _auth(tok)

    r = await client.get("/api/merchant/list", headers=h)
    ids = [m["id"] for m in r.json()["data"]["items"]]
    assert m1 in ids
    assert m2 not in ids

    r2 = await client.get(f"/api/merchant/{m1}", headers=h)
    assert r2.status_code == 200

    r3 = await client.get(f"/api/merchant/{m2}", headers=h)
    assert r3.status_code == 404


async def test_disable_requires_admin(client, admin_token, register_user, make_token):
    mid = (await _create_merchant(client, admin_token, "店F")).json()["data"]["id"]
    u = await register_user("merch2", role="merchant", merchant_id=mid)
    tok = make_token(u)
    r = await client.post(
        f"/api/merchant/{mid}/disable",
        headers=_auth(tok),
        json={"disabled": True},
    )
    assert r.status_code == 403
    assert r.json()["code"] == 403
