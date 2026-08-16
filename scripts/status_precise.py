# -*- coding: utf-8 -*-
"""精确查看构建状态，不执行任何 kill"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

_, o, _ = cli.exec_command('ps -eo pid,etime,cmd | grep -E "compose|npm|pip3|docker build" | grep -v grep', timeout=30)
print('=== 相关进程(pid 时间 命令) ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('cat /root/build_ai.log 2>/dev/null | tail -30', timeout=30)
print('=== build_ai.log 尾部 ===')
print(o.read().decode('utf-8', 'replace'))

_, o, _ = cli.exec_command('docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}"', timeout=30)
print('=== 镜像 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
