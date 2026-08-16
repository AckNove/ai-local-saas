# -*- coding: utf-8 -*-
"""轮询等待构建完成（通过日志尾部 + 容器状态判断），最长 15 分钟"""
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
    _, o, _ = cli.exec_command('docker ps -a --format "{{.Names}}|{{.Status}}"', timeout=30)
    cont = o.read().decode('utf-8', 'replace').strip()
    _, o, _ = cli.exec_command('tail -3 /root/build_ai.log 2>/dev/null', timeout=30)
    log = o.read().decode('utf-8', 'replace').strip().replace('\n', ' ')
    cli.close()
    return cont, log

for i in range(30):
    cont, log = check()
    print(f"[{i*30}s] containers={cont or '(none)'} | log: {log[:100]}", flush=True)
    if cont.strip():
        print('=== 容器已启动，构建完成 ===', flush=True)
        break
    time.sleep(30)
