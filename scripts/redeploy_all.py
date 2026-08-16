# -*- coding: utf-8 -*-
"""解压覆盖 + 重新构建两个服务"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import paramiko

HOST = '8.134.36.218'
USER = 'root'
PWD = '@Hl20010420'

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, port=22, username=USER, password=PWD, timeout=15)

# 解压覆盖
cmds = [
    'rm -rf /root/apps/AI-Local-Growth-SaaS/* /root/apps/AI-Local-Growth-SaaS/.[!.]* 2>/dev/null; tar -xzf /root/ai-local.tar.gz -C /root/apps/AI-Local-Growth-SaaS',
    'rm -rf /root/apps/WeChat-POI-Groupbuy-SaaS/* /root/apps/WeChat-POI-Groupbuy-SaaS/.[!.]* 2>/dev/null; tar -xzf /root/wechat.tar.gz -C /root/apps/WeChat-POI-Groupbuy-SaaS',
]
for c in cmds:
    _, o, e = cli.exec_command(c, timeout=60)
    o.read(); e.read()

# 重新生成 .env（因为 rm 删掉了 .env）
import secrets
jwt1 = secrets.token_hex(32); jwt2 = secrets.token_hex(32)
pg1 = secrets.token_hex(16); pg2 = secrets.token_hex(16)
ai_env = f"POSTGRES_USER=saas\nPOSTGRES_PASSWORD={pg1}\nPOSTGRES_DB=growth\nJWT_SECRET={jwt1}\nJWT_EXPIRE_MINUTES=1440\nPUBLIC_BASE_URL=http://8.134.36.218:8000\nLLM_PROVIDER=deepseek\nDEEPSEEK_API_KEY=\nCORS_ORIGINS=http://8.134.36.218:8000\n"
wechat_env = f"POSTGRES_USER=wechat\nPOSTGRES_PASSWORD={pg2}\nPOSTGRES_DB=groupbuy\nJWT_SECRET={jwt2}\nJWT_EXPIRE_MINUTES=1440\n"
sftp = cli.open_sftp()
with sftp.open('/root/apps/AI-Local-Growth-SaaS/.env', 'w') as f:
    f.write(ai_env)
with sftp.open('/root/apps/WeChat-POI-Groupbuy-SaaS/.env', 'w') as f:
    f.write(wechat_env)
sftp.close()
print('.env 已重新写入')

# 后台重建两个服务
cli.exec_command('cd /root/apps/AI-Local-Growth-SaaS && nohup docker compose -p ai-local -f docker/docker-compose.yml up --build -d > /root/rebuild_ai.log 2>&1 &', timeout=15)
time.sleep(1)
cli.exec_command('cd /root/apps/WeChat-POI-Groupbuy-SaaS && nohup docker compose -p wechat -f docker/docker-compose.yml up --build -d > /root/rebuild_wechat.log 2>&1 &', timeout=15)
time.sleep(1)
print('两个服务重建已启动')
cli.close()
