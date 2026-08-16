# -*- coding: utf-8 -*-
"""启动 WeChat 构建"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

cmd = 'cd /root/apps/WeChat-POI-Groupbuy-SaaS && nohup docker compose -f docker/docker-compose.yml up --build -d > /root/build_wechat.log 2>&1 &'
cli.exec_command(cmd, timeout=15)
time.sleep(2)
print('WeChat 构建已启动')
cli.close()
