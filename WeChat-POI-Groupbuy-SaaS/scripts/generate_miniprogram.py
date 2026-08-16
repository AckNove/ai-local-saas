#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小程序一键生成脚本

用途：输入商家标识（merchant_code）+ 商家小程序 AppID，自动从模板生成一个
"商家专属小程序文件夹"，可直接用微信开发者工具打开上传。

用法：
    python generate_miniprogram.py --code 商家标识 --appid wx商家AppID [--name 商家名] [--out 输出目录]

示例：
    python generate_miniprogram.py --code shop_zhangsan --appid wx1234567890abcdef --name 张三餐饮

生成结果：
    output/shop_zhangsan/   ← 这个文件夹用微信开发者工具导入即可
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# 模板目录（本脚本位于 WeChat-POI-Groupbuy-SaaS/scripts/，模板在其上一级 miniprogram/）
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "miniprogram"


def generate(merchant_code: str, appid: str, name: str | None, out_dir: str) -> Path:
    if not TEMPLATE_DIR.exists():
        print(f"[错误] 找不到小程序模板目录：{TEMPLATE_DIR}", file=sys.stderr)
        sys.exit(1)

    target = Path(out_dir) / merchant_code
    if target.exists():
        print(f"[提示] 目标目录已存在，清空后重新生成：{target}")
        shutil.rmtree(target)

    # 复制整个模板
    shutil.copytree(TEMPLATE_DIR, target)
    print(f"[1/3] 已复制模板 -> {target}")

    # 修改 config.js
    config_path = target / "config.js"
    config_text = config_path.read_text(encoding="utf-8")
    # 简单文本替换（模板里这些是占位值）
    config_text = config_text.replace("MERCHANT_CODE: ''", f"MERCHANT_CODE: '{merchant_code}'")
    config_text = config_text.replace("APP_ID: ''", f"APP_ID: '{appid}'")
    # API_BASE：保持模板里的值（部署时统一改），这里不强制改
    config_path.write_text(config_text, encoding="utf-8")
    print(f"[2/3] 已写入 config.js（MERCHANT_CODE={merchant_code}, APP_ID={appid}）")

    # 修改 project.config.json
    proj_path = target / "project.config.json"
    proj = json.loads(proj_path.read_text(encoding="utf-8"))
    proj["appid"] = appid
    proj["projectname"] = f"poi-groupbuy-{merchant_code}"
    if name:
        proj["description"] = f"{name} - 视频号 POI 团购小程序"
    proj_path.write_text(json.dumps(proj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[3/3] 已写入 project.config.json（appid={appid}）")

    print()
    print("=" * 50)
    print("[完成] 生成成功！")
    print(f"   小程序文件夹：{target}")
    print(f"   商家标识：{merchant_code}")
    print(f"   AppID：{appid}")
    print()
    print("下一步：")
    print("   1. 打开「微信开发者工具」")
    print("   2. 点「导入项目」，选择上面这个文件夹")
    print("   3. 填 AppID（如果没自动填上）")
    print("   4. 点「上传」→ 提交审核")
    print("=" * 50)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小程序一键生成")
    parser.add_argument("--code", required=True, help="商家标识 merchant_code（后台商户管理里填的那个）")
    parser.add_argument("--appid", required=True, help="商家小程序的 AppID（商家注册认证后拿到）")
    parser.add_argument("--name", default=None, help="商家名称（可选，用于项目描述）")
    parser.add_argument("--out", default="output", help="输出目录（默认 output）")
    args = parser.parse_args()

    generate(args.code, args.appid, args.name, args.out)
