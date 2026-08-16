# -*- coding: utf-8 -*-
"""排查 502 根源：检查阿里云安全组件、绑定域名、80端口等"""
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
    out = o.read().decode('utf-8', 'replace')
    print(out if out.strip() else '(空)')
    err = e.read().decode('utf-8', 'replace')
    if err.strip(): print('[stderr]', err)
    print()

run('阿里云安全组件进程', 'ps aux | grep -iE "aliyun|aegis|assist|cloudmonitor|yunjing" | grep -v grep || echo 无')
run('hostname', 'hostname; cat /etc/hostname')
run('公网IP归属网卡', 'ip addr show | grep -E "inet " | grep -v 127.0.0.1')
run('检查是否有80/443监听', 'ss -tlnp | grep -E ":80 |:443 |:8080" || echo "无80/443监听"')
run('docker 网络', 'docker network ls')

cli.close()
