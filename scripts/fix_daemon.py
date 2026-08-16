# -*- coding: utf-8 -*-
"""修复 docker daemon.json（之前 JSON 无效）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

correct_json = '{\n  "registry-mirrors": [\n    "https://docker.1ms.run",\n    "https://docker.xuanyuan.me"\n  ]\n}\n'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
sftp = cli.open_sftp()
with sftp.open('/etc/docker/daemon.json', 'w') as f:
    f.write(correct_json)
sftp.close()

# 重启 docker
stdin, stdout, stderr = cli.exec_command('systemctl restart docker && sleep 4 && docker ps && echo "=== DOCKER OK ==="', timeout=60)
print(stdout.read().decode('utf-8', 'replace'))
print(stderr.read().decode('utf-8', 'replace'))
cli.close()
