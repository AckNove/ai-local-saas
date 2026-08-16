# -*- coding: utf-8 -*-
"""在服务器上创建生产 .env 文件"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

# 生成随机 JWT 密钥
import secrets
jwt1 = secrets.token_hex(32)
jwt2 = secrets.token_hex(32)
pg1 = secrets.token_hex(16)
pg2 = secrets.token_hex(16)

ai_local_env = f"""# AI-Local 生产环境
POSTGRES_USER=saas
POSTGRES_PASSWORD={pg1}
POSTGRES_DB=growth
JWT_SECRET={jwt1}
JWT_EXPIRE_MINUTES=1440
PUBLIC_BASE_URL=http://8.134.36.218:8000
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=
CORS_ORIGINS=http://8.134.36.218:8000
"""

wechat_env = f"""# WeChat 生产环境
POSTGRES_USER=wechat
POSTGRES_PASSWORD={pg2}
POSTGRES_DB=groupbuy
JWT_SECRET={jwt2}
JWT_EXPIRE_MINUTES=1440
"""

def run(cmd):
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
    stdin, stdout, stderr = cli.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', 'replace')
    err = stderr.read().decode('utf-8', 'replace')
    cli.close()
    return out, err

# 写 AI-Local .env
import base64
def write_remote(remote_path, content):
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)
    sftp = cli.open_sftp()
    with sftp.open(remote_path, 'w') as f:
        f.write(content)
    sftp.close()
    cli.close()
    print(f'已写入 {remote_path}')

write_remote('/root/apps/AI-Local-Growth-SaaS/.env', ai_local_env)
write_remote('/root/apps/WeChat-POI-Groupbuy-SaaS/.env', wechat_env)
print('两个 .env 已写入')
