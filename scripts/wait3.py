# -*- coding: utf-8 -*-
"""轮询等 AI-Local 容器启动（通过 docker ps）"""
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
    _, o, _ = cli.exec_command('tail -2 /root/build_ai.log', timeout=30)
    log = o.read().decode('utf-8', 'replace').strip().replace('\n',' ')
    cli.close()
    return cont, log

for i in range(20):
    cont, log = check()
    print(f"[{i*15}s] {cont or '(no containers)'} | {log[:80]}", flush=True)
    if 'app' in cont and 'Up' in cont:
        print('=== AI-Local 容器已运行 ===', flush=True)
        break
    time.sleep(15)
