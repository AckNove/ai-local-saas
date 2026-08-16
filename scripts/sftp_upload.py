# -*- coding: utf-8 -*-
"""SFTP 上传项目压缩包到服务器"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

local_files = [
    (r'D:\桌面\AI-local\ai-local.tar.gz', '/root/ai-local.tar.gz'),
    (r'D:\桌面\AI-local\wechat.tar.gz', '/root/wechat.tar.gz'),
]

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
sftp = cli.open_sftp()
for local, remote in local_files:
    print(f'上传 {local} -> {remote} ...')
    sftp.put(local, remote)
    print('  完成')
sftp.close()
cli.close()
print('全部上传完成')
