"""集成验证脚本：直接用 FastAPI TestClient 跑通 main:app 的关键路由。

覆盖：
- GET /                        → 200 + index.html（含 <div id="root">）
- GET /assets/<built js>       → 200 + application/javascript
- GET /api/health              → 200 + {code:0}
- POST /api/auth/login(admin)  → 200 + token
- GET /api/merchant/list(Bearer) → 200 + {items,total}
- GET /some/spa/route          → 200 + SPA index 兜底（非 404）

说明：
- 本脚本须从 backend/ 目录运行（DATABASE_URL 默认 sqlite+aiosqlite:///./app.db 为相对路径）。
  先运行 `python seed_admin.py` 建表并写入默认管理员 admin/admin123，再运行本脚本。
- 使用 `with TestClient(main.app) as client:` 触发 lifespan，确保 init_db() 建表（幂等）。

用法（在 backend/ 目录）：
    python seed_admin.py
    python verify_integration.py
"""
from __future__ import annotations

import re
from fastapi.testclient import TestClient

import main  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def main_checks() -> None:
    # 使用 with 触发 lifespan（init_db 建表，幂等）
    with TestClient(main.app) as client:
        # 1) 根路径 SPA
        r = client.get("/")
        ok = r.status_code == 200 and '<div id="root">' in r.text
        check("GET / (SPA index)", ok, f"status={r.status_code}")

        # 2) 静态资源 /assets
        m = re.search(r'/assets/([^"]+\.js)', r.text)
        if m:
            asset = m.group(1)
            ra = client.get(f"/assets/{asset}")
            ok = ra.status_code == 200 and "javascript" in ra.headers.get("content-type", "")
            check(f"GET /assets/{asset}", ok, f"status={ra.status_code} ctype={ra.headers.get('content-type')}")
        else:
            check("GET /assets/<js>", False, "未从 index.html 解析到 asset 路径")

        # 3) 健康检查
        rh = client.get("/api/health")
        ok = rh.status_code == 200 and rh.json().get("code") == 0
        check("GET /api/health", ok, f"status={rh.status_code} body={rh.text[:80]}")

        # 4) 登录
        rl = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        ok = rl.status_code == 200 and bool(rl.json().get("data", {}).get("token"))
        token = rl.json().get("data", {}).get("token", "")
        check("POST /api/auth/login(admin)", ok, f"status={rl.status_code} has_token={bool(token)}")

        # 5) 商家列表（带 token）
        rm = client.get("/api/merchant/list", headers={"Authorization": f"Bearer {token}"})
        ok = rm.status_code == 200 and "items" in rm.json().get("data", {})
        check("GET /api/merchant/list(Bearer)", ok, f"status={rm.status_code} body={rm.text[:80]}")

        # 6) SPA 兜底（前端客户端路由）
        rs = client.get("/dashboard")
        ok = rs.status_code == 200 and '<div id="root">' in rs.text
        check("GET /dashboard (SPA fallback)", ok, f"status={rs.status_code}")


if __name__ == "__main__":
    main_checks()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\nSUMMARY: {passed}/{total} checks passed")
    raise SystemExit(0 if passed == total else 1)
