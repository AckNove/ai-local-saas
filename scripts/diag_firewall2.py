# -*- coding: utf-8 -*-
"""进一步诊断：检查服务器类型 + 端口外部可达性"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 检查 iptables 规则（阿里云轻量服务器可能用 iptables 做防火墙）
_, o, _ = cli.exec_command('iptables -L -n 2>/dev/null | head -30', timeout=30)
print('=== iptables 规则 ===')
print(o.read().decode('utf-8', 'replace'))

# 检查 firewalld
_, o, _ = cli.exec_command('systemctl is-active firewalld 2>/dev/null; echo; firewall-cmd --list-all 2>/dev/null', timeout=30)
print('=== firewalld ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
