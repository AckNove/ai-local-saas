# -*- coding: utf-8 -*-
"""测试 SSH 连接服务器"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
    stdin, stdout, stderr = cli.exec_command('uname -a && echo "---" && cat /etc/os-release | head -3 && echo "---" && docker --version 2>&1')
    out = stdout.read().decode('utf-8', 'replace')
    err = stderr.read().decode('utf-8', 'replace')
    print('连接成功！')
    print(out)
    if err:
        print('stderr:', err)
except Exception as e:
    print('连接失败:', repr(e))
finally:
    cli.close()
