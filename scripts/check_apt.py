# -*- coding: utf-8 -*-
"""确认构建卡点 + 检查 apt 源连通性"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('tail -5 /root/build_ai.log', timeout=30)
print('=== 构建日志尾部 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('curl -sI --max-time 8 http://deb.debian.org/debian/ | head -1', timeout=20)
print('=== deb.debian.org 连通性 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('curl -sI --max-time 8 http://mirrors.aliyun.com/debian/ | head -1', timeout=20)
print('=== mirrors.aliyun.com 连通性 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
