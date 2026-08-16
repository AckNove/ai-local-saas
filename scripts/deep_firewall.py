# -*- coding: utf-8 -*-
"""深入检查 ufw 和 iptables INPUT 链真实状态"""
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

run('ufw status verbose', 'ufw status verbose')
run('iptables INPUT链完整规则', 'iptables -L INPUT -n -v --line-numbers')
run('公网IP访问8000详细', 'curl -v -m 8 http://8.134.36.218:8000/api/health 2>&1 | tail -20')

cli.close()
