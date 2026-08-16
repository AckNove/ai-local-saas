# -*- coding: utf-8 -*-
"""用不同项目名重新部署两个服务，解决容器名冲突"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 1. 停掉并删除所有当前容器
print('清理旧容器...')
_, o, _ = cli.exec_command('docker compose -f /root/apps/WeChat-POI-Groupbuy-SaaS/docker/docker-compose.yml down 2>/dev/null; docker compose -f /root/apps/AI-Local-Growth-SaaS/docker/docker-compose.yml down 2>/dev/null; docker rm -f $(docker ps -aq) 2>/dev/null; echo done', timeout=60)
o.read()

# 2. 用 -p 项目名分别启动（AI-Local 用项目名 ai-local，WeChat 用 wechat）
print('启动 AI-Local（项目名 ai-local）...')
cli.exec_command('cd /root/apps/AI-Local-Growth-SaaS && nohup docker compose -p ai-local -f docker/docker-compose.yml up -d > /root/build_ai.log 2>&1 &', timeout=15)
time.sleep(1)

print('启动 WeChat（项目名 wechat）...')
cli.exec_command('cd /root/apps/WeChat-POI-Groupbuy-SaaS && nohup docker compose -p wechat -f docker/docker-compose.yml up -d > /root/build_wechat.log 2>&1 &', timeout=15)
time.sleep(1)

cli.close()
print('两个服务已用不同项目名启动，正在拉起...')
