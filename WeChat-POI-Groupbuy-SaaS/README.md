# 微信视频号 POI 团购 SaaS

面向本地生活商家的微信生态团购 SaaS：多商户多门店 + 团购套餐 + 小程序下单/微信支付(Mock) + 扫码核销（幂等防重）+ 外卖自提 + 预约订座 + 视频号挂载 + 数据看板 + 独立 Web 管理后台。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0（异步）+ Pydantic v2 + SQLite/PostgreSQL + JWT + bcrypt + Alembic |
| 小程序 | 微信原生小程序（Native），`wx.login` / `wx.requestPayment` / `wx.scanCode` |
| Web 后台 | React 18 + Vite 5 + TypeScript + Tailwind 3（独立工程，同源或 CORS 连后端） |
| 多租户 | `TenantContext` 由 JWT 注入，查询层 `tenant_filter()` 自动加 merchant/store 隔离；5 角色 RBAC |
| 外部能力 | 支付 / 地图 POI / 通知三类 Provider 抽象，环境变量切换 `mock` / `real`（默认 mock） |

## 目录结构

```
WeChat-POI-Groupbuy-SaaS/
├── backend/                 # FastAPI 后端
│   ├── app/                 # api / core / models / schemas / services
│   ├── scripts/seed.py      # 建表 + 演示种子数据
│   ├── tests/               # pytest（23 用例）
│   └── alembic/             # 数据库迁移
├── miniprogram/             # 微信小程序（C 端）
├── web-admin/               # React 管理后台（商户/平台）
├── docs/                    # PRD / 架构设计 / 交付总结
└── scripts/                 # 启动与自启脚本（工作区级，见 AI-local 根目录 scripts/）
```

## 快速开始

### 1. 后端

```bash
cd backend
cp .env.example .env          # 按需改 JWT_SECRET / SERVER_PORT / Mock 开关
# 创建表 + 演示种子数据（幂等）
python -m scripts.seed
# 启动（默认 8000；与其他服务冲突时改 SERVER_PORT 或 uvicorn --port 8001）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 健康检查
curl http://127.0.0.1:8000/api/health
```

### 2. Web 管理后台（开发 / 分离模式）

```bash
cd web-admin
npm install
npm run dev                   # http://localhost:5173
# API 基址默认 http://localhost:8000/api/v1（可改 .env 的 VITE_API_BASE）
```

### 3. 单服务部署（后端托管前端，推荐）

```bash
cd web-admin
VITE_API_BASE=/api/v1 npm run build   # 构建为同源调用（dist 已就绪）
cd ../backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 浏览器访问 http://localhost:8000 即管理后台，API 同在 /api/v1
```

> 单服务模式下 `WEB_ADMIN_DIST` 留空即自动取 `../web-admin/dist`。

### 4. 测试

```bash
cd backend
python -m pytest -q           # 23 passed, 0 warning
```

## 演示账号（seed 生成）

| 角色 | 账号 | 密码 |
|---|---|---|
| 平台运营 | admin | admin123 |
| 商户主 | merchant | merchant123 |
| 门店经理 | manager | manager123 |
| 核销员 | verifier | verifier123 |

## 核心能力（P0 + P1 全量）

- 团购套餐上架 / 列表 / 详情 / 上下架（库存、有效期、适用门店）
- 小程序下单 + 微信支付（Mock）+ 支付回调 + 订单状态流转
- 扫码 / 输码核销：全局唯一核销码 + 行级幂等（重复核销返回 `4001`）
- 退款流程（含库存回滚、重复退款拦截）
- 多商户 / 多门店管理，多租户数据隔离，5 角色 RBAC
- 外卖自提状态机（preparing → ready → picked_up）
- 预约订座（pending → confirmed → arrived/cancelled/released，时段容量）
- 视频号挂载绑定（VideoChannelBinding）
- 数据看板（销量 / GMV / 核销率 / 自提转化 / 内容引流 / 订座转化）
- 统一响应 `{code, message, data}`

## Mock 说明

默认 `WECHAT_PAY_PROVIDER=mock` / `MAP_POI_PROVIDER=mock` / `WECHAT_NOTIFY_PROVIDER=mock`，
无任何微信/腾讯凭证即可完整演示。凭证就绪后改 `.env` 为 `=real` 并填入对应 Key 即切换真实调用（代码已抽象，无需改逻辑）。

## 已知待办（非阻断）

1. **P2 功能按设计未做**：小红书内容分发、营销活动、消息通知中心、平台分账。
2. **订单接口返回结构**：`POST /orders` 返回 `data={order, pay_params}`，其余订单接口返回裸 order；两端当前各自匹配、无解析 bug。
3. **端口**：本机 8000 常被其他项目占用时，用 `SERVER_PORT` 或 `uvicorn --port 8001` 错开。

详细交付信息见 `docs/03-交付总结报告-2026-08-14.md`。
