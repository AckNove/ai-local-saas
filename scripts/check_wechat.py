# -*- coding: utf-8 -*-
"""检查 WeChat 构建进度"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}"', timeout=30)
print('=== 容器 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('tail -8 /root/build_wechat.log 2>/dev/null', timeout=30)
print('=== WeChat 构建日志尾部 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
