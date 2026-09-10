#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事实案例注入引擎 (Fact Case Injector)
为金融图文卡片注入真实中产财务切片、避坑警示与商业历史样本
"""

import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SKILL_ROOT, "database", "case_library.json")

def load_case_library() -> dict:
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("cases", {})
    return {}

def get_cases_by_topic(topic_id: str) -> dict:
    cases = load_case_library()
    if topic_id in cases:
        return cases[topic_id]
    
    # 模糊匹配
    for tid, c in cases.items():
        if tid in topic_id or topic_id in tid:
            return c
    return cases.get("mortgage_vs_invest", {})

def inject_cases_into_deck(deck_data: dict) -> dict:
    """
    将事实案例深度注入到 6 页标准卡片结构中
    - P3 认知剪刀差：注入历史或宏观对比案例
    - P4 正方立论：注入正方现实受益/避坑切片
    - P5 反方立论：注入反方现金流断裂/真实警示切片
    """
    meta = deck_data.get("meta", {})
    topic_id = meta.get("topic_id", "")
    cases = get_cases_by_topic(topic_id)
    if not cases:
        return deck_data

    pages = deck_data.get("pages", [])
    for p in pages:
        ptype = p.get("type", "")
        if ptype == "contrast_gap" and "contrast" in cases:
            c = cases["contrast"]
            p["case_slice"] = {
                "tag": c.get("tag", "案例透视"),
                "title": c.get("title", ""),
                "story": c.get("story", ""),
                "key_metric": c.get("key_metric", "")
            }
        elif ptype == "side_a" and "side_a" in cases:
            c = cases["side_a"]
            p["case_slice"] = {
                "tag": c.get("tag", "现实切片"),
                "title": c.get("title", ""),
                "story": c.get("story", ""),
                "key_metric": c.get("key_metric", "")
            }
        elif ptype == "side_b" and "side_b" in cases:
            c = cases["side_b"]
            p["case_slice"] = {
                "tag": c.get("tag", "警示切片"),
                "title": c.get("title", ""),
                "story": c.get("story", ""),
                "key_metric": c.get("key_metric", "")
            }
            
    deck_data["meta"]["has_cases_injected"] = True
    return deck_data

def main():
    parser = argparse.ArgumentParser(description="事实案例注入与检索引擎")
    parser.add_argument("--topic-id", type=str, default="mortgage_vs_invest", help="议题ID")
    parser.add_argument("--viewpoint", type=str, choices=["side_a", "side_b", "contrast", "all"], default="all", help="指定视角切片")
    parser.add_argument("--list-all", action="store_true", help="列出数据库中所有案例")
    args = parser.parse_args()

    cases = load_case_library()

    if args.list_all:
        print("=" * 60)
        print("📜 [已入库的金融议题事实案例库]")
        print("=" * 60)
        for tid, tcase in cases.items():
            print(f"\n📌 议题ID: {tid} ({tcase.get('topic', '')})")
            for side in ["side_a", "side_b", "contrast"]:
                c = tcase.get(side, {})
                print(f"   [{side.upper()}] [{c.get('tag')}] {c.get('title')}")
                print(f"          指标: {c.get('key_metric')}")
                print(f"          摘要: {c.get('story')[:60]}...")
        return

    topic_cases = get_cases_by_topic(args.topic_id)
    print(f"🔍 议题 [{args.topic_id}] 事实案例切片提取结果：\n")
    if args.viewpoint == "all":
        print(json.dumps(topic_cases, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(topic_cases.get(args.viewpoint, {}), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
