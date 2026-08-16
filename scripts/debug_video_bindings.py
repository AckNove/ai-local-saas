# -*- coding: utf-8 -*-
"""调试 video-bindings 500 根因"""
import asyncio, traceback, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from sqlalchemy import select

async def main():
    from app.core.db import async_session_factory
    from app.api.v1 import fulfillment
    from app.models.fulfillment import VideoChannelBinding
    async with async_session_factory() as db:
        rows = list((await db.scalars(select(VideoChannelBinding))).all())
        print("binding rows:", len(rows))
        if rows:
            try:
                out = fulfillment._binding_out(rows[0])
                print("binding_out OK:", out)
            except Exception:
                traceback.print_exc()
        else:
            print("no bindings yet — 500 可能来自 list_video_api 的 paginate 边界")
        # 直接跑 list_video_api 逻辑
        from app.core.tenant import TenantContext
        ctx = TenantContext(user_id=1, role='platform_operator', merchant_id=None, store_id=None)
        try:
            resp = await fulfillment.list_video_api(db=db, ctx=ctx)
            print("list_video_api resp:", resp.status_code, resp.body)
        except Exception:
            traceback.print_exc()

asyncio.run(main())
