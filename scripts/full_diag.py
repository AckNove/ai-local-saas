# -*- coding: utf-8 -*-
"""完整重新诊断：从容器、端口、系统防火墙、公网访问全链路检查"""
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
    out = o.read().decode('utf-8', 'replace')
    err = e.read().decode('utf-8', 'replace')
    print(f'=== {tag} ===')
    if out.strip(): print(out)
    if err.strip(): print('[stderr]', err)
    print()

run('1. 容器状态', 'docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
run('2. 端口监听', 'ss -tlnp | grep -E ":8000|:8001|:80|:443"')
run('3. 本机访问8000', 'curl -s -m 5 http://127.0.0.1:8000/api/health; echo')
run('4. 本机访问8001', 'curl -s -m 5 http://127.0.0.1:8001/api/health; echo')
run('5. 公网IP访问8000', 'curl -s -m 8 http://8.134.36.218:8000/api/health; echo "END"')
run('6. 80端口探测', 'curl -s -m 5 http://8.134.36.218:80/ -o /dev/null -w "%{http_code}"; echo')
run('7. nginx/apache是否在跑', 'ps aux | grep -E "nginx|apache|caddy" | grep -v grep || echo "无"')
run('8. 是否有云防火墙组件', 'ls /etc/nginx 2>/dev/null && echo "有nginx配置" || echo "无nginx"; systemctl list-units --type=service | grep -iE "nginx|apache|firewall" ')

cli.close()
