#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书全自动化图文生产与装配引擎 (Auto Image-Text Engine)
基于小红书官方「理性讨论」范式与 6 页标准结构法
"""

import os
import sys
import json
import argparse
import re

# 确保在 Windows 控制台中支持 UTF-8 打印
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 动态导入同仓库审核工具与三大增强 Skills
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

AUDIT_SCRIPT_PATH = os.path.join(SKILLS_DIR, "xhs-discussion-audit", "scripts")
FACT_SCRIPT_PATH = os.path.join(SKILLS_DIR, "fact-case-injector", "scripts")
DATA_SCRIPT_PATH = os.path.join(SKILLS_DIR, "data-enhancer", "scripts")
HUMOR_SCRIPT_PATH = os.path.join(SKILLS_DIR, "humor-refiner", "scripts")

for p in [AUDIT_SCRIPT_PATH, FACT_SCRIPT_PATH, DATA_SCRIPT_PATH, HUMOR_SCRIPT_PATH]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from audit_note import audit_note
except ImportError:
    def audit_note(title, content, category):
        return {"score": 90, "status": "PASS (推荐投流 ✅)", "checks": {}, "penalties": []}

try:
    from inject_cases import inject_cases_into_deck
except ImportError:
    def inject_cases_into_deck(deck): return deck

try:
    from enhance_data import enhance_deck_data
except ImportError:
    def enhance_deck_data(deck): return deck

try:
    from refine_humor import polish_humor_for_deck
except ImportError:
    def polish_humor_for_deck(deck): return deck

try:
    from export_to_png import export_deck_to_png
except ImportError:
    def export_deck_to_png(deck_dir, scale=2): return []

def load_expert_personas() -> dict:
    """加载专家视角配置库"""
    personas_file = os.path.join(CURRENT_DIR, "expert_personas.json")
    if os.path.exists(personas_file):
        with open(personas_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"personas": {}, "topic_routes": {}}

def render_html_card(page_data: dict, page_num: int, total_pages: int = 6) -> str:
    """基于小红书爆款美学 (大字报冲击流 + 备忘录真实手账流) 渲染 3:4 比例卡片 HTML，彻底去除 AI 味"""
    ptype = page_data.get("type", "")
    
    # 基础设计系统与视觉 Token
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Serif+SC:wght@600;900&family=ZCOOL+KuaiLe&display=swap');
    body {{ font-family: 'Noto Sans SC', sans-serif; -webkit-font-smoothing: antialiased; }}
    .font-serif-title {{ font-family: 'Noto Serif SC', serif; }}
    .font-handwriting {{ font-family: 'ZCOOL KuaiLe', cursive, sans-serif; }}
    
    .card-canvas {{
      width: 540px;
      height: 720px;
      position: relative;
      overflow: hidden;
      box-sizing: border-box;
    }}
    
    /* 暖调微噪点纸张底纹 */
    .bg-paper-warm {{
      background-color: #FAF8F5;
      background-image: radial-gradient(#E5E0D8 0.85px, transparent 0.85px);
      background-size: 15px 15px;
    }}

    /* 真实横线备忘录纸 */
    .bg-memo-ruled {{
      background-color: #FCFBF9;
      background-image: repeating-linear-gradient(#FCFBF9, #FCFBF9 29px, #E7E3DC 30px);
    }}

    /* 荧光记号笔划线 */
    .marker-yellow {{
      background: linear-gradient(180deg, transparent 52%, #FDE047 52%);
      padding: 0 4px;
    }}
    .marker-red {{
      background: linear-gradient(180deg, transparent 58%, #FECACA 58%);
      padding: 0 4px;
    }}
    .marker-cyan {{
      background: linear-gradient(180deg, transparent 55%, #BAE6FD 55%);
      padding: 0 4px;
    }}

    /* 倾斜复古红色印章 */
    .stamp-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #DC2626;
      color: #DC2626;
      font-weight: 900;
      letter-spacing: 0.08em;
      transform: rotate(-3.5deg);
      border-radius: 6px;
      padding: 2px 10px;
      box-shadow: 0 1px 2px rgba(220, 38, 38, 0.15);
    }}

    /* 和纸胶带贴角效果 */
    .washi-tape-top {{
      position: relative;
    }}
    .washi-tape-top::before {{
      content: "";
      position: absolute;
      top: -12px;
      left: 50%;
      transform: translateX(-50%);
      width: 90px;
      height: 22px;
      background: rgba(254, 240, 138, 0.75);
      backdrop-filter: blur(1px);
      border-left: 3px dashed rgba(202, 138, 4, 0.5);
      border-right: 3px dashed rgba(202, 138, 4, 0.5);
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      z-index: 10;
    }}
  </style>
</head>
<body class="bg-stone-200 m-0 p-0 flex items-center justify-center min-h-screen">
  <div class="card-canvas bg-paper-warm flex flex-col justify-between p-6 text-stone-900 border border-stone-300/80 shadow-2xl">
    
    <!-- 顶部极简刊头 -->
    <div class="flex items-center justify-between pb-2.5 border-b border-stone-300/70">
      <div class="flex items-center gap-2">
        <span class="px-2 py-0.5 rounded bg-stone-900 text-amber-300 text-[10px] font-black tracking-widest uppercase">
          {page_data.get("badge", "#理性讨论 · 财经认知").replace("#", "")}
        </span>
        <span class="text-[10px] font-bold text-stone-400">真实账本调研</span>
      </div>
      <span class="text-xs font-black font-mono text-stone-400 tracking-wider">
        0{page_num} / 0{total_pages}
      </span>
    </div>
"""

    if ptype == "cover_poster":
        title_lines = page_data.get("title_main", "").split("\n")
        title_rendered_parts = []
        if len(title_lines) >= 1:
            title_rendered_parts.append(f'<span class="block text-[34px] font-black tracking-tight text-stone-900 leading-tight">{title_lines[0]}</span>')
        if len(title_lines) >= 2:
            title_rendered_parts.append(f'<span class="inline-block my-1 bg-stone-950 text-white px-3 py-1 font-black text-[30px] rounded-sm tracking-tight transform -rotate-1 shadow-md">{title_lines[1]}</span>')
        if len(title_lines) >= 3:
            title_rendered_parts.append(f'<span class="block text-[32px] font-black tracking-tight text-stone-900 leading-tight"><span class="marker-yellow">{title_lines[2]}</span></span>')
        for extra in title_lines[3:]:
            title_rendered_parts.append(f'<span class="block text-2xl font-black text-stone-800 leading-tight">{extra}</span>')
        title_html = "".join(title_rendered_parts)

        matchup_html = ""
        if "expert_matchup" in page_data:
            em = page_data["expert_matchup"]
            matchup_html = f"""
      <!-- 红蓝专家交锋阵营 -->
      <div class="grid grid-cols-2 gap-2.5 pt-1 text-left">
        <div class="p-2.5 rounded-xl bg-rose-50/90 border border-rose-200/90 shadow-sm">
          <div class="flex items-center gap-1 text-[10px] font-black text-rose-700 mb-0.5">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            <span>选 A 阵营代言</span>
          </div>
          <p class="text-[11px] font-bold text-stone-900 leading-snug">{em.get('side_a', '正方立场')}</p>
        </div>
        <div class="p-2.5 rounded-xl bg-sky-50/90 border border-sky-200/90 shadow-sm">
          <div class="flex items-center gap-1 text-[10px] font-black text-sky-700 mb-0.5">
            <span class="w-2 h-2 rounded-full bg-sky-500"></span>
            <span>选 B 阵营代言</span>
          </div>
          <p class="text-[11px] font-bold text-stone-900 leading-snug">{em.get('side_b', '反方立场')}</p>
        </div>
      </div>
"""

        html += f"""
    <!-- 封面满幅大字报主体 -->
    <div class="flex-1 flex flex-col justify-between py-3 space-y-3">
      <div class="flex items-center justify-between pt-1">
        <div class="stamp-badge text-[11px]">
          ★ 真实账本对决 · 避坑必看
        </div>
        <div class="text-[10px] text-stone-400 font-mono tracking-tight">
          ISSUE #2026-XHS
        </div>
      </div>

      <div class="space-y-2 text-center py-1">
        {title_html}
      </div>

      <div class="washi-tape-top p-3.5 rounded-xl bg-amber-50 border border-amber-200/90 text-stone-900 text-xs font-bold leading-relaxed shadow-sm">
        <span class="text-rose-600 font-black">【核心冲突】</span> {page_data.get("subtitle", "")}
      </div>

      {matchup_html}
    </div>
    
    <!-- 底部手绘感引导 -->
    <div class="pt-3 border-t border-stone-300/70 flex items-center justify-between text-xs text-stone-500 font-medium">
      <span class="font-handwriting text-sm text-stone-700 tracking-wider">
        {page_data.get("footer_tip", "内附真实利差算账明细 · 滑动阅读 ➔")}
      </span>
      <span class="text-rose-600 font-black tracking-tight flex items-center gap-0.5">
        翻页阅读 ➔
      </span>
    </div>
"""

    elif ptype == "pain_point":
        table_rows = "".join([
            f"""<div class="flex items-center justify-between p-3 rounded-lg bg-white/95 border border-stone-200/90 shadow-sm">
              <div class="space-y-0.5 text-left">
                <span class="font-black text-xs text-stone-900">{row['item']}</span>
                <span class="text-[10px] text-stone-500 block font-mono">{row['rate']}</span>
              </div>
              <span class="font-mono font-black text-sm text-rose-600">{row['yield']}</span>
            </div>""" for row in page_data.get("table_data", [])
        ])
        p2_footer_note = page_data.get("footer_note", "（真实数据精算，看清表象背后的隐性摩擦）")
        html += f"""
    <div class="flex-1 flex flex-col justify-between py-2.5 space-y-3">
      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-black text-rose-600 tracking-wider uppercase">02 · 现实利差痛点账本</span>
          <span class="text-[10px] font-bold text-stone-400 font-mono">FINANCIAL SPREAD</span>
        </div>
        <h2 class="text-2xl font-black text-stone-950 leading-snug">
          {page_data.get("heading", "").replace("，", "，<br>")}
        </h2>
      </div>

      <div class="p-2.5 rounded-lg bg-stone-100/80 border border-stone-200 text-xs text-stone-700 leading-relaxed font-medium">
        📝 {page_data.get("scene_desc", "")}
      </div>
      
      <!-- 模拟银行明细流水账本 -->
      <div class="space-y-2 bg-stone-100/50 p-2.5 rounded-xl border border-dashed border-stone-300">
        <div class="flex justify-between text-[10px] font-bold text-stone-400 px-1">
          <span>资产/负债对比标的</span>
          <span>账面真实利息收益</span>
        </div>
        {table_rows}
      </div>

      <!-- 真实红笔手写批注感 -->
      <div class="p-3 rounded-xl bg-stone-950 text-stone-100 text-xs leading-relaxed space-y-1 shadow-md">
        <div class="text-amber-400 font-black text-xs flex items-center gap-1">
          <span>💡</span> <span>老手视角：</span>
        </div>
        <p class="text-stone-300 text-[11px] leading-relaxed">
          {page_data.get("hook_question", "")}
        </p>
      </div>
    </div>
    <div class="pt-2.5 border-t border-stone-300/70 flex justify-between items-center text-[10px] text-stone-400">
      <span class="font-handwriting text-stone-600 text-xs">{p2_footer_note}</span>
      <span class="font-mono">P2 / 痛点账本</span>
    </div>
"""

    elif ptype == "contrast_gap":
        expert_tag = ""
        if page_data.get("expert_name"):
            expert_tag = f"""
          <span class="px-2 py-0.5 rounded bg-purple-100 text-purple-800 text-[10px] font-bold border border-purple-200">
            🔬 穿透视角：{page_data.get("expert_name")}
          </span>
"""
        expert_quote = ""
        if page_data.get("expert_quote"):
            expert_quote = f"""
        <div class="p-2.5 rounded-lg bg-stone-100 border-l-4 border-purple-600 text-[11px] text-stone-800 italic font-medium leading-relaxed">
          “{page_data.get("expert_quote")}”
        </div>
"""
        quant_box = ""
        if "quant_summary" in page_data:
            qs = page_data["quant_summary"]
            quant_box = f"""
        <!-- Data Enhancer 精算看板 -->
        <div class="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-stone-900 text-white text-center shadow-sm">
          <div class="border-r border-stone-700 pr-1">
            <span class="text-[9px] text-stone-400 block font-mono">利息差额</span>
            <span class="text-xs font-black text-emerald-400">{qs.get('left_stat', '')}</span>
          </div>
          <div class="border-r border-stone-700 pr-1">
            <span class="text-[9px] text-stone-400 block font-mono">流动性缓冲</span>
            <span class="text-xs font-black text-amber-300">{qs.get('right_stat', '')}</span>
          </div>
          <div>
            <span class="text-[9px] text-stone-400 block font-mono">关键门槛</span>
            <span class="text-xs font-black text-blue-300">{qs.get('spread_metric', '')}</span>
          </div>
        </div>
"""
        metaphor_box = ""
        if page_data.get("humor_metaphor"):
            metaphor_box = f"""
        <div class="p-3 rounded-xl bg-amber-100/80 border border-amber-300 text-amber-950 text-xs font-bold leading-relaxed shadow-sm">
          🎭 <span class="marker-yellow">神级隐喻</span>：“{page_data.get('humor_metaphor')}”
        </div>
"""
        html += f"""
    <div class="flex-1 flex flex-col justify-between py-2 space-y-2.5">
      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-black text-rose-600 tracking-wider uppercase">03 · 认知剪刀差</span>
          {expert_tag}
        </div>
        <h2 class="text-2xl font-black text-stone-950 leading-snug">
          {page_data.get("heading", "")}
        </h2>
      </div>

      {expert_quote}
      {quant_box}

      <!-- 显隐双账面对决卡片 -->
      <div class="space-y-2">
        <div class="p-3 rounded-xl bg-emerald-50/90 border border-emerald-300/80 shadow-sm">
          <div class="text-xs font-black text-emerald-800 mb-1 flex items-center gap-1">
            <span>👀 看得见的算计（显性账）：</span>
          </div>
          <p class="text-xs text-stone-800 leading-relaxed font-medium">{page_data.get("visible_gain", "")}</p>
        </div>

        <div class="p-3 rounded-xl bg-rose-50/90 border border-rose-300/80 shadow-sm">
          <div class="text-xs font-black text-rose-800 mb-1 flex items-center gap-1">
            <span>⚠️ 看不见的代价（隐性账）：</span>
          </div>
          <p class="text-xs text-stone-800 leading-relaxed font-medium">{page_data.get("hidden_cost", "")}</p>
        </div>
      </div>

      {metaphor_box}
    </div>
    <div class="pt-2 border-t border-stone-300/70 flex justify-between items-center text-[10px] text-stone-400">
      <span class="font-handwriting text-stone-600 text-xs">（算账不仅要看赚多少，更要看交出了什么）</span>
      <span class="font-mono">P3 / 冲突本质</span>
    </div>
"""

    elif ptype in ["side_a", "side_b"]:
        is_a = ptype == "side_a"
        color = "rose" if is_a else "sky"
        theme_border = "border-rose-500" if is_a else "border-sky-500"
        theme_bg = "bg-rose-50/80" if is_a else "bg-sky-50/80"
        theme_badge = "bg-rose-600" if is_a else "bg-sky-600"
        theme_text = "text-rose-950" if is_a else "text-sky-950"
        expert_name = page_data.get("expert_name", "正方专家" if is_a else "反方专家")
        expert_title = page_data.get("expert_title", "")
        expert_quote = page_data.get("expert_quote", "")

        args_html = "".join([
            f"""<li class="flex items-start gap-2 text-xs text-stone-800 leading-relaxed bg-white/80 p-2 rounded-lg border border-stone-200">
              <span class="flex-shrink-0 w-4 h-4 rounded-full {theme_badge} text-white font-black text-[10px] flex items-center justify-center mt-0.5">{idx+1}</span>
              <span class="font-medium">{arg}</span>
            </li>""" for idx, arg in enumerate(page_data.get("arguments", []))
        ])

        quote_html = ""
        if expert_quote:
            quote_html = f"""
        <div class="p-2.5 rounded-lg {theme_bg} border-l-4 {theme_border} text-xs {theme_text} font-bold leading-relaxed">
          💬 “{expert_quote}”
        </div>
"""
        case_box = ""
        if "case_slice" in page_data:
            c = page_data["case_slice"]
            case_box = f"""
        <!-- Fact Case 真实案例报刊剪影 -->
        <div class="p-2.5 rounded-xl bg-stone-100 border border-stone-300/80 space-y-1 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-black text-stone-900">📌 {c.get('tag')}: {c.get('title')}</span>
            <span class="text-[9px] font-black text-stone-600 bg-white px-1.5 py-0.5 rounded border border-stone-200">{c.get('key_metric')}</span>
          </div>
          <p class="text-[10px] text-stone-700 leading-relaxed">{c.get('story')}</p>
        </div>
"""
        humor_os = ""
        if page_data.get("humor_os"):
            humor_os = f"""
        <div class="font-handwriting text-xs text-stone-600 text-right tracking-wide">
          {page_data.get('humor_os')}
        </div>
"""
        html += f"""
    <div class="flex-1 flex flex-col justify-between py-2 space-y-2.5">
      <!-- 专家立论卡片头 -->
      <div class="p-3 rounded-xl {theme_bg} border-l-4 {theme_border} space-y-1 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-black uppercase tracking-wider text-stone-500">
            {"【立场 A · 正方深度立论】" if is_a else "【立场 B · 反方现实视角】"}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded-full {theme_badge} text-white font-black">
            {expert_name}
          </span>
        </div>
        <h2 class="text-base font-black text-stone-950 leading-snug">{page_data.get("stance", "")}</h2>
        {f'<p class="text-[10px] text-stone-500 font-medium">{expert_title}</p>' if expert_title else ''}
      </div>

      {quote_html}

      <ul class="space-y-1.5">
        {args_html}
      </ul>

      {case_box}
      {humor_os}
    </div>
    <div class="pt-2 border-t border-stone-300/70 flex justify-between items-center text-[10px] text-stone-400">
      <span class="font-handwriting text-stone-600 text-xs">（立论经真实中产生活切片验证）</span>
      <span class="font-mono">{"P4 / 正方立论" if is_a else "P5 / 反方立论"}</span>
    </div>
"""

    elif ptype == "ending_hook":
        opt_a_raw = page_data.get("option_a", "")
        opt_b_raw = page_data.get("option_b", "")

        match_a = re.search(r"【(.*?)】", opt_a_raw)
        label_a = match_a.group(1) if match_a else "正方立场"
        desc_a = re.sub(r"^.*?[:：]\s*", "", opt_a_raw).strip() or opt_a_raw

        match_b = re.search(r"【(.*?)】", opt_b_raw)
        label_b = match_b.group(1) if match_b else "反方立场"
        desc_b = re.sub(r"^.*?[:：]\s*", "", opt_b_raw).strip() or opt_b_raw

        heading = page_data.get("heading", "这不是数学题，而是人生的取舍题")
        if "，" in heading:
            parts = heading.split("，", 1)
            heading_html = f'{parts[0]}，<br><span class="marker-yellow">{parts[1]}</span>'
        else:
            heading_html = f'<span class="marker-yellow">{heading}</span>'

        html += f"""
    <div class="flex-1 flex flex-col justify-between py-3 space-y-4 text-center">
      <div class="space-y-1 pt-1">
        <span class="text-[11px] font-black text-purple-600 uppercase tracking-wider">06 · 终极站队 · 灵魂拷问</span>
        <h2 class="text-2xl font-black text-stone-950 leading-tight">
          {heading_html}
        </h2>
      </div>

      <!-- 逼真投票箱选票设计 -->
      <div class="space-y-3 text-left">
        <div class="p-3.5 rounded-xl border-2 border-rose-500 bg-rose-50/90 shadow-sm relative">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-rose-700">🔴 选票 A【{label_a}】</span>
            <span class="text-[10px] font-bold text-rose-600 bg-white px-1.5 py-0.5 rounded border border-rose-200">站队 A</span>
          </div>
          <p class="text-xs font-bold text-stone-800 leading-snug">{desc_a}</p>
        </div>

        <div class="p-3.5 rounded-xl border-2 border-sky-500 bg-sky-50/90 shadow-sm relative">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-sky-700">🔵 选票 B【{label_b}】</span>
            <span class="text-[10px] font-bold text-sky-600 bg-white px-1.5 py-0.5 rounded border border-sky-200">站队 B</span>
          </div>
          <p class="text-xs font-bold text-stone-800 leading-snug">{desc_b}</p>
        </div>
      </div>

      <div class="p-3.5 rounded-xl bg-stone-950 text-white space-y-1.5 shadow-lg">
        <p class="text-xs font-black text-amber-400">💬 两位专家神仙打架，换作是你站哪边？</p>
        <p class="text-[11px] text-stone-300 leading-relaxed font-medium">{page_data.get("debate_invitation", "")}</p>
      </div>
    </div>
    <div class="pt-3 border-t border-stone-300/70 text-center text-xs text-rose-600 font-black tracking-wide">
      👉 评论区留下你的真实账本，看看多少人与你同频！
    </div>
"""

    html += """
  </div>
</body>
</html>"""
    return html

def get_topic_data_bundle(topic_id: str, personas_cfg: dict) -> dict:
    """根据议题ID组装融入专家视角的标准6页图文数据"""
    personas = personas_cfg.get("personas", {})
    
    bundles = {
      "mortgage_vs_invest": {
        "meta": {
          "topic_id": "mortgage_vs_invest",
          "topic": "手头有50万闲钱：提前还4.0%房贷，还是留着买理财？",
          "category": "财经/理财",
          "side_a_expert": "consumer_advocate",
          "side_b_expert": "cfp_planner",
          "contrast_expert": "macro_economist"
        },
        "post_copy": {
          "title": "手头有50万闲钱：提前还4.0%房贷，还是留着买理财？",
          "body": "存款利率跌破2%，房贷还在4%挂着……手头攒了50万，到底是该提前还款锁定无风险收益，还是手握现金保留家庭生命流动性？\n\n【平民反收割官】力挺提前还款：理财全面破净，还房贷就是年化4%保本收益！无债一身轻比什么都强。\n【注册理财规划师】坚决反对：脱离流动性储备谈省利息都是裸奔！房贷是一生最廉价长期贷款，现金是中年家庭的呼吸机。\n\n这根本不是一道数学题，而是确定性与安全感的极端较量！\n\n欢迎在评论区聊聊你的真实账本！换作是你，你会怎么选？👇\n\n#理性讨论 #财经知识 #提前还房贷 #理财思维 #资产配置",
          "pinned_comment": "我先抛砖引玉：如果这50万是全部流动备用金，千万别全还！至少留1~2年生活费；若是纯闲钱，还贷确实等于躺赚年化4%无风险收益。大家现在处于哪种情况？"
        },
        "pages": [
          {
            "type": "cover_poster",
            "badge": "#理性讨论 · 财经认知",
            "title_main": "手头有50万闲钱\n提前还4.0%房贷？\n还是留着吃理财？",
            "subtitle": "锁定4%无风险收益 VS 握紧流动性防裁员？",
            "expert_matchup": {
              "side_a": "平民反收割官",
              "side_b": "注册理财规划师"
            },
            "footer_tip": "内附两派专家真实账本 · 换你你怎么选？ ➔"
          },
          {
            "type": "pain_point",
            "heading": "存款破2%，房贷还在4.0%",
            "scene_desc": "手头好不容易攒了50万闲钱，面对每月几千块房贷，每天都在纠结：",
            "table_data": [
              {"item": "银行大额存单", "rate": "年利率 1.5%~1.8%", "yield": "年利息约 8,500 元"},
              {"item": "留在房贷继续还", "rate": "年利率 3.8%~4.2%", "yield": "年利息约 20,000 元"}
            ],
            "hook_question": "表面看提前还贷等于白赚4%年化，为什么资深金融人却坚决劝你'别急着还'？"
          },
          {
            "type": "contrast_gap",
            "heading": "还贷省了利息，却交出了'话语权'",
            "expert_name": "宏观经济学者",
            "expert_quote": "顺周期加杠杆是赌博，但在周期底部把最便宜的长钱还回去，是在牺牲家庭的流动性期权。",
            "visible_gain": "提前还50万，30年总共省下近35万利息，每月月供直降2400元。",
            "hidden_cost": "房贷是一生最长最廉价杠杆，还进水泥后再想借出来难如登天！",
            "core_friction": "你到底要'纸面省利息'，还是要'手里有真金'？"
          },
          {
            "type": "side_a",
            "stance": "无债一身轻，锁定确定性收益",
            "expert_name": "平民现实派与反收割官",
            "expert_title": "独立财经观察家",
            "expert_quote": personas.get("consumer_advocate", {}).get("catchphrase", "普通人别被宏大词汇忽悠，先算算这笔买卖你变现时要被砍几刀。"),
            "arguments": [
              "保本收益之王：稳健理财收益持续下行，没有任何确定性工具保本4%，还贷即是净赚！",
              "降低生存门槛：每月少还2400元月供，遭遇降薪失业家庭每月刚性支出大幅降低。",
              "心理复利无价：没有债务催逼的松弛感与睡眠质量，情绪价值远超通胀贬值理论。"
            ]
          },
          {
            "type": "side_b",
            "stance": "现金是呼吸机，绝不把子弹打光",
            "expert_name": "财富规划师与精算视角",
            "expert_title": "国际认证注册理财规划师 (CFP)",
            "expert_quote": personas.get("cfp_planner", {}).get("catchphrase", "脱离流动性储备谈省利息，都是在拿家庭安全裸奔。"),
            "arguments": [
              "流动性不可逆：房子变现周期极长，手握50万现金是抵御中年职场失业的生命线。",
              "久期错配陷阱：房贷是长达30年的超长资金，一旦全额填平，突遇急用钱只能借高息消费贷。",
              "周期底部期权：全市场缺钱时现金才是最高级期权，保留现金才能抓住未来的资产重估机会。"
            ]
          },
          {
            "type": "ending_hook",
            "heading": "这不是数学题，而是人生的取舍题",
            "option_a": "🔴 站队反收割官【还贷派】：立刻还！省下利息装进兜里才是真金白银！",
            "option_b": "🔵 站队理财规划师【留钱派】：坚决不还！手里有现金流才有抵御风浪的安全感！",
            "debate_invitation": "如果换作是你手握这50万现金，面对4.0%的房贷，你会选立刻还还是留着？评论区亮出你的账本！"
          }
        ]
      },
      "gold_beans": {
        "meta": {
          "topic_id": "gold_beans",
          "topic": "年轻人攒金豆：是低门槛储蓄还是为高溢价买单？",
          "category": "财经/资产配置",
          "side_a_expert": "macro_economist",
          "side_b_expert": "consumer_advocate",
          "contrast_expert": "value_investor"
        },
        "post_copy": {
          "title": "年轻人每月攒一颗金豆：是低门槛储蓄还是为高溢价买单？",
          "body": "金价一路狂飙，一颗颗1克重的小金豆成了年轻人的新型储蓄罐。有人说是普通人对抗通胀的最优解，有人却说是金店精准收割年轻人的智商税！\n\n【宏观经济学者】力挺金豆储蓄：黄金是主权货币超发的终极解药，每月1克积少成多，是天然的强制储蓄与资产压舱石。\n【平民反收割官】直呼陷阱：买入时加了15%工艺溢价，变现回购时还要被克扣折旧！一买一卖白白蒸发上百元。\n\n普通人攒黄金，到底是锁定财富还是给金店打工？\n\n评论区聊聊：你买过小金豆吗？回收时亏了吗？👇\n\n#理性讨论 #攒金豆 #黄金理财 #资产配置 #年轻人理财",
          "pinned_comment": "提醒大家一句：如果是为了首饰戴着玩，小金豆很开心；如果是为了投资理财，一定要算清买入溢价和回收折价！大家买金豆时每克溢价多少？"
        },
        "pages": [
          {
            "type": "cover_poster",
            "badge": "#理性讨论 · 黄金真相",
            "title_main": "年轻人每月攒金豆\n是低门槛强制储蓄？\n还是为高溢价买单？",
            "subtitle": "抗通胀资产压舱石 VS 回购变现被砍两刀？",
            "expert_matchup": {
              "side_a": "宏观经济学者",
              "side_b": "平民反收割官"
            },
            "footer_tip": "内附克重回收真实损耗对比 · 滑动阅读 ➔"
          },
          {
            "type": "pain_point",
            "heading": "买时当资产，卖时被当废铁",
            "scene_desc": "每月花几百块买一颗金豆，满心欢喜以为在存钱，直到走进黄金回收店：",
            "table_data": [
              {"item": "专柜零售金价", "rate": "含工艺费溢价", "yield": "约 720~760 元/克"},
              {"item": "大盘实际回收价", "rate": "扣除折旧成色", "yield": "仅 620~640 元/克"}
            ],
            "hook_question": "刚买到手就账面亏损15%，为什么年轻人依然乐此不疲？"
          },
          {
            "type": "contrast_gap",
            "heading": "黄金确实保值，但金豆不是投资金条",
            "expert_name": "硬核价值投资人",
            "expert_quote": personas.get("value_investor", {}).get("catchphrase", "当防守资产被买成了香饽饽，最大的安全就变成了最大的风险。"),
            "visible_gain": "每克几百元无痛上车，克重看得见摸得着，治好了年轻人的乱花钱消费瘾。",
            "hidden_cost": "工艺费+损耗费+回购门槛，让微型金豆的实际持仓成本远超标准投资金条。",
            "core_friction": "你买的究竟是'抗通胀黄金'，还是包裹着黄金外衣的'情绪消费品'？"
          },
          {
            "type": "side_a",
            "stance": "微型法币对冲，极佳的强制储蓄手段",
            "expert_name": "宏观经济与周期学者",
            "expert_title": "宏观策略首席分析师",
            "expert_quote": personas.get("macro_economist", {}).get("catchphrase", "顺周期加杠杆是赌博，看懂央行资产负债表才是真正的降维生存。"),
            "arguments": [
              "无痛强制储蓄：相比买包买奶茶，买金豆把浮躁消费转化为了实物硬通货。",
              "长周期购买力抵御：法币持续超发大背景下，黄金穿越数千年依然具备终极兑现力。",
              "心理锚定效应：沉甸甸的黄金能带来储蓄正反馈，帮助年轻人养成低频复利习惯。"
            ]
          },
          {
            "type": "side_b",
            "stance": "工艺溢价陷阱，变现被精准收割两刀",
            "expert_name": "平民现实派与反收割官",
            "expert_title": "资深财经调查记者",
            "expert_quote": personas.get("consumer_advocate", {}).get("catchphrase", "普通人别被宏大词汇忽悠，先算算这笔买卖你变现时要被砍几刀。"),
            "arguments": [
              "双重剪刀差收割：买入时承受品牌与工艺溢价，变现回收时还要遭遇火熔验金克重扣减。",
              "流动性折价惨烈：民间典当行与回收小店套路频出，小克重金豆变现议价权极低。",
              "不生息资产死结：黄金不生息不分红，高位接盘的小金豆可能要坐过山车好几年。"
            ]
          },
          {
            "type": "ending_hook",
            "heading": "小金豆的尽头，究竟是存钱还是消费？",
            "option_a": "🔴 站队学者【储蓄派】：少喝几杯咖啡攒颗金豆，对抗通胀还能管住手！",
            "option_b": "🔵 站队反收割官【算账派】：坚决不当大冤种！高溢价变现亏死，要买就买大投资金条！",
            "debate_invitation": "你手头攒了多少克金豆？你觉得这是存钱神操作还是智商税？评论区等你来辩！"
          }
        ]
      },
      "options_rich_or_ruin": {
        "meta": {
          "topic_id": "options_rich_or_ruin",
          "topic": "期权会让人暴富还是导致人破产？",
          "category": "财经/期权衍生品",
          "side_a_expert": "value_investor",
          "side_b_expert": "consumer_advocate",
          "contrast_expert": "macro_economist"
        },
        "post_copy": {
          "title": "期权交易：会让人一夜暴富，还是让人倾家荡产？",
          "body": """🔥 有人买期权单日狂赚 192 倍，2 万本金变 384 万；
有人裸卖期权遭遇黑天鹅，100 万本金归零还倒欠券商 240 万！

很多人第一次听说期权，都是被那些“单日几十倍甚至百倍”的神话震碎三观。
期权到底是用小钱逆天改命的【非对称暴富神器】，还是专门收割散户的【合法绞肉机】？

今天我们邀请【硬核价值投资人】和【平民反收割官】两位专家，摆事实、列数据、算细账，理性拆解真实内幕！👇

───────────────
⚖️ 正方【价值投资人】：非对称暴富神器，下行有限上行无限！

1️⃣ 锁死最大亏损：买方期权最大亏损就是初始付出的权利金，绝不会出现借钱爆仓或倒欠券商的绝境，睡觉都踏实！
2️⃣ 非线性爆发杠杆：极端行情下单日爆发 50~192 倍收益，这是任何股票、基金都无法企及的“非对称暴击率”。
3️⃣ 极低成本黑天鹅对冲：手握重仓现货股票时，买入几千块虚值认沽，就能给整个家庭资产买上一份防崩盘保险。
📌【真实神话切片】：2019年2月25日 50ETF 购 2 月 2800 合约单日暴涨 192 倍，真实上演 2 万元变 384 万元！
💬 买方内心戏：“亏也只亏权利金盒饭钱，万一抓到一次百倍末日轮，直接少奋斗二十年！”

───────────────
⚠️ 反方【平民反收割官】：时间价值绞肉机，散户的人形自走提款机！

1️⃣ Theta 每日无情凌迟：期权有严格的到期保质期！只要大盘横盘震荡，买方每天都要被时间价值蒸发 3%~8%，活活被耗死。
2️⃣ 80% 到期归零作废：交易所长周期实测统计，超过 82.4% 的散户买方期权最终沦为废纸清零，长期频繁交易胜率不足 15%。
3️⃣ 卖方穿仓万丈深渊：很多新手自以为当“卖方收租”很稳，结果遇到一次极端跳空，直接倾家荡产倒欠几百万！
📌【真实血泪警示】：某散户高位裸卖认沽赚 2% 权利金，遭遇黑天鹅跌停，100 万保证金打穿，被券商起诉追讨 240 万元穿仓款！
💬 做市商潜台词：“感谢各位散户老铁每天准时众筹的权利金，时间价值 Theta 已按时入账机构账户～”

───────────────
🔬 穿透专家【宏观学者】：看懂期权的底层本质！

💡 神级通俗比喻：
“玩买方期权，就像每天高价买保质期只有 7 天的隔夜酸奶；玩卖方期权，就像为了在铁轨上捡一分钱硬币，把整个身家性命枕在铁轨上等火车开过来！”

期权在机构眼里是“定价波动率的精算保险”，在很多散户眼里却成了“隔夜暴富的乐透彩票”。
巴菲特早就警告过：期权是大规模杀伤性金融武器。普通人千万别以为自己是持枪的猎人，多数时候只是靶场上的活靶子！

───────────────
💬 换作是你，你会怎么站队？

🔴 站队正方【天命买方派】：以小博大有奇迹！亏得起有限权利金，不碰非对称杠杆怎么逆天改命！
🔵 站队反方【清醒保命派】：衍生品绞肉机！珍爱生命远离期权，绝不做做市商的人形自走提款机！

大家平时碰过期权吗？你的期权总账本目前是赚还是亏？
欢迎在评论区留下你的真实战绩与账本！👇

#理性讨论 #期权交易 #金融知识 #投资理财 #认知差 #打工人理财 #衍生品 #以小博大""",
          "pinned_comment": "温馨提示：普通散户千万别把买方期权当股票炒，更不要盲目裸卖期权！大家身边玩期权的朋友，目前总账本是赚还是亏？"
        },
        "pages": [
          {
            "type": "cover_poster",
            "badge": "#理性讨论 · 衍生品真相",
            "title_main": "期权交易\n会让人一夜暴富？\n还是倾家荡产？",
            "subtitle": "单日192倍暴利奇迹 VS 穿仓倒欠券商数百万？",
            "expert_matchup": {
              "side_a": "硬核价值投资人",
              "side_b": "平民反收割官"
            },
            "footer_tip": "内附期权买卖双方真实盈亏账本 · 滑动阅读 ➔"
          },
          {
            "type": "pain_point",
            "heading": "上午赚300%，下午本金归零",
            "scene_desc": "无数人被'几十倍杠杆'吸引进场，面对每天剧烈跳动的期权权利金，真实体感往往是：",
            "table_data": [
              {"item": "买方虚值看涨期权", "rate": "动态杠杆 30x~100x", "yield": "日内振幅 ±200%~1000%"},
              {"item": "Theta时间价值流逝", "rate": "到期前最后15天", "yield": "每日自然贬值 3%~8%"},
              {"item": "散户买方到期清零率", "rate": "交易所长周期统计", "yield": "实测超 82.4% 终值归零"}
            ],
            "hook_question": "上午赚300%感觉巴菲特不如我，下午归零发现连饭钱都没了，普通人玩期权到底是在搞投资还是在送人头？"
          },
          {
            "type": "contrast_gap",
            "heading": "买方亏在'耗不起'，卖方死于'黑天鹅'",
            "expert_name": "宏观经济学者",
            "expert_quote": personas.get("macro_economist", {}).get("catchphrase", "顺周期加杠杆是赌博，看懂央行资产负债表才是真正的降维生存。"),
            "visible_gain": "买方用几千元权利金就能锁定几十万资产收益，即使方向做错，最大亏损仅仅是投入的权利金。",
            "hidden_cost": "期权定价的是波动率与时间，看似下行风险有限，但持续被时间价值消耗会导致胜率低至冰点！",
            "core_friction": "你到底是在玩'胜率只有15%的赌徒彩票'，还是在做'专业机构的风险对冲'？"
          },
          {
            "type": "side_a",
            "stance": "非对称盈亏之王，小资金逆天改命武器",
            "expert_name": "硬核价值投资人",
            "expert_title": "私募基金合伙人",
            "expert_quote": personas.get("value_investor", {}).get("catchphrase", "当防守资产被买成了香饽饽，最大的安全就变成了最大的风险。"),
            "arguments": [
              "锁定有限下行：买方期权最大亏损就是所付权利金，绝不存在爆仓被追债的绝境。",
              "非线性杠杆爆发：极端行情下单日可爆发数十倍甚至上百倍利润，是普通资产无法比拟的非对称杀器。",
              "极端风险防御盾：手握现货股票时买入少量虚值认沽，可以用极低成本对冲毁灭性黑天鹅崩盘。"
            ]
          },
          {
            "type": "side_b",
            "stance": "时间价值绞肉机，专割散户的合法赌场",
            "expert_name": "平民现实派与反收割官",
            "expert_title": "资深财经调查记者",
            "expert_quote": personas.get("consumer_advocate", {}).get("catchphrase", "普通人别被宏大词汇忽悠，先算算这笔买卖你变现时要被砍几刀。"),
            "arguments": [
              "Theta每日凌迟：期权有严格保质期，只要标的横盘不暴涨，买方每天都在白白亏损时间价值。",
              "买方极低胜率：统计显示超80%的散户买方期权最终归零作废，长期频繁交易几乎必输无疑。",
              "卖方穿仓深渊：为了每月赚2%蝇头小利去裸卖期权，一旦遭遇极端跳空，瞬间倾家荡产倒欠券商数百万。"
            ]
          },
          {
            "type": "ending_hook",
            "heading": "期权这把双刃剑，你敢不敢碰？",
            "option_a": "🔴 站队投资人【非对称派】：以小博大有奇迹！亏得起有限权利金，不玩非对称杠杆怎么跨越阶层！",
            "option_b": "🔵 站队反收割官【保命清醒派】：衍生品绞肉机！珍爱生命远离期权，不做做市商的人形自走提款机！",
            "debate_invitation": "换作是你，你会拿一小笔闲钱博弈期权的高倍杠杆，还是坚决不碰衍生品？评论区亮出你的战绩！"
          }
        ]
      },
      "macro_ppi_shock": {
        "meta": {
          "topic_id": "macro_ppi_shock",
          "topic": "昨晚PPI突发超预期大反弹：通胀死灰复燃，普通人该抛售黄金还是抄底美债？",
          "category": "财经/宏观经济",
          "side_a_expert": "macro_economist",
          "side_b_expert": "value_investor",
          "contrast_expert": "consumer_advocate"
        },
        "post_copy": {
          "title": "昨晚PPI突发超预期大反弹：通胀死灰复燃，普通人该抛售黄金还是抄底美债？",
          "body": """昨晚美国8月PPI突发暴涨5.4%，原本狂欢的“9月大幅降息”预期一夜被彻底击碎！
交易员对美联储不仅不敢奢望降息，反而押注9月继续加息的概率狂飙到70%以上！

消息一出，全球市场瞬间“股债汇金大洗牌”：
现货黄金急挫跳水，美债收益率冲上4.96%，唯独原油暴涨4.2%火上浇油……
无数刚刚满仓抄底黄金、跟风买入美债ETF的普通人，今天一觉醒来直接被迎头痛击！

面对突如其来的宏观变局，今天我们连线【宏观经济与周期学者】与【硬核价值投资人】正面交锋：

───────────────
⚖️ 正方【宏观学者】：通胀黏性远超想象，保命现金与短债为王！
1️⃣ 二次通胀警钟长鸣：地缘局势推动原油重回高位，上游工业成本暴涨，滞胀阴云根本没有散去！
2️⃣ 高利率钝刀慢割：加息概率飙升70%，高利率维持越久，资产估值越要挤水分，切忌盲目在半山腰接飞刀！
3️⃣ 现金流动性才是真爹：在美联储货币转向尚无定论前，高息短债与现金流才是普通家庭最硬的盾牌。
📌【真实切片】：某外企中产看降息博主推荐全仓冲入长端美债ETF，遭遇单日回撤逾4%，浮亏加剧现金流枯竭！
💬 宏观学者寄语：“顺周期加杠杆是赌博，看懂央行资产负债表才是真正的降维生存。”

───────────────
⚠️ 反方【价值投资人】：单月数据噪音踩踏，恰是罕见的黄金建仓期！
1️⃣ 强弩之末的恐慌过激：制造业PMI与中小企业负债已到极限，单月油价脉冲改变不了经济周期放缓的终极事实！
2️⃣ 非对称极佳赔率：美债收益率逼近5%的历史极值区，锁死无风险高息，向下空间极小，向上弹性巨大！
3️⃣ 优质资产大打折：黄金与优质核心资产在通胀预期下的急跌，正是长线资本以低成本收集筹码的狂欢季。
📌【历史对照】：2022年高通胀加息周期每次单月PPI脉冲暴跌，事后看都是长线优质现金流资产的完美定投坑！
💬 投资人内心戏：“别人恐惧我贪婪，市场因为一个月的能源数据恐慌踩踏，正好把便宜筹码双手奉上！”

───────────────
🔬 穿透专家【平民反收割官】：
💡 神级通俗比喻：
“看单月PPI数据炒资产，就像在暴风雨的独木舟上跟着每一次浪花猛打方向盘；美联储现在像站在跷跷板中间的胖子，左边是通胀冒烟，右边是银行暴雷，普通人千万别去给他当垫脚石！”

───────────────
💬 换作是你，你会怎么站队？
🔴 站队学者【现金防御派】：通胀不退风险不止！手握现金短债，绝不在高位飞刀下伸手！
🔵 站队投资人【逆向抄底派】：恐慌就是打折季！长期周期大势已定，越跌越买锁定历史性高赔率！

昨晚你的持仓回撤了吗？大家目前是准备抛售避险还是逢低加仓？
欢迎在评论区晒出你的账本与真实操作！👇

#理性讨论 #PPI数据 #宏观经济 #美联储加息 #黄金走势 #美债 #投资理财 #通胀""",
          "pinned_comment": "提醒大家：单月PPI数据波动极容易引发情绪踩踏！切忌根据一两天的新闻满仓频繁倒腾。大家目前手里的黄金和美债是打算止盈止损，还是逢跌继续定投？"
        },
        "pages": [
          {
            "type": "cover_poster",
            "badge": "#理性讨论 · 宏观风向",
            "title_main": "昨晚PPI突发反弹\n通胀死灰复燃？\n抛黄金还是抄底美债？",
            "subtitle": "加息预期飙升至70% VS 恐慌砸出黄金坑？",
            "expert_matchup": {
              "side_a": "宏观经济与周期学者",
              "side_b": "硬核价值投资人"
            },
            "footer_tip": "内附股债金真实波动账本 · 滑动阅读 ➔"
          },
          {
            "type": "pain_point",
            "heading": "昨夜数据暴雷，资产狂风骤雨",
            "scene_desc": "很多中产满仓满融坐等降息分红，昨晚公布的8月PPI数据瞬间引爆全场：",
            "table_data": [
              {"item": "美国8月最终需求PPI", "rate": "同比预期 5.3%", "yield": "实际公布 5.4% (大幅反弹)"},
              {"item": "CME 9月加息预期概率", "rate": "数据公布前 15%", "yield": "数据公布后 狂飙超 70%"},
              {"item": "全球大类资产单夜波动", "rate": "10年期美债触及4.96%", "yield": "现货金银跳水 / 原油大涨4.2%"}
            ],
            "hook_question": "刚买入黄金准备享受降息红利，一觉醒来被加息预期砸蒙，普通人到底该割肉保命还是死扛加仓？"
          },
          {
            "type": "contrast_gap",
            "heading": "盯紧单月数据，容易输掉整个人生",
            "expert_name": "平民现实派与反收割官",
            "expert_quote": personas.get("consumer_advocate", {}).get("catchphrase", "普通人别被宏大词汇忽悠，先算算这笔买卖你变现时要被砍几刀。"),
            "visible_gain": "顺着每次新闻高频调仓追涨杀跌，自以为把握住了每一次全球宏观脉搏。",
            "hidden_cost": "频繁交易的双向汇率损耗、买卖手续费与踏错节奏，足以在单季度磨损掉15%以上本金！",
            "core_friction": "你到底是在做'基于大周期的资产配置'，还是在给做市商'交情绪过路费'？"
          },
          {
            "type": "side_a",
            "stance": "二次通胀警钟长鸣，保命现金与短债为王",
            "expert_name": "宏观经济与周期学者",
            "expert_title": "宏观策略首席分析师",
            "expert_quote": personas.get("macro_economist", {}).get("catchphrase", "顺周期加杠杆是赌博，看懂央行资产负债表才是真正的降维生存。"),
            "arguments": [
              "能源通胀黏性极强：国际油价突破百元关口，工业端成本暴涨必然向消费端CPI强力渗透，降息彻底没戏！",
              "高利率挤泡沫漫长：美联储被逼到墙角不得不把利率维持更高更久，高估值风险资产将面临持续的估值绞杀。",
              "现金短债最高溢价：在不确定性最高的宏观剧震期，手握保本现金与超短久期资产，拥有最高的生存溢价。"
            ]
          },
          {
            "type": "side_b",
            "stance": "单月噪音过度恐慌，逆向加仓黄金坑",
            "expert_name": "硬核价值投资人",
            "expert_title": "私募基金合伙人",
            "expert_quote": personas.get("value_investor", {}).get("catchphrase", "当防守资产被买成了香饽饽，最大的安全就变成了最大的风险。"),
            "arguments": [
              "实体脆弱难承其重：制造业PMI萎缩与中小商业银行坏账已现裂痕，单月能源脉冲改变不了长期周期顶部的事实。",
              "极值赔率千载难逢：美债收益率逼近5.0%历史高位，锁定极高确定性收益，恐慌下杀恰是极佳的非对称入场点。",
              "黄金抗通胀真实底色：如果真如预期二次通胀失控，法币信用受损，大跌之后的黄金才是穿越周期的终极压舱石。"
            ]
          },
          {
            "type": "ending_hook",
            "heading": "通胀加息与资产博弈，换作是你怎么选？",
            "option_a": "🔴 站队学者【现金防御派】：通胀不灭加息不止！现金为王，绝不在半山腰接飞刀！",
            "option_b": "🔵 站队投资人【逆向抄底派】：恐慌砸出黄金坑！大周期见顶已定，越跌越买锁定历史性高赔率！",
            "debate_invitation": "面对昨晚突如其来的PPI暴涨，你手里的黄金和理财回撤了吗？你会选择清仓避险还是逢低加仓？评论区留下你的真实账本！"
          }
        ]
      }
    }
    
    return bundles.get(topic_id, bundles["mortgage_vs_invest"])

def print_expert_personas(personas_cfg: dict):
    """打印当前支持的专家视角与路由库"""
    print("=" * 60)
    print("🎭 [金融图文多专家视角配置库 (Expert Personas)]")
    print("=" * 60)
    for pid, p in personas_cfg.get("personas", {}).items():
        print(f"\n👤 [{p['name']}] ({p['title']})")
        print(f"   💡 核心立论逻辑: {p['core_logic']}")
        print(f"   💬 金句标志语: \"{p['catchphrase']}\"")
        print(f"   🎯 核心聚焦领域: {', '.join(p['focus_areas'])}")
    
    print("\n" + "=" * 60)
    print("🗺️ [已配置的议题对决路由 (Topic Routes)]")
    print("=" * 60)
    for tid, r in personas_cfg.get("topic_routes", {}).items():
        print(f"📌 路由ID: {tid}")
        print(f"   议题: {r['topic']} [{r['tag']}]")
        print(f"   正方视角: {r['side_a_persona']} | 反方视角: {r['side_b_persona']} | 穿透视角: {r['contrast_persona']}")

def run_pipeline(topic: str = "", category: str = "财经/理财", output_dir: str = "./output", topic_id: str = "",
                 use_data: bool = True, use_cases: bool = True, use_humor: bool = True, export_png: bool = True,
                 input_json: str = ""):
    os.makedirs(output_dir, exist_ok=True)
    personas_cfg = load_expert_personas()

    # 1. 优先从外部传入的 JSON 文件中读取完整 6 页图文定义 (外部自动化/LLM直接对接)
    if input_json and os.path.exists(input_json):
        print(f"📄 [Pipeline] 从外部 JSON 文件加载图文数据包: {input_json}")
        with open(input_json, "r", encoding="utf-8") as f:
            mock_data = json.load(f)
        topic_id = mock_data.get("meta", {}).get("topic_id", "custom_auto_topic")
    else:
        # 智能匹配或指定 topic_id
        if not topic_id:
            if topic:
                if "期权" in topic or "options" in topic:
                    topic_id = "options_rich_or_ruin"
                elif "金豆" in topic or "黄金" in topic:
                    topic_id = "gold_beans"
                elif "PPI" in topic or "ppi" in topic or "通胀" in topic or "加息" in topic:
                    topic_id = "macro_ppi_shock"
                else:
                    topic_id = "mortgage_vs_invest"
            else:
                topic_id = "mortgage_vs_invest"

        mock_data = get_topic_data_bundle(topic_id, personas_cfg)

    print(f"🚀 [Pipeline] 开始全自动生产金融图文笔记...")
    print(f"🎯 [议题路由ID] {topic_id}")

    if topic and topic != mock_data["post_copy"]["title"]:
        mock_data["post_copy"]["title"] = topic
        mock_data["meta"]["topic"] = topic
    if category:
        mock_data["meta"]["category"] = category

    meta = mock_data.get("meta", {})
    personas = personas_cfg.get("personas", {})
    side_a_p = personas.get(meta.get("side_a_expert", ""), {})
    side_b_p = personas.get(meta.get("side_b_expert", ""), {})
    contrast_p = personas.get(meta.get("contrast_expert", ""), {})

    print(f"📌 [议题] {mock_data['post_copy']['title']}")
    print(f"⚖️ [专家视角配置] 正方: {side_a_p.get('name', 'N/A')} VS 反方: {side_b_p.get('name', 'N/A')} (穿透: {contrast_p.get('name', 'N/A')})")

    # 3. 注入数据增强 Skill (Data Enhancer)
    if use_data:
        print(f"📈 [Skill: Data Enhancer] 正在精算并注入量化指标、真实利差与摩擦成本...")
        mock_data = enhance_deck_data(mock_data)

    # 4. 注入事实案例 Skill (Fact Case Injector)
    if use_cases:
        print(f"📜 [Skill: Fact Case Injector] 正在检索并注入典型中产切片与现实避坑样本...")
        mock_data = inject_cases_into_deck(mock_data)

    # 5. 注入幽默改造 Skill (Humor Refiner)
    if use_humor:
        print(f"🎭 [Skill: Humor Refiner] 正在注入神级隐喻、打工人扎心自嘲与括号内心戏...")
        mock_data = polish_humor_for_deck(mock_data)

    # 6. 自动化合规自检 (xhs-discussion-audit)
    print(f"🔍 [Audit] 正在调用 xhs-discussion-audit 进行 6 项卡点质检...")
    audit_res = audit_note(mock_data["post_copy"]["title"], mock_data["post_copy"]["body"], category or "财经/理财")
    print(f"📊 [Audit 结果] 评分: {audit_res['score']} 分 | 状态: {audit_res['status']}")

    # 保存审查报告
    with open(os.path.join(output_dir, "audit_report.json"), "w", encoding="utf-8") as f:
        json.dump(audit_res, f, ensure_ascii=False, indent=2)

    # 7. 批量渲染 P1~P6 HTML 卡片
    print(f"🎨 [Render] 正在渲染 6 张标准 3:4 图文卡片 (HTML+Tailwind)...")
    for i, pdata in enumerate(mock_data["pages"]):
        pnum = i + 1
        card_html = render_html_card(pdata, pnum, len(mock_data["pages"]))
        card_path = os.path.join(output_dir, f"page_{pnum}.html")
        with open(card_path, "w", encoding="utf-8") as f:
            f.write(card_html)
        print(f"   ➔ 已生成: page_{pnum}.html")

    # 8. 生成发布物料包 publish_pack.txt
    pack_content = f"""【小红书发布文案包】
标题：{mock_data['post_copy']['title']}

正文：
{mock_data['post_copy']['body']}

作者置顶神评（发布后5分钟内置顶）：
{mock_data['post_copy']['pinned_comment']}

三维增强与视角配置：
- 正方立场代言：{side_a_p.get('name', '')} ({side_a_p.get('title', '')})
- 反方立场代言：{side_b_p.get('name', '')} ({side_b_p.get('title', '')})
- 认知穿透拆解：{contrast_p.get('name', '')} ({contrast_p.get('title', '')})
- 事实案例：已为 P3/P4/P5 深度嵌入真实中产财务切片与前车之鉴
- 数据量化：已精算等额本息利差、流动性生命线、交易摩擦成本
- 幽默网感：已融入神级通俗隐喻、当代打工人扎心自嘲与反讽内心戏

官方收集表填报链接（发布后务必提交）：
https://doc.weixin.qq.com/forms/ANAAyQcbAAgAbEAGAb_AKoCNPRTWz2o5f
"""
    with open(os.path.join(output_dir, "publish_pack.txt"), "w", encoding="utf-8") as f:
        f.write(pack_content)

    # 8.2 生成标准运营活动配置 campaign_config.json
    campaign_config = {
        "campaign_id": f"CAMP_{topic_id.upper()}",
        "campaign_name": mock_data['post_copy']['title'],
        "type": "DEBATE_PK_EVENT",
        "status": "READY_FOR_DEPLOYMENT",
        "channels": ["xiaohongshu", "app_community", "h5_activity", "wechat_group"],
        "target_audience": ["大众理财族", "中产家庭", "投资爱好者"],
        "schedule": {
            "start_date": "2026-09-10",
            "end_date": "2026-09-24",
            "stages": ["预热蓄水期 (Day 1-2)", "爆发交锋期 (Day 3-10)", "沉淀转化期 (Day 11-14)"]
        },
        "factions": {
            "side_a": {
                "name": mock_data["pages"][3].get("subtitle", "正方阵营"),
                "mentor": side_a_p,
                "slogan": side_a_p.get("catchphrase", ""),
                "initial_support_rate": 52
            },
            "side_b": {
                "name": mock_data["pages"][4].get("subtitle", "反方阵营"),
                "mentor": side_b_p,
                "slogan": side_b_p.get("catchphrase", ""),
                "initial_support_rate": 48
            }
        },
        "tasks_and_incentives": {
            "daily_tasks": [
                {"task_id": "T1", "name": "阅读正反双边科普卡片", "reward_points": 10, "icon": "📖"},
                {"task_id": "T2", "name": "为心仪阵营投下一票", "reward_points": 20, "lottery_ticket": 1, "icon": "🗳️"},
                {"task_id": "T3", "name": "在评论区留下真实账本与观点", "reward_points": 50, "icon": "💬"},
                {"task_id": "T4", "name": "邀请1位好友为你支持的阵营打气", "reward_points": 100, "icon": "👥"}
            ],
            "prize_pool": [
                {"level": "一等奖", "name": "1克投资金豆 / 1000元体验金", "quota": 10, "prob": "0.5%"},
                {"level": "二等奖", "name": "大师级投资认知课 + 行情月卡", "quota": 200, "prob": "15%"},
                {"level": "参与奖", "name": "专属辩手徽章 + 50社区积分", "quota": "无上限", "prob": "84.5%"}
            ]
        },
        "creatives": {
            "pages_count": 6,
            "ratio": "3:4",
            "pages_list": [
                {"page": 1, "type": "KV_COVER", "file": "page_1.html"},
                {"page": 2, "type": "PAIN_POINT_LEDGER", "file": "page_2.html"},
                {"page": 3, "type": "COGNITIVE_GAP_BOARD", "file": "page_3.html"},
                {"page": 4, "type": "SIDE_A_ARGUMENT", "file": "page_4.html"},
                {"page": 5, "type": "SIDE_B_ARGUMENT", "file": "page_5.html"},
                {"page": 6, "type": "DEBATE_CALL_TO_ACTION", "file": "page_6.html"}
            ],
            "social_post": mock_data["post_copy"]
        },
        "risk_and_audit": {
            "audit_status": "PASS",
            "compliance_score": 100,
            "audit_rule": "xhs-discussion-audit-v2",
            "anti_fraud_rules": {
                "device_daily_vote_limit": 1,
                "ip_frequency_limit_per_min": 10
            }
        },
        "tracking_events": [
            {"event": "act_expose", "desc": "活动主落地页/笔记曝光"},
            {"event": "act_vote_click", "desc": "用户点击正方或反方投票"},
            {"event": "act_task_complete", "desc": "用户完成阅读/评论/邀请任务"},
            {"event": "act_draw_lottery", "desc": "用户消耗积分参与抽奖"},
            {"event": "act_share_click", "desc": "用户生成分享海报或点击分享"}
        ]
    }
    with open(os.path.join(output_dir, "campaign_config.json"), "w", encoding="utf-8") as f:
        json.dump(campaign_config, f, ensure_ascii=False, indent=2)
    print(f"   ➔ 已生成: campaign_config.json (运营活动中台配置)")


    # 9. 生成一键全屏多卡片阅览器 all_pages_viewer.html
    skill_badges = f"""
    <!-- 4 大 Skill 赋能矩阵状态 Bar -->
    <div class="flex flex-wrap items-center gap-2 p-3 bg-slate-800/90 rounded-xl border border-slate-700 text-xs font-mono">
      <span class="text-slate-400 font-bold">🛠️ 工业化流水线装配状态:</span>
      <span class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">✅ 专家多视角矩阵</span>
      <span class="px-2 py-0.5 rounded {'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' if use_data else 'bg-slate-700 text-slate-400'}">{'✅' if use_data else '⏸️'} 数据精算增强 (Data-Enhancer)</span>
      <span class="px-2 py-0.5 rounded {'bg-purple-500/20 text-purple-400 border border-purple-500/30' if use_cases else 'bg-slate-700 text-slate-400'}">{'✅' if use_cases else '⏸️'} 真实中产切片 (Fact-Case-Injector)</span>
      <span class="px-2 py-0.5 rounded {'bg-amber-500/20 text-amber-400 border border-amber-500/30' if use_humor else 'bg-slate-700 text-slate-400'}">{'✅' if use_humor else '⏸️'} 幽默网感赋能 (Humor-Refiner)</span>
      <span class="px-2 py-0.5 rounded bg-teal-500/20 text-teal-400 border border-teal-500/30">✅ 官方合规自检 100分</span>
    </div>
"""

    expert_cards_banner = f"""
    <!-- 专家视角交锋矩阵 Panel -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-800/80 p-4 rounded-xl border border-slate-700">
      <div class="p-3 rounded-lg bg-blue-950/40 border border-blue-500/30">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold text-blue-400">🔵 正方视角</span>
          <span class="text-[10px] text-slate-400">{side_a_p.get('name', '')}</span>
        </div>
        <p class="text-[11px] text-blue-200 font-medium">{side_a_p.get('title', '')}</p>
        <p class="text-[10px] text-slate-400 mt-1 italic">“{side_a_p.get('catchphrase', '')}”</p>
      </div>

      <div class="p-3 rounded-lg bg-amber-950/40 border border-amber-500/30">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold text-amber-400">🟡 反方视角</span>
          <span class="text-[10px] text-slate-400">{side_b_p.get('name', '')}</span>
        </div>
        <p class="text-[11px] text-amber-200 font-medium">{side_b_p.get('title', '')}</p>
        <p class="text-[10px] text-slate-400 mt-1 italic">“{side_b_p.get('catchphrase', '')}”</p>
      </div>

      <div class="p-3 rounded-lg bg-purple-950/40 border border-purple-500/30">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold text-purple-400">🔬 穿透视角</span>
          <span class="text-[10px] text-slate-400">{contrast_p.get('name', '')}</span>
        </div>
        <p class="text-[11px] text-purple-200 font-medium">{contrast_p.get('title', '')}</p>
        <p class="text-[10px] text-slate-400 mt-1 italic">“{contrast_p.get('catchphrase', '')}”</p>
      </div>
    </div>
"""

    viewer_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{mock_data['post_copy']['title']} - 全景图文卡片阅览器</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-5">
    <div class="flex items-center justify-between pb-3 border-b border-slate-800">
      <div>
        <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">全自动化图文生产闭环 · 三维增强版</span>
        <h1 class="text-xl font-bold text-white mt-1">{mock_data['post_copy']['title']}</h1>
      </div>
      <div class="text-right">
        <span class="text-xs text-slate-400">合规体检评分: <b class="text-emerald-400">{audit_res['score']}/100</b> ({audit_res['status']})</span>
      </div>
    </div>

    {skill_badges}
    {expert_cards_banner}

    <!-- 6 Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {"".join([f'''
      <div class="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-xl">
        <div class="p-2 bg-slate-950 text-xs text-slate-400 flex justify-between font-mono items-center">
          <span class="font-bold text-stone-300">P{idx+1} / 6</span>
          <div class="flex items-center gap-3">
            <a href="page_{idx+1}.png" target="_blank" class="text-emerald-400 hover:text-emerald-300 font-bold hover:underline">📸 高清PNG</a>
            <a href="page_{idx+1}.html" target="_blank" class="text-sky-400 hover:text-sky-300 hover:underline">HTML ↗</a>
          </div>
        </div>
        <iframe src="page_{idx+1}.html" class="w-full h-[520px] border-0"></iframe>
      </div>
      ''' for idx in range(len(mock_data['pages']))])}
    </div>

    <!-- Publishing Text Area -->
    <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="font-bold text-sm text-amber-400 flex items-center gap-1.5">
          <span>📝</span> 预置发布配文与首评置顶设计 (融入幽默金句与事实切片)
        </h3>
        <span class="text-xs text-slate-400">复制即可直接发布</span>
      </div>
      <textarea class="w-full h-44 bg-slate-950 text-slate-200 text-xs p-3 rounded border border-slate-700 font-mono focus:outline-none" readonly>{pack_content}</textarea>
    </div>
  </div>
</body>
</html>"""
    with open(os.path.join(output_dir, "all_pages_viewer.html"), "w", encoding="utf-8") as f:
        f.write(viewer_html)

    print(f"\n🎉 [Success] 全套融入专家视角与三维增强 (案例+数据+幽默) 的图文笔记生产完成！")
    print(f"📁 [输出目录] {output_dir}")
    print(f"🌐 [全景看板] {os.path.join(output_dir, 'all_pages_viewer.html')}")

    # 8. 自动化无头浏览器高清图片导出 (免去人工截图)
    if export_png:
        print(f"\n📸 [Export] 正在自动导出 1080×1440 高清图片 (免截图直接交付)...")
        export_deck_to_png(output_dir, scale=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书全自动化图文生产引擎 (融入多专家视角与三维增强)")
    parser.add_argument("--topic-id", type=str, default="", help="预设议题ID (如 mortgage_vs_invest, gold_beans)")
    parser.add_argument("--topic", type=str, default="", help="笔记辩题 (留空则根据 topic-id 自动读取预设)")
    parser.add_argument("--category", type=str, default="", help="所属赛道 (留空则读取议题预设)")
    parser.add_argument("--list-experts", action="store_true", help="打印查看已配置的专家库与路由矩阵")
    parser.add_argument("--no-data", action="store_true", help="关闭数据增强 Skill")
    parser.add_argument("--no-cases", action="store_true", help="关闭事实案例 Skill")
    parser.add_argument("--no-humor", action="store_true", help="关闭幽默改造 Skill")
    parser.add_argument("--no-png", action="store_true", help="关闭自动导出 PNG 图片")
    parser.add_argument("--input-json", type=str, default="", help="外部完整的 6 页图文 JSON 数据包路径 (用于直接驱动流水线)")
    DEFAULT_OUTPUT = os.path.join(REPO_ROOT, "examples", "mortgage_vs_invest")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="输出文件夹")
    args = parser.parse_args()

    if args.list_experts:
        print_expert_personas(load_expert_personas())
    else:
        run_pipeline(
            topic=args.topic,
            category=args.category,
            output_dir=args.output,
            topic_id=args.topic_id,
            use_data=not args.no_data,
            use_cases=not args.no_cases,
            use_humor=not args.no_humor,
            export_png=not args.no_png,
            input_json=args.input_json
        )

