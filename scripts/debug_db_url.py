# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
print("cwd:", os.getcwd())
os.environ.setdefault("PYTHONPATH", r"D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\backend")
from app.core.config import settings
print("DATABASE_URL:", settings.DATABASE_URL)
from app.core.db import engine
print("engine url:", engine.url)
import asyncio

async def main():
    async with engine.connect() as conn:
        rows = await conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'")
        print("tables:", [r[0] for r in rows])

asyncio.run(main())
