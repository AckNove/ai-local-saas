# -*- coding: utf-8 -*-
"""给 merchant 表补 merchant_code 列（dev.db 旧结构迁移）"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

con = sqlite3.connect(r'D:\桌面\AI-local\WeChat-POI-Groupbuy-SaaS\backend\dev.db')
cols = [r[1] for r in con.execute('PRAGMA table_info(merchant)').fetchall()]
print('merchant cols before:', cols)
if 'merchant_code' not in cols:
    con.execute('ALTER TABLE merchant ADD COLUMN merchant_code VARCHAR(32)')
    con.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_merchant_merchant_code ON merchant(merchant_code)')
    con.commit()
    print('ADDED merchant_code')
else:
    print('merchant_code already exists')
cols = [r[1] for r in con.execute('PRAGMA table_info(merchant)').fetchall()]
print('merchant cols after:', cols)
