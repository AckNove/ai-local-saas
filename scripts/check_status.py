# -*- coding: utf-8 -*-
"""检查构建是否完成 + 容器状态"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"', timeout=30)
print('=== 容器状态 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('docker images --format "table {{.Repository}}\t{{.Size}}"', timeout=30)
print('=== 镜像 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('ps aux | grep "docker compose" | grep -v grep | wc -l', timeout=30)
print('=== 仍在构建的进程数 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
