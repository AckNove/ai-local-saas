# -*- coding: utf-8 -*-
"""进容器跑 seed，建 admin 账号"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('docker exec wechat-app-1 python -m scripts.seed 2>&1 | tail -20', timeout=60)
print(o.read().decode('utf-8', 'replace'))

cli.close()
