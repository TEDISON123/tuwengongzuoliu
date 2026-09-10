#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据增强装配引擎 (Data Enhancer Assembly)
调用精算函数并将量化算账模型深度装配进图文卡片
"""

import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from finance_math import (
    calc_mortgage_prepayment,
    calc_gold_premium_and_loss,
    calc_emergency_cash_runway,
    calc_dividend_vs_drawdown
)

def enhance_deck_data(deck_data: dict) -> dict:
    """
    根据议题类别调用精算模型，将量化指标注入到卡片中
    """
    meta = deck_data.get("meta", {})
    topic_id = meta.get("topic_id", "")
    pages = deck_data.get("pages", [])

    if topic_id == "mortgage_vs_invest" or (not topic_id and "房贷" in meta.get("topic", "")):
        m_res = calc_mortgage_prepayment(500000.0, 0.040, 30)
        runway_res = calc_emergency_cash_runway(500000.0, 10000.0, 8000.0)

        for p in pages:
            ptype = p.get("type", "")
            if ptype == "pain_point":
                p["table_data"] = [
                    {"item": "银行3年期大额存单 (1.8%)", "rate": "50万本金年收益", "yield": "约 9,000 元/年"},
                    {"item": "等额本息房贷利息 (4.0%)", "rate": "50万贷款年利息", "yield": "约 20,000 元/年"},
                    {"item": "资金存贷剪刀差 (利差2.2%)", "rate": "资金放错位置年损耗", "yield": "-11,000 元/年"}
                ]
            elif ptype == "contrast_gap":
                p["quant_summary"] = {
                    "headline": "30年量化精算总账本",
                    "left_stat": f"省下利息: ¥{round(m_res['total_interest_saved']/10000, 1)}万",
                    "right_stat": f"流动性缓冲: {runway_res['runway_months_with_mortgage']}个月",
                    "spread_metric": f"锁定无风险年化: {m_res['locked_risk_free_yield_pct']}%"
                }

    elif "gold" in topic_id or "金豆" in meta.get("topic", ""):
        g_res = calc_gold_premium_and_loss(740.0, 630.0, 10.0, 2.0)

        for p in pages:
            ptype = p.get("type", "")
            if ptype == "pain_point":
                p["table_data"] = [
                    {"item": "零售专柜小金豆 (含工艺溢价)", "rate": "买入单价 740 元/克", "yield": "总支出 7,400 元"},
                    {"item": "实时上海金交所基准大盘价", "rate": "黄金真实纯金价值", "yield": "价值 6,300 元"},
                    {"item": "民间回购变现价 (扣2%损耗)", "rate": "到手实收 617 元/克", "yield": "实收 6,174 元 (-16.6%)"}
                ]
            elif ptype == "contrast_gap":
                p["quant_summary"] = {
                    "headline": "买入即刻摩擦成本精算",
                    "left_stat": f"工艺溢价: +{g_res['craft_premium_pct']}%",
                    "right_stat": f"变现即刻折损: -{g_res['immediate_loss_pct']}%",
                    "spread_metric": f"保本金价门槛: ¥{int(g_res['breakeven_spot_price'])}/克"
                }

    deck_data["meta"]["has_data_enhanced"] = True
    return deck_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="数据增强测试")
    parser.add_argument("--topic-id", default="mortgage_vs_invest")
    args = parser.parse_args()

    dummy_deck = {
        "meta": {"topic_id": args.topic_id, "topic": "房贷"},
        "pages": [{"type": "pain_point"}, {"type": "contrast_gap"}]
    }
    enhanced = enhance_deck_data(dummy_deck)
    print("📈 [增强后卡片量化数据集]")
    print(json.dumps(enhanced, ensure_ascii=False, indent=2))
