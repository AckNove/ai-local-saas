# -*- coding: utf-8 -*-
"""查看 docker compose 构建的实时日志（判断是正常下载还是卡住）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 查看正在运行的构建进程详情
_, o, _ = cli.exec_command('ps aux | grep -E "npm|pip|docker build|node" | grep -v grep', timeout=30)
print('=== 构建相关进程 ===')
print(o.read().decode('utf-8', 'replace'))

# 查看 docker 是否在拉取镜像
_, o, _ = cli.exec_command('docker events --since 5m --until 0s 2>/dev/null | tail -20', timeout=30)
print('=== docker 事件 ===')
print(o.read().decode('utf-8', 'replace'))

# 检查网络：能否访问 docker 镜像源
_, o, _ = cli.exec_command('curl -sI --max-time 10 https://docker.1ms.run/v2/ | head -3', timeout=20)
print('=== 镜像源连通性 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
