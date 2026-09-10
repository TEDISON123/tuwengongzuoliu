#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
幽默化改造与网感赋能引擎 (Humor Refiner)
为金融图文卡片注入神级通俗隐喻、打工人自嘲与括号内心戏 OS
"""

import os
import json
import argparse

HUMOR_KNOWLEDGE_BASE = {
    "mortgage_vs_invest": {
        "cover_subtitle_addon": "给银行减负 VS 留救命子弹？（内附不吐不快的明白账）",
        "p2_hook_witty": "表面看提前还贷白捡了一辆特斯拉，为什么金融老炮却劝你'别急着把防弹衣当废品卖了'？",
        "p3_metaphor": "把现金全还进水泥里，就像给大门装了三道指纹锁，结果把自己的钥匙反锁在门里！",
        "side_a_os": "（打工人独白：只要不用每月看催款短信，晚上能睡个踏实觉，比什么通胀理论都管用！）",
        "side_b_os": "（银行经理潜台词：感谢大善人提前结清低息贷款！顺便请了解一下我们年化9%的信用消费贷？）",
        "p6_witty_a": "🔴 选 A【无债神仙派】：宁愿喝粥也要无债一身轻！睡眠质量无价，坚决不给银行多打一天工！",
        "p6_witty_b": "🔵 选 B【现金硬汉派】：水泥不能当下酒菜！手握子弹才有安全感，现金才是中年家庭的呼吸机！",
        "copy_punchline": "💡 房贷就像那个廉价但包容的前任，一旦结清了很痛快，但哪天你急用钱想再追回来，可就千难万难了……"
    },
    "gold_beans": {
        "cover_subtitle_addon": "建微型诺亚方舟 VS 给金店老板众筹年终奖？",
        "p2_hook_witty": "刚买到手账面就跌掉一顿海底捞，为什么打工人依然攒得乐此不疲？",
        "p3_metaphor": "你以为买的是抗通胀资产，其实是包裹着一层金箔的'当代年轻人情绪布洛芬'！",
        "side_a_os": "（年轻人自嘲：少喝几杯奶茶攒颗豆，就算亏了工艺费，起码抽屉里还剩个真金硬茬！）",
        "side_b_os": "（回收小哥潜台词：火熔枪一响，大盘梦变废铁，扣完杂质损耗，欢迎下次再来交学费～）",
        "p6_witty_a": "🔴 选 A【微量克己派】：千金难买我自律！物理级管住乱花钱，看着小玻璃瓶越来越满就很爽！",
        "p6_witty_b": "🔵 选 B【人间清醒派】：拒绝给金店打白工！一买一卖亏掉两成，要攒就攒没工艺费的标准投资金！",
        "copy_punchline": "💡 金店柜姐看着你桌上的小玻璃瓶，嘴角微微上扬，默默给老家盖房添了一块砖……"
    },
    "dividend_assets": {
        "cover_subtitle_addon": "熊市安乐窝 VS 火山口上搭帐篷？",
        "p2_hook_witty": "大家都以为买高股息是躺平吃利息，怎么买着买着就成了'为了4%股息亏掉20%本金'？",
        "p3_metaphor": "当全世界都涌进防守资产避险，曾经的安全边际就被踩成了最拥挤的独木桥！",
        "side_a_os": "（退休股神独白：任你大盘翻江倒海，我只关心每年分红能不能准时打进工资卡！）",
        "side_b_os": "（机构操盘手潜台词：感谢各路散户帮我们在历史估值最高位完成体面换筹，承让了承让了！）",
        "p6_witty_a": "🔴 选 A【收息佛系派】：只要公司不倒闭分红不停歇，净值波动与我何干？",
        "p6_witty_b": "🔵 选 B【防守反击派】：防守资产被炒上天就是最大的危险！宁可空仓绝不给抱团接盘！",
        "copy_punchline": "💡 投资最扎心的悲剧，不是在熊市被套，而是在防守资产里被当成韭菜连根拔起……"
    },
    "options_rich_or_ruin": {
        "cover_subtitle_addon": "非对称暴富神器 VS 倾家荡产绞肉机？（看完再碰期权！）",
        "p2_hook_witty": "上午赚300%感觉巴菲特不如我，下午归零发现连饭钱都没了，普通人玩期权到底是在搞投资还是在送人头？",
        "p3_metaphor": "玩买方期权就像每天高价买保质期只有7天的隔夜酸奶；玩卖方期权就像为了在铁轨上捡一分钱硬币，把整个身家枕在铁轨上等火车开过来！",
        "side_a_os": "（买方赌神独白：亏也只亏权利金盒饭钱，万一撞上百倍末日轮，直接少奋斗二十年！）",
        "side_b_os": "（做市商潜台词：感谢各位散户老铁每天按时送来的权利金！您的时间价值Theta已准时汇入机构账户～）",
        "p6_witty_a": "🔴 选 A【天命买方派】：以小博大有奇迹！有限风险博无限利润，不碰非对称杠杆怎么逆天改命！",
        "p6_witty_b": "🔵 选 B【清醒保命派】：衍生品绞肉机！珍爱生命远离期权，绝不做做市商的人形自走提款机！",
        "copy_punchline": "💡 巴菲特早就警告过：期权是大规模杀伤性金融武器。普通人千万别以为自己是持枪的猎人，多数时候只是靶场上的活靶子……"
    }
}

def polish_humor_for_deck(deck_data: dict) -> dict:
    """
    对图文卡片各页面注入幽默神级比喻、打工人自嘲与反讽旁白
    """
    meta = deck_data.get("meta", {})
    topic_id = meta.get("topic_id", "")
    hdata = HUMOR_KNOWLEDGE_BASE.get(topic_id, HUMOR_KNOWLEDGE_BASE["mortgage_vs_invest"])

    pages = deck_data.get("pages", [])
    for p in pages:
        ptype = p.get("type", "")
        if ptype == "cover_poster":
            p["humor_tag"] = "💡 犀利嘴替 · 扎心账本"
            if "subtitle" in p:
                p["subtitle"] = f"{p['subtitle']} {hdata.get('cover_subtitle_addon', '')}"

        elif ptype == "pain_point":
            p["hook_question"] = hdata.get("p2_hook_witty", p.get("hook_question", ""))

        elif ptype == "contrast_gap":
            p["humor_metaphor"] = hdata.get("p3_metaphor", "")

        elif ptype == "side_a":
            p["humor_os"] = hdata.get("side_a_os", "")

        elif ptype == "side_b":
            p["humor_os"] = hdata.get("side_b_os", "")

        elif ptype == "ending_hook":
            p["option_a"] = hdata.get("p6_witty_a", p.get("option_a", ""))
            p["option_b"] = hdata.get("p6_witty_b", p.get("option_b", ""))

    # 注入文案
    if "post_copy" in deck_data:
        deck_data["post_copy"]["body"] += f"\n\n{hdata.get('copy_punchline', '')}"

    deck_data["meta"]["has_humor_polished"] = True
    return deck_data

def main():
    parser = argparse.ArgumentParser(description="幽默化改造与金句引擎")
    parser.add_argument("--topic-id", default="mortgage_vs_invest", help="议题ID")
    parser.add_argument("--list-quotes", action="store_true", help="打印所有已入库的幽默比喻与神级金句")
    args = parser.parse_args()

    if args.list_quotes:
        print("=" * 60)
        print("🎭 [金融图文幽默比喻与打工人扎心金句库]")
        print("=" * 60)
        for tid, data in HUMOR_KNOWLEDGE_BASE.items():
            print(f"\n📌 议题ID: {tid}")
            print(f"   💡 神级比喻: {data['p3_metaphor']}")
            print(f"   💬 正方内心戏: {data['side_a_os']}")
            print(f"   💬 反方内心戏: {data['side_b_os']}")
            print(f"   🎯 文案落幕金句: {data['copy_punchline']}")
        return

    res = HUMOR_KNOWLEDGE_BASE.get(args.topic_id, {})
    print(f"🎭 [{args.topic_id}] 幽默改造配置：")
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

