# 多阶段构建：前端构建 + 后端运行
# 最终镜像单进程 uvicorn 同时托管 API 与 frontend/dist

# ---------- 阶段 1：构建前端 ----------
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---------- 阶段 2：运行后端 ----------
FROM python:3.11-slim AS backend-runner
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 换用阿里云 Debian 源（国内服务器加速）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
# pip 用阿里云源加速
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r backend/requirements.txt

COPY backend/ ./backend/
# 复制前端构建产物到 backend 期望的 ../frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY h5/ ./h5/
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/backend

EXPOSE 8000
# 运行时入口：迁移 -> 种子（连 PostgreSQL，幂等）-> 启动 gunicorn
ENTRYPOINT ["/entrypoint.sh"]
