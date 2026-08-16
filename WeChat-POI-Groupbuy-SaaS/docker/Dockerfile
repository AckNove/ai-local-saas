# 微信视频号 POI 团购 SaaS — 服务器部署 Dockerfile（多阶段）
# 阶段1：构建 web-admin 前端
FROM node:20-slim AS admin-builder
WORKDIR /app/web-admin
COPY web-admin/package.json web-admin/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY web-admin/ ./
RUN VITE_API_BASE=/api/v1 npm run build

# 阶段2：运行后端（托管 web-admin/dist）
FROM python:3.11-slim AS backend
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 换用阿里云 Debian 源 + pip 源（国内服务器加速）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-server.txt ./requirements.txt
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY backend/ ./backend/
COPY --from=admin-builder /app/web-admin/dist ./web-admin/dist
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/backend
EXPOSE 8000
# 运行时入口：迁移 -> 种子（连 PostgreSQL）-> 启动 gunicorn
ENTRYPOINT ["/entrypoint.sh"]
