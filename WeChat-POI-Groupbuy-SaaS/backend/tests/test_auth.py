"""认证测试：wx-login / web-login 各角色 / 错误密码。"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def test_wx_login_returns_consumer_token(api):
    resp = await api.client.post("/api/v1/auth/wx-login", json={"code": "test_code_1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["user"]["role"] == "consumer"
    token = body["data"]["token"]
    # 消费者 token 可访问自身订单列表
    r = await api.client.get("/api/v1/orders", headers=auth_header(token))
    assert r.status_code == 200


async def test_web_logins_roles(api):
    mapping = {
        "admin": "platform_operator",
        "merchant": "merchant_owner",
        "manager": "store_manager",
        "verifier": "verifier",
    }
    for username, expected_role in mapping.items():
        token = await login(api.client, username, f"{username}123")
        r = await api.client.get("/api/v1/auth/wx-login", headers=auth_header(token))
        # wx-login 不需鉴权；改用 token 解析：直接断言登录返回的 role
        # 重新登录并检查（web-login 返回 user.role）
        resp = await api.client.post(
            "/api/v1/auth/web-login",
            json={"username": username, "password": f"{username}123"},
        )
        assert resp.json()["data"]["user"]["role"] == expected_role


async def test_bad_password_rejected(api):
    resp = await api.client.post(
        "/api/v1/auth/web-login", json={"username": "admin", "password": "wrong"}
    )
    # 认证失败返回 401 + 业务码 1001（统一响应体 code 非 0）
    assert resp.status_code == 401
    assert resp.json()["code"] == 1001


async def test_missing_token_rejected(api):
    resp = await api.client.get("/api/v1/orders")
    assert resp.json()["code"] == 1001
