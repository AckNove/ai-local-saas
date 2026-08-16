#!/usr/bin/env bash
# 一键启动后端（API + H5 + 可选前端静态托管）
# 用法：bash scripts/start.sh
set -euo pipefail

# 进入脚本所在目录的上一级（项目根），再进入 backend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}/backend"

# 优先使用项目内虚拟环境（若存在）
if [ -x "${PROJECT_ROOT}/.venv/bin/python" ]; then
  PY="${PROJECT_ROOT}/.venv/bin/python"
else
  PY="python"
fi

echo ">>> 初始化数据库与管理员（若尚未创建）"
"$PY" seed_admin.py

echo ">>> 执行 Alembic 迁移（best-effort，失败则回退 create_all）"
"$PY" -m alembic upgrade head 2>/dev/null || alembic upgrade head || echo ">> 迁移跳过，使用 create_all 兜底"

echo ">>> 启动 uvicorn（127.0.0.1:8000）"
exec "$PY" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
