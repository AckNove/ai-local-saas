# -*- coding: utf-8 -*-
"""确认内网IP访问正常，隔离问题范围"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

def run(tag, cmd):
    _, o, e = cli.exec_command(cmd, timeout=30)
    print(f'=== {tag} ===')
    print(o.read().decode('utf-8', 'replace'))
    err = e.read().decode('utf-8', 'replace')
    if err.strip(): print('[stderr]', err)
    print()

# 内网IP访问（这是 NAT 之前应该通的）
run('内网IP 172.18.40.96:8000', 'curl -s -m 5 http://172.18.40.96:8000/api/health; echo')
run('内网IP 172.18.40.96:8001', 'curl -s -m 5 http://172.18.40.96:8001/api/health; echo')

cli.close()
