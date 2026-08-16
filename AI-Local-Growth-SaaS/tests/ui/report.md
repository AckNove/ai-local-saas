# 管理后台 UI 自动化测试报告

- 生成时间：2026-08-13T02:04:42
- 测试地址：http://127.0.0.1:8000
- 用例总数：**10**　通过：**10**　失败：**0**

## 用例明细

| 用例 | 结果 | 说明 | 截图 |
| --- | --- | --- | --- |
| 登录 | PASS | 已使用 admin 登录并跳转 /dashboard | [截图](screenshots\01_login_dashboard.png) |
| 数据概览渲染 | PASS | 侧边栏与主体已渲染，登录按钮已消失 | [截图](screenshots\02_dashboard.png) |
| 创建商家 | PASS | 已创建商家「E2E商家_1786557875」并出现在列表 | [截图](screenshots\03_merchant_created.png) |
| 创建种草卡 | PASS | 已创建种草卡「E2E种草卡_1786557875」并跳转详情页 | [截图](screenshots\04_seedcard_created.png) |
| 生成二维码 | PASS | 种草卡二维码已成功渲染（PNG） | [截图](screenshots\05_qrcode.png) |
| AI 评论生成 | PASS | AI 已返回评论结果并渲染结果卡片 | [截图](screenshots\06_ai_comment.png) |
| 页面渲染::AI 诊断报告 | PASS | AI 诊断报告 页面已渲染 | [截图](screenshots\07_page_ai_report.png) |
| 页面渲染::AI 内容生成 | PASS | AI 内容生成 页面已渲染 | [截图](screenshots\07_page_ai_content.png) |
| 页面渲染::商家管理 | PASS | 商家管理 页面已渲染 | [截图](screenshots\07_page_merchants.png) |
| 页面渲染::种草卡管理 | PASS | 种草卡管理 页面已渲染 | [截图](screenshots\07_page_seed-cards.png) |

## 结论

✅ 全部核心路径通过，管理后台可正常使用。
