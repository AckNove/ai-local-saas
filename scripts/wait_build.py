# -*- coding: utf-8 -*-
"""轮询等待 AI-Local 构建完成，最长等 15 分钟"""
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
    _, o, _ = cli.exec_command('ps aux | grep "docker compose" | grep -v grep | wc -l', timeout=30)
    cnt = o.read().decode('utf-8', 'replace').strip()
    _, o, _ = cli.exec_command('docker images --format "{{.Repository}}"', timeout=30)
    imgs = o.read().decode('utf-8', 'replace').strip()
    cli.close()
    return cont, cnt, imgs

for i in range(30):
    cont, cnt, imgs = check()
    print(f"[{i*30}s] build_procs={cnt} | containers={cont or '(none)'} | images={imgs or '(none)'}", flush=True)
    if cnt == '0' and cont.strip():
        print('=== AI-Local 构建完成 ===', flush=True)
        break
    time.sleep(30)
