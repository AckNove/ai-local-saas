# -*- coding: utf-8 -*-
"""上传新迁移文件，重建 WeChat app 容器"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 1. 上传迁移文件
sftp = cli.open_sftp()
local = r'D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\backend\alembic\versions\0002_merchant_code.py'
remote = '/root/apps/WeChat-POI-Groupbuy-SaaS/backend/alembic/versions/0002_merchant_code.py'
sftp.put(local, remote)
sftp.close()
print('迁移文件已上传')

# 2. 重新构建 + 启动 wechat（用 nohup 后台）
cmd = 'cd /root/apps/WeChat-POI-Groupbuy-SaaS && nohup docker compose -p wechat -f docker/docker-compose.yml up --build -d > /root/rebuild_wechat.log 2>&1 &'
cli.exec_command(cmd, timeout=15)
time.sleep(2)
print('WeChat 重建已启动')
cli.close()
