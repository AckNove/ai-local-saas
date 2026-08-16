# -*- coding: utf-8 -*-
"""检查服务器 docker 构建状态"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
stdin, stdout, stderr = cli.exec_command('docker ps -a', timeout=30)
print('=== CONTAINERS ===')
print(stdout.read().decode('utf-8', 'replace'))
stdin, stdout, stderr = cli.exec_command('docker images', timeout=30)
print('=== IMAGES ===')
print(stdout.read().decode('utf-8', 'replace'))
stdin, stdout, stderr = cli.exec_command('ps aux | grep "docker compose" | grep -v grep', timeout=30)
print('=== BUILD PROCS ===')
print(stdout.read().decode('utf-8', 'replace'))
cli.close()
