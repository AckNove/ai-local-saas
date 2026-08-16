# -*- coding: utf-8 -*-
"""SSH 远程执行工具（支持自定义超时）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

def run(cmd, timeout=600):
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
    stdin, stdout, stderr = cli.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', 'replace')
    err = stderr.read().decode('utf-8', 'replace')
    code = stdout.channel.recv_exit_status()
    cli.close()
    return code, out, err

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'echo hello'
    tmo = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    code, out, err = run(cmd, timeout=tmo)
    print(f'[exit={code}]')
    if out:
        print(out)
    if err:
        print('[stderr]', err)
