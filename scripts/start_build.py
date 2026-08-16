# -*- coding: utf-8 -*-
"""启动 AI-Local 构建（nohup 后台）"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

cmd = 'cd /root/apps/AI-Local-Growth-SaaS && nohup docker compose -f docker/docker-compose.yml up --build -d > /root/build_ai.log 2>&1 &'
_, o, e = cli.exec_command(cmd, timeout=30)
o.read(); e.read()
time.sleep(3)
print('构建已启动')
cli.close()
