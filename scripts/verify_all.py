# -*- coding: utf-8 -*-
"""确认两个服务的容器都正常运行"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"', timeout=30)
print('=== 所有容器 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('curl -s -m 8 http://127.0.0.1:8000/api/health; echo; curl -s -m 8 http://127.0.0.1:8001/api/health', timeout=20)
print('=== 内部健康检查 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
