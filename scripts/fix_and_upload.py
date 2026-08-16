# -*- coding: utf-8 -*-
"""重新上传修改后的 Dockerfile，并杀掉卡住的构建，重新构建"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 1. 杀掉卡住的构建进程（按 pid 精确杀，避免误杀自己）
_, o, _ = cli.exec_command("ps -eo pid,cmd | grep -E 'docker-buildx|docker compose|docker-compose' | grep -v grep | awk '{print $1}'", timeout=30)
pids = o.read().decode('utf-8', 'replace').strip().split()
print('要杀的进程:', pids)
for pid in pids:
    if pid.strip():
        cli.exec_command(f'kill -9 {pid}', timeout=15)
time.sleep(2)
print('已清理残留进程')

# 2. 上传修改后的 Dockerfile
sftp = cli.open_sftp()
with sftp.open('/root/apps/AI-Local-Growth-SaaS/docker/Dockerfile', 'w') as f:
    f.write(open(r'D:\桌面\AI-local\AI-Local-Growth-SaaS\docker\Dockerfile', 'r', encoding='utf-8').read())
with sftp.open('/root/apps/WeChat-POI-Groupbuy-SaaS/docker/Dockerfile', 'w') as f:
    f.write(open(r'D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\docker\Dockerfile', 'r', encoding='utf-8').read())
sftp.close()
print('Dockerfile 已更新')

cli.close()
