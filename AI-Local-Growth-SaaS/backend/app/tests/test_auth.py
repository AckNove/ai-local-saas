"""认证相关测试：登录、错误密码、鉴权、统一结构。"""
from __future__ import annotations


async def test_login_success(client, admin_token):
    # admin_token 已确保管理员存在；验证登录可返回 token 与角色
    r = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    assert body["data"]["token"]
    assert body["data"]["user"]["role"] == "admin"
    assert body["data"]["token_type"] == "bearer"


async def test_login_wrong_password(client, admin_user):
    r = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert r.status_code == 401
    assert r.json()["code"] == 401


async def test_profile_requires_token(client):
    r = await client.get("/api/user/profile")
    assert r.status_code == 401
    assert r.json()["code"] == 401


async def test_profile_with_token(client, admin_token):
    r = await client.get(
        "/api/user/profile", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    # datetime 字段应可被序列化（曾因 JSONResponse 不支持 tz-aware datetime 而 500）
    assert "created_at" in data


async def test_login_missing_field_422(client):
    # 缺少 password -> 422 参数错误
    r = await client.post("/api/auth/login", json={"username": "admin"})
    assert r.status_code == 422
    assert r.json()["code"] == 422
