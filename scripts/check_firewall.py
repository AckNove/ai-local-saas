# -*- coding: utf-8 -*-
"""检查阿里云安全组是否放行 8000（通过防火墙和端口监听判断）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 检查监听情况
_, o, _ = cli.exec_command('ss -tlnp | grep -E ":8000|:8001"', timeout=30)
print('=== 端口监听 ===')
print(o.read().decode('utf-8', 'replace'))

# 检查系统防火墙（ufw/iptables）
_, o, _ = cli.exec_command('ufw status 2>/dev/null || echo "no ufw"', timeout=30)
print('=== ufw 状态 ===')
print(o.read().decode('utf-8', 'replace'))

cli.close()
