#!/bin/sh
# 容器启动入口：迁移建表 -> 幂等种子 -> 启动 gunicorn
set -e

echo "[entrypoint] 执行数据库迁移..."
alembic upgrade head || echo "[entrypoint] alembic 未执行，依赖 create_all 兜底"

echo "[entrypoint] 初始化种子数据（幂等）..."
python -m scripts.seed || echo "[entrypoint] seed 跳过"

echo "[entrypoint] 启动服务..."
exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2 app.main:app
