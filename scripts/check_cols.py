# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
con = sqlite3.connect(r'D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\backend\dev.db')
for table in ['video_channel_binding', 'reservation', 'group_buy_package', 'store', 'merchant', 'staff']:
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()]
    print(f"{table}: {cols}")
