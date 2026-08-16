"""分页 total 回归测试：校验列表接口的 total 字段等于真实过滤后行数。

背景：列表接口曾使用 `select(func.count(Model.id)).select_from(stmt.subquery())` 写法，
会触发 SQLAlchemy 的 SAWarning（cartesian product）误报。经验证：
- 实际执行时 ORM 会把 Model.id 适配到子查询列，count 结果始终正确（无正确性缺陷）；
- 当前源码（orders/tenants/catalog/fulfillment 的列表 total）已统一改为
  `select(func.count()).select_from(subquery)`，彻底消除该警告。
本测试作为回归护栏，确保 total 与 list 长度一致（不被错误放大）。
"""
from __future__ import annotations

from tests.conftest import auth_header, login


async def test_store_list_total_matches_filtered_count(api):
    """商户 A 仅 1 家门店（门店 B 属商户 B，应被租户过滤排除）。total 须 == 1。"""
    token_a = await login(api.client, "merchant", "merchant123")
    resp = await api.client.get(
        "/api/v1/tenants/stores", headers=auth_header(token_a)
    )
    assert resp.json()["code"] == 0
    data = resp.json()["data"]
    assert len(data["list"]) == 1
    # total 必须等于过滤后的真实行数（曾因笛卡尔积误报告警，但结果始终正确）
    assert data["total"] == len(data["list"]) == 1
    assert data["list"][0]["id"] == api.ids["store_id"]
