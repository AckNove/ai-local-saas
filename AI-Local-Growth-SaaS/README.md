# AI 本地商家增长 SaaS 系统

面向本地实体商家的增长 SaaS：管理员创建商家 → 生成「种草卡」(二维码/NFC) → 消费者扫码落地页跳转视频号并上报互动事件 → 后台查看数据 → AI 生成评论 / 脚本 / 诊断报告。MVP 可**离线、无 API Key** 完整演示。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0（异步）+ Pydantic v2 + PyJWT + bcrypt + segno + httpx |
| 数据 | SQLite 默认（零依赖）；生产经 `DATABASE_URL` 切 PostgreSQL |
| 前端 | React 18 + Vite 5 + TypeScript + Tailwind 3 + react-router-dom 6 + axios |
| AI | `LLMProvider` 抽象 + `MockProvider` 离线兜底（默认）+ OpenAI / DeepSeek Provider |
| 部署 | 单 `uvicorn` 同时托管 API + 后台静态页 + 消费者 H5；可选 docker-compose |

## 目录结构

```
AI-Local-Growth-SaaS/
├── backend/                 # FastAPI 后端（API + H5 + 静态托管）
│   ├── main.py              # 应用入口：路由挂载、frontend/dist 托管、H5
│   ├── config.py            # 环境变量配置
│   ├── seed_admin.py        # 初始化管理员
│   ├── app/                 # 业务代码（api / services / models / schemas / agents / utils）
│   └── requirements.txt
├── frontend/                # React 管理后台（本仓库前端实现）
│   ├── src/
│   │   ├── api/             # axios 封装与各模块请求
│   │   ├── components/      # ui（手写 Shadcn 风格）+ layout + MerchantForm
│   │   ├── hooks/           # useAuth / useMerchants / useSeedCards
│   │   ├── pages/           # 登录 / 概览 / 商家 / 种草卡 / AI 工具
│   │   └── utils/           # cn / toast
│   └── dist/                # 构建产物（由后端托管）
├── h5/                      # 消费者扫码落地页（纯静态，由后端 serve）
├── docker/                  # 可选：Dockerfile / docker-compose.yml / .dockerignore
├── docs/                    # 需求 / 评审 / 任务拆解文档
├── scripts/start.sh         # 一键启动脚本
└── README.md
```

## 环境要求

- Python ≥ 3.10（建议 3.11+）
- Node.js ≥ 18（建议 20+）
- 可联网安装依赖（npm 源已配置 npmmirror）

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python seed_admin.py            # 初始化管理员（幂等）
python main.py                  # 或：uvicorn main:app --host 0.0.0.0 --port 8000
```

启动后：
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health
- 默认管理员账号：**admin / admin123**

> 后端会自动托管 `frontend/dist`（若存在）与 `h5/`；单进程同时提供 API 与前端。

### 2. 前端（构建后由后端托管）

```bash
cd frontend
npm install
npm run build                  # 产出 frontend/dist
```

构建完成后，直接访问 http://127.0.0.1:8000/  即可使用管理后台（与 API 同源）。

> 本地联调可选：`npm run dev` 启动 Vite（默认 5173），其 `server.proxy` 已将 `/api` 代理到 `http://127.0.0.1:8000`。

### 3. 一键启动（推荐）

```bash
bash scripts/start.sh          # 初始化管理员 + 启动 uvicorn
```

## AI Mock 说明

默认 `LLM_PROVIDER=mock`，无需任何 API Key 即可返回结构化结果（评论 / 脚本 / 诊断报告）。
配置真实 Key 后自动切换（DeepSeek 优先使用专用 Key，不硬编码）：

```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxx          # DeepSeek 专用 Key（推荐）
# LLM_API_KEY=sk-xxx              # 旧版通用 Key 仍可作为回退
```

`deepseek_provider` 默认 `https://api.deepseek.com` + `deepseek-chat`，
并对模型输出做容错 JSON 解析；任何异常自动降级到 Mock（ai_task 仍记为 done）。

所有 AI 调用均落库 `ai_task`（`pending → running → done/failed`），无 Key 也能离线演示。

## 环境变量

后端：复制 `backend/.env.example` 为 `backend/.env`（`.env` 不入库）。
前端：复制 `frontend/.env.example` 为 `frontend/.env`。
根目录 `.env.example` 汇总了主要变量，供参考。

关键变量：
- `DATABASE_URL`：默认 `sqlite+aiosqlite:///./app.db`，生产切 PG
- `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_BASE_URL`：AI 提供方
- `JWT_SECRET` / `JWT_EXPIRE_MINUTES`：鉴权
- `PUBLIC_BASE_URL`：生成二维码落地页绝对 URL 的基址
- `VITE_API_BASE`（前端）：API 基地址，默认 `/api`（同源）

## 统一接口结构

所有业务接口返回：

```json
{ "code": 0, "message": "ok", "data": {} }
```

`code`：0 成功；401 未认证；403 无权限；404 不存在；422 参数错误；500 服务器错误。
列表类 `data` 含 `items` 与 `total`。

## API 索引

| 模块 | 方法 & 路径 | 说明 |
|---|---|---|
| 认证 | `POST /api/auth/login` | 登录，返回 JWT 与用户信息 |
| 认证 | `GET /api/user/profile` | 当前用户信息 |
| 商家 | `POST /api/merchant/create` | 创建商家（含门店） |
| 商家 | `GET /api/merchant/list` | 商家列表（分页 / 关键词） |
| 商家 | `GET /api/merchant/{id}` | 商家详情 + 门店 |
| 商家 | `PUT /api/merchant/{id}` | 更新商家 |
| 商家 | `POST /api/merchant/{id}/disable` | 禁用 / 启用 |
| 商家 | `DELETE /api/merchant/{id}` | 软删除 |
| 种草卡 | `POST /api/seed-card/create` | 创建种草卡（生成 slug + 二维码） |
| 种草卡 | `GET /api/seed-card/list` | 种草卡列表 |
| 种草卡 | `GET /api/seed-card/{id}` | 种草卡详情 |
| 种草卡 | `GET /api/seed-card/{id}/qrcode` | 二维码 PNG |
| 种草卡 | `POST /api/seed-card/event` | 事件上报（来自 H5，公开） |
| 统计 | `GET /api/stats/overview` | 平台 / 商家数据概览 |
| AI | `POST /api/ai/comment` | AI 评论生成 |
| AI | `POST /api/ai/report` | AI 商家诊断 |
| AI | `POST /api/ai/content` | AI 脚本 / 文案生成 |
| 系统 | `GET /api/health` | 健康检查 |
| H5 | `GET /c/{slug}` | 消费者扫码落地页 |

## 部署（生产）

> ⚠️ 说明：当前交付的是**可部署产物 + 步骤**。沙箱环境无法托管长期运行、可被公网访问的服务器；请在自有服务器 / 云主机 / K8s 上按以下步骤部署。

### 方式一：Docker Compose（推荐，含 PostgreSQL + gunicorn）

```bash
# 1) 在仓库根目录准备环境变量（参考根 .env.example）
cp .env.example .env
# 至少修改：JWT_SECRET(≥32位随机串)、DEEPSEEK_API_KEY、CORS_ORIGINS、POSTGRES_PASSWORD

# 2) 启动（app + PostgreSQL + Redis）
docker compose -f docker/docker-compose.yml up --build -d
```

- `DATABASE_URL` 已由 Compose 指向栈内 PostgreSQL（`postgresql+asyncpg://...`）。
- 容器启动时自动执行 `alembic upgrade head` 迁移（失败则回退 `create_all` 兜底）。
- API 由 **gunicorn + UvicornWorker** 多进程托管，端口 8000。
- 访问 http://<服务器IP>:8000/ 使用管理后台；默认管理员 admin / admin123（请尽快改密）。

### 方式二：裸机 / 虚拟环境

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # 修改 JWT_SECRET / DEEPSEEK_API_KEY / DATABASE_URL 等
python seed_admin.py            # 初始化管理员（幂等）
alembic upgrade head            # 执行迁移（全新库；已有库可跳过，create_all 兜底）
bash scripts/start.sh           # 启动（含迁移步骤）：uvicorn 0.0.0.0:8000
```

### 关键生产环境变量

| 变量 | 说明 |
|---|---|
| `DATABASE_URL` | 默认 SQLite；生产切 `postgresql+asyncpg://user:pwd@host/db`（需 asyncpg） |
| `LLM_PROVIDER` | `mock` / `openai` / `deepseek` |
| `DEEPSEEK_API_KEY` | DeepSeek 专用 Key（不硬编码；缺省回退 `LLM_API_KEY`） |
| `JWT_SECRET` | **务必改成 ≥32 位随机串** |
| `CORS_ORIGINS` | 逗号分隔域名，**生产勿用 `*`** |
| `PUBLIC_BASE_URL` | 部署域名，用于生成落地页绝对 URL |

### 数据库迁移（Alembic）

迁移用于**全新部署**；现有 `app.db`（由 `create_all` 创建）的数据不受影响——迁移只对空库执行。

```bash
alembic upgrade head             # 升级到最新
alembic downgrade base           # 回滚（仅全新库，会删表）
alembic history                  # 查看迁移链
```

`init_db()` 中的 `create_all` 保留作为兜底，确保无 Alembic 也能启动。
