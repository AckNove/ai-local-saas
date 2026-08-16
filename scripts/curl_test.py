# -*- coding: utf-8 -*-
"""从服务器内部 curl 测试 8000 端口"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('curl -s -m 10 http://127.0.0.1:8000/api/health', timeout=20)
print('=== 内部 curl 127.0.0.1:8000 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('curl -s -m 10 http://localhost:8000/api/health', timeout=20)
print('=== 内部 curl localhost:8000 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('docker exec docker-app-1 curl -s -m 5 http://127.0.0.1:8000/api/health 2>&1 || echo "容器内无curl"', timeout=20)
print('=== 容器内测试 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
