# AI-local 工作区

本工作区包含两个 SaaS 项目（同一目录下独立仓库）：

| 项目 | 目录 | 说明 | 端口 | 管理后台 |
|---|---|---|---|---|
| **AI 本地商家增长 SaaS** | `AI-Local-Growth-SaaS/` | 管理员创建商家 → 生成种草卡(二维码) → 消费者扫码落地页 → AI 评论/脚本/诊断 → 数据看板 | **8000** | http://127.0.0.1:8000 |
| **微信视频号 POI 团购 SaaS** | `WeChat-POI-Groupbuy-SaaS/` | 多商户多门店 + 团购套餐 + 小程序下单(Mock支付) + 扫码核销防重 + 自提/订座/看板 + Web 后台 | **8001** | http://127.0.0.1:8001 |

> 端口约定：AI-Local 用 8000；WeChat-POI 用 8001（避免同机冲突）。

---

## 一键启动 / 停止 / 开机自启

工作区根目录下 `scripts/` 提供三个脚本，**双击即可运行**（Windows）：

| 脚本 | 作用 |
|---|---|
| `scripts/start-services.ps1` | 检查并拉起两个后端服务（独立进程，关窗口不中断） |
| `scripts/stop-services.ps1` | 停止两个服务 |
| `scripts/install-autostart.ps1` | 注册计划任务：**用户登录 Windows 后自动启动**两个服务（需管理员权限运行一次） |

常用操作：

```powershell
# 启动（PowerShell）
powershell -ExecutionPolicy Bypass -File D:\桌面\AI-local\scripts\start-services.ps1

# 停止
powershell -ExecutionPolicy Bypass -File D:\桌面\AI-local\scripts\stop-services.ps1

# 开机自启（管理员 PowerShell 运行一次）
powershell -ExecutionPolicy Bypass -File D:\桌面\AI-local\scripts\install-autostart.ps1

# 卸载开机自启
powershell -Command "Unregister-ScheduledTask -TaskName AI-Local-Services -Confirm:$false"
```

服务日志：`D:\桌面\AI-local\logs\`（ai-local-8000.log / wechat-poi-8001.log）。

> 说明：两个后端均为独立 uvicorn 进程（Python venv：
> `C:/Users/25803/.workbuddy/binaries/python/envs/default`）。
> 网站打不开时先跑 `start-services.ps1`；要跨会话常驻请执行 `install-autostart.ps1` 注册开机自启。

---

## 演示账号

**AI 本地商家增长 SaaS**：`admin / admin123`

**微信视频号 POI 团购 SaaS**（seed 生成）：

| 角色 | 账号 | 密码 |
|---|---|---|
| 平台运营 | admin | admin123 |
| 商户主 | merchant | merchant123 |
| 门店经理 | manager | manager123 |
| 核销员 | verifier | verifier123 |

---

## 项目文档入口

- AI-Local：`AI-Local-Growth-SaaS/README.md` + `AI-Local-Growth-SaaS/docs/`
- WeChat-POI：`WeChat-POI-Groupbuy-SaaS/README.md` + `WeChat-POI-Groupbuy-SaaS/docs/`
