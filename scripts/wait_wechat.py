# -*- coding: utf-8 -*-
"""轮询等 WeChat 容器启动"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

def check():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
    _, o, _ = cli.exec_command('docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}"', timeout=30)
    cont = o.read().decode('utf-8', 'replace').strip()
    cli.close()
    return cont

for i in range(20):
    cont = check()
    print(f"[{i*15}s]", flush=True)
    print(cont, flush=True)
    if '8001' in cont and 'Up' in cont:
        print('=== WeChat 容器已运行 ===', flush=True)
        break
    time.sleep(15)
