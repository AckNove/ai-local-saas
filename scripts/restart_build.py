# -*- coding: utf-8 -*-
"""清理残留进程，用 nohup 后台重新构建 AI-Local，日志落盘"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 1. 杀掉残留的 docker compose / build 进程
cmds = [
    'pkill -f "docker compose" || true',
    'pkill -f "docker build" || true',
    'sleep 2',
    'docker ps -a -q | xargs -r docker rm -f 2>/dev/null || true',
]
for c in cmds:
    _, o, e = cli.exec_command(c, timeout=30)
    o.read(); e.read()

# 2. 用 nohup 后台构建，日志写到 /root/build_ai.log
cmd = 'cd /root/apps/AI-Local-Growth-SaaS && nohup docker compose -f docker/docker-compose.yml up --build -d > /root/build_ai.log 2>&1 &'
_, o, e = cli.exec_command(cmd, timeout=30)
o.read(); e.read()
print('已启动后台构建，日志 /root/build_ai.log')
cli.close()
