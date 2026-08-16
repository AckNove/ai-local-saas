# -*- coding: utf-8 -*-
"""等待 WeChat 重建完成 + 验证迁移和 seed"""
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
    _, o, _ = cli.exec_command('docker logs wechat-app-1 2>&1 | tail -15', timeout=30)
    log = o.read().decode('utf-8', 'replace')
    cli.close()
    return log

for i in range(20):
    log = check()
    if 'seed 跳过' in log or '种子数据' in log or '已创建' in log or 'admin' in log:
        print(f'=== [{i*15}s] seed 完成 ===')
        print(log)
        break
    if i % 4 == 0:
        print(f'[{i*15}s] 等待中... {log.strip()[-80:]}', flush=True)
    time.sleep(15)
