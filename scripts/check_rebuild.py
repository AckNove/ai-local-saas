# -*- coding: utf-8 -*-
"""检查重建状态和日志"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('docker ps -a --format "{{.Names}}|{{.Status}}"', timeout=30)
print('=== 容器 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('tail -20 /root/rebuild_ai.log 2>/dev/null', timeout=30)
print('=== AI 重建日志 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
