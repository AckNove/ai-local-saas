# -*- coding: utf-8 -*-
"""诊断 502：检查容器状态、公网访问路径"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 容器是否还在运行
_, o, _ = cli.exec_command('docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}"', timeout=30)
print('=== 容器状态 ===')
print(o.read().decode('utf-8', 'replace'))

# 用服务器自己的公网 IP 访问（模拟外部访问路径）
_, o, _ = cli.exec_command('curl -s -m 8 http://8.134.36.218:8000/api/health; echo; curl -s -m 8 http://8.134.36.218:8001/api/health', timeout=20)
print('=== 用公网IP访问 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
