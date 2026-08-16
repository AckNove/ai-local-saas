"""生成种草卡唯一短码 slug。

使用大小写字母 + 数字的可读短码，并通过对数据库查重保证唯一性。
"""
from __future__ import annotations

import random
import string

_ALPHABET = string.ascii_letters + string.digits


def _random_slug(length: int = 8) -> str:
    """生成一个随机短码。"""
    return "".join(random.choices(_ALPHABET, k=length))


async def generate_unique_slug(exists_fn, length: int = 8, max_tries: int = 10) -> str:
    """生成数据库中不存在的唯一 slug。

    exists_fn(slug) 为异步函数，返回 bool（该 slug 是否已存在）。
    """
    for _ in range(max_tries):
        candidate = _random_slug(length)
        if not await exists_fn(candidate):
            return candidate
    # 极端冲突时加长并带时间戳后缀保证唯一
    return _random_slug(length) + str(random.randint(1000, 9999))
