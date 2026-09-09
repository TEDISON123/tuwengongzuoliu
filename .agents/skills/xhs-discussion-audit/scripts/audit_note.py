#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书「理性讨论」活动合规审核与改写引擎
对标小红书官方新版创作指导标准 (https://cowork.xiaohongshu.com/f/sr-8ffe0573/)
"""

import sys
import os
import json
import argparse
import re

def audit_note(title: str, content: str = "", category: str = "auto") -> dict:
    title = title.strip()
    content = content.strip()
    full_text = f"{title}\n{content}"

    report = {
        "title": title,
        "category": category,
        "checks": {},
        "penalties": [],
        "strengths": [],
        "score": 100,
        "status": "PASS",
        "rewrite_suggestions": []
    }

    # 1. 标题是否本身就是问题
    is_question = bool(re.search(r"[?？]|吗|为什么|为何|谁|哪个|何为|是否|能否|值不值|算不算|何在|怎样|如何", title))
    report["checks"]["check_1_title_is_question"] = {
        "rule": "标题本身就是一个问题，用户一眼能看懂在讨论什么",
        "passed": is_question,
        "detail": "标题含有疑问/辨析标识" if is_question else "标题不是疑问句或议题句，缺少天然讨论引信"
    }
    if not is_question:
        report["score"] -= 25
        report["penalties"].append("标题非设问句：标题未直接抛出疑问或选择，读者难以一眼理解讨论标的。")

    # 2. 是否存在空泛问法（"你怎么看"、"大家怎么看"）
    vague_invitation = bool(re.search(r"(大家|你)(们)?(觉得|怎么看|如何看|怎么认为|怎么想)[？?]?$", title))
    if vague_invitation:
        report["score"] -= 15
        report["penalties"].append("提问过于空泛：使用了'你怎么看'式空泛提问，缺少具体比较标准或二选一取舍。")

    # 3. 四大投流死穴检测 (Negative Traps)
    is_personal = bool(re.search(r"(我的求职|面试进度|今天去面试|建了个群|加群|我的复盘|日常记录|打卡第\d+天)", full_text))
    is_tutorial = bool(re.search(r"(保姆级|手把手|避坑指南|干货分享|拿走不谢|建议收藏|保姆教程|全网最全)", full_text))
    is_motivational = bool(re.search(r"(狠狠搞钱|人生感悟|终于想通了|致年轻的我们|这几句话送给大家|太真实了|一定要远离)", full_text))
    is_lifestyle = bool(re.search(r"(我的极简|松弛感生活|给生活减负|沉浸式开箱|爱自己才是终身浪漫)", full_text))

    deadly_trap_detected = False
    trap_reasons = []

    if is_personal:
        deadly_trap_detected = True
        trap_reasons.append("命中死穴【个人流水账】：内容偏向个人日记与个人求职记录，读者无法开展对立辩论。")
    if is_tutorial:
        deadly_trap_detected = True
        trap_reasons.append("命中死穴【方法教学/教程】：经验教程类笔记结论由作者单向输出，非观点讨论，活动方不予投流。")
    if is_motivational:
        deadly_trap_detected = True
        trap_reasons.append("命中死穴【励志鸡汤/感悟】：单向灌输观点感悟，结论封闭，缺少不同立场的交锋空间。")
    if is_lifestyle:
        deadly_trap_detected = True
        trap_reasons.append("命中死穴【主观生活态度】：生活方式或消费偏好表达，缺少可核查的公共争议焦点。")

    report["checks"]["check_5_no_pure_sharing"] = {
        "rule": "内容不是纯个人经历、方法教学、励志感悟或生活态度分享",
        "passed": not deadly_trap_detected,
        "detail": "排除四大非投流死穴" if not deadly_trap_detected else "；".join(trap_reasons)
    }

    if deadly_trap_detected:
        report["score"] -= 40
        report["penalties"].extend(trap_reasons)

    # 4. 公式要素检测 (OBJECT + CONDITION + QUESTION + INVITATION)
    has_condition = bool(re.search(r"(若|如果|假[如下设]|同为|同样|还是|比起|二选一|限[制度]|成本|代价|不仅|虽然|为何却|怎么保住|哪个更|为何仍|有无责任)", full_text))
    report["checks"]["check_4_concrete_condition"] = {
        "rule": "有具体对象、时间或条件，不是空泛提问",
        "passed": has_condition,
        "detail": "具备具体的限制条件、反差比较或具体处境" if has_condition else "缺少限制前提或取舍约束，问题容易演变为无定标空谈"
    }
    if not has_condition:
        report["score"] -= 15
        report["penalties"].append("缺少限定条件/反差对比：建议增加'二选一'、'极端代价'或'身份困境'设定。")

    # 5. 问题答案是否非单一（是否查资料即知）
    has_debate_space = bool(re.search(r"(还是|哪个|如何平衡|合理吗|是否被高估|偏袒|压垮|责任|失灵|更能|难干到底|裁员|走上|避免)", title))
    report["checks"]["check_2_multiple_answers"] = {
        "rule": "这个问题至少存在两种站得住脚的答案，而不是只有一个标准答案",
        "passed": has_debate_space,
        "detail": "具备多元立场对辩空间" if has_debate_space else "争议切口较浅，需确保至少存在两种针锋相对的有力论据"
    }
    if not has_debate_space:
        report["score"] -= 10

    # 6. 事实准确性提醒
    report["checks"]["check_3_fact_accuracy"] = {
        "rule": "问题里的事实部分经得起核查，没有为了尖锐而编造虚假前提",
        "passed": True,
        "detail": "观点可以尖锐，事实必须准确。严禁出现'黄埔没有任何军事教育'式的硬伤前提。"
    }

    # 7. 填表合规提醒
    report["checks"]["check_6_form_submitted"] = {
        "rule": "已准备按要求填写群内腾讯统计表格（不填表视为未参与）",
        "passed": True,
        "detail": "强提醒：发布后务必第一时间复制链接提交至腾讯文档收集表。"
    }

    # 综合裁定
    report["score"] = max(0, report["score"])
    if report["score"] >= 80 and not deadly_trap_detected and is_question:
        report["status"] = "PASS (推荐投流 ✅)"
    elif report["score"] >= 50 and not deadly_trap_detected:
        report["status"] = "NEEDS_OPTIMIZATION (需优化后投流 ⚠️)"
    else:
        report["status"] = "REJECTED (非活动投流范式 ❌)"

    # 生成改写建议
    if not is_question or deadly_trap_detected or not has_condition:
        report["rewrite_suggestions"].append(f"【聚焦取舍改写】将陈述句拆分为两方博弈：围绕'{title[:15]}'设定 A方案 vs B方案")
        report["rewrite_suggestions"].append("【情境代入改写】设定：具体身份 ＋ 关键节点 ＋ 核心困境 ＋ 抉择目标")

    return report

def format_markdown_report(report: dict) -> str:
    md = []
    md.append(f"# 📋 小红书「理性讨论」活动合规审核报告")
    md.append(f"**原笔记标题**：`{report['title']}`\n")
    md.append(f"### 一、 综合判定结果")
    md.append(f"- **审核结论**：**{report['status']}**")
    md.append(f"- **议题指数评分**：**{report['score']} / 100 分**")
    md.append(f"- **判定赛道**：{report['category']}\n")

    md.append(f"### 二、 官方自检六卡点状态 (Checklist)")
    for k, v in report["checks"].items():
        icon = "✅ [PASS]" if v["passed"] else "❌ [FAIL]"
        md.append(f"- {icon} **{v['rule']}**\n  *说明*：{v['detail']}")

    if report["penalties"]:
        md.append(f"\n### 三、 核心扣分与违规项诊断")
        for p in report["penalties"]:
            md.append(f"- ⚠️ {p}")

    if report["rewrite_suggestions"]:
        md.append(f"\n### 四、 官方范式优化建议")
        for s in report["rewrite_suggestions"]:
            md.append(f"- 💡 {s}")

    md.append(f"\n> **官方投流锦囊**：符合要求的笔记单篇保底享 10万~20万 流量扶持，发布后务必[点击提交收集表](https://doc.weixin.qq.com/forms/ANAAyQcbAAgAbEAGAb_AKoCNPRTWz2o5f)！")
    return "\n".join(md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书理性讨论内容审核工具")
    parser.add_argument("--title", type=str, required=True, help="笔记标题")
    parser.add_argument("--content", type=str, default="", help="笔记正文或大纲")
    parser.add_argument("--category", type=str, default="通用", help="所属垂类")
    args = parser.parse_args()

    res = audit_note(args.title, args.content, args.category)
    print(format_markdown_report(res))
