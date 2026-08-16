# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
con = sqlite3.connect(r'D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\backend\dev.db')
rows = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("tables:", rows)
print("count:", len(rows))
missing = [t for t in ['video_channel_binding', 'reservation', 'group_buy_package', 'package_store', 'merchant', 'store', 'staff', 'consumer', 'orders', 'refund', 'platform_operator', 'merchant_user'] if t not in rows]
print("missing:", missing)
