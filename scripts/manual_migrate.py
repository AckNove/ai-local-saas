# -*- coding: utf-8 -*-
"""进 WeChat 容器手动跑迁移 + seed"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 1. 确认新迁移文件在容器里（容器是从镜像 COPY 的，需要重建才有）
_, o, _ = cli.exec_command('docker exec wechat-app-1 ls /app/backend/alembic/versions/', timeout=30)
print('=== 容器内迁移文件 ===')
print(o.read().decode('utf-8', 'replace'))

# 2. 手动跑迁移
_, o, _ = cli.exec_command('docker exec wechat-app-1 alembic upgrade head 2>&1 | tail -20', timeout=60)
print('=== alembic upgrade ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
