# -*- coding: utf-8 -*-
"""查看 AI-Local app 容器日志，确认启动状态"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
_, o, _ = cli.exec_command('docker logs docker-app-1 2>&1 | tail -30', timeout=30)
print(o.read().decode('utf-8', 'replace'))
cli.close()
