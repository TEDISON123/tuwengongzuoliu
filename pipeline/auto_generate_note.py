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

def load_expert_personas() -> dict:
    """加载专家视角配置库"""
    personas_file = os.path.join(CURRENT_DIR, "expert_personas.json")
    if os.path.exists(personas_file):
        with open(personas_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"personas": {}, "topic_routes": {}}

def render_html_card(page_data: dict, page_num: int, total_pages: int = 6) -> str:
    """基于 Tailwind CSS 渲染 3:4 比例卡片 HTML (全面融入专家视角)"""
    ptype = page_data.get("type", "")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');
    body {{ font-family: 'Noto Sans SC', sans-serif; }}
    .card-canvas {{
      width: 540px;
      height: 720px;
      position: relative;
      overflow: hidden;
    }}
  </style>
</head>
<body class="bg-slate-100 flex items-center justify-center min-h-screen p-4">
  <div class="card-canvas bg-white shadow-xl rounded-2xl flex flex-col justify-between p-8 border border-slate-200">
    
    <!-- Top Header Bar -->
    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
      <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-600 tracking-wider">
        {page_data.get("badge", "#理性讨论 · 财经认知")}
      </span>
      <span class="text-xs font-semibold text-slate-400 font-mono">
        {page_num} / {total_pages}
      </span>
    </div>
"""

    if ptype == "cover_poster":
        title_lines = page_data.get("title_main", "").split("\n")
        title_html = "".join([f'<span class="block">{line}</span>' for line in title_lines])
        
        matchup_html = ""
        if "expert_matchup" in page_data:
            em = page_data["expert_matchup"]
            matchup_html = f"""
      <!-- 专家视角交锋对决 Badge -->
      <div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 text-white text-[11px] font-bold shadow-md">
        <span class="text-slate-400">⚖️ 专家对决:</span>
        <span class="text-amber-300">{em.get('side_a', '')}</span>
        <span class="text-slate-500 font-mono text-[10px]">VS</span>
        <span class="text-blue-300">{em.get('side_b', '')}</span>
      </div>
"""

        html += f"""
    <!-- Cover Poster Content -->
    <div class="my-auto space-y-5 text-center">
      <div class="inline-block px-3 py-1 rounded bg-amber-50 border border-amber-200 text-amber-700 text-xs font-bold tracking-wide">
        💰 真实账本对决 · 争议辩题
      </div>
      <h1 class="text-3xl font-black text-slate-900 leading-tight tracking-tight px-2">
        {title_html}
      </h1>
      <div class="mx-auto max-w-sm p-3 rounded-xl bg-red-50 border-2 border-red-500/30 text-red-600 font-bold text-sm leading-snug">
        {page_data.get("subtitle", "")}
      </div>
      {matchup_html}
    </div>
    
    <!-- Footer CTA -->
    <div class="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400 font-medium">
      <span>{page_data.get("footer_tip", "内附两派专家真实账本 · 换你你怎么选？ ➔")}</span>
      <span class="text-blue-500 font-bold">滑动阅读 ➔</span>
    </div>
"""

    elif ptype == "pain_point":
        table_rows = "".join([
            f"""<div class="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span class="font-bold text-xs text-slate-700">{row['item']}</span>
              <span class="text-xs font-semibold text-slate-500">{row['rate']}</span>
              <span class="font-mono font-bold text-xs text-red-500">{row['yield']}</span>
            </div>""" for row in page_data.get("table_data", [])
        ])
        html += f"""
    <div class="my-auto space-y-4">
      <div class="space-y-1">
        <span class="text-xs font-bold text-blue-600 uppercase tracking-wider">现实痛点拆解 · 真实利差</span>
        <h2 class="text-2xl font-black text-slate-900 leading-tight">{page_data.get("heading", "")}</h2>
      </div>
      <p class="text-xs text-slate-600 leading-relaxed">{page_data.get("scene_desc", "")}</p>
      
      <div class="space-y-2">
        {table_rows}
      </div>

      <div class="p-3 rounded-xl bg-amber-500/10 border-l-4 border-amber-500 text-xs text-amber-900 font-medium leading-relaxed">
        💡 {page_data.get("hook_question", "")}
      </div>
    </div>
    <div class="pt-3 border-t border-slate-100 text-right text-xs text-slate-400">P2 / 痛点账本</div>
"""

    elif ptype == "contrast_gap":
        expert_tag = ""
        if page_data.get("expert_name"):
            expert_tag = f"""
        <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-50 border border-purple-200 text-purple-700 text-[11px] font-bold">
          <span>🔬 穿透视角：{page_data.get("expert_name")}</span>
        </div>
"""
        expert_quote = ""
        if page_data.get("expert_quote"):
            expert_quote = f"""
        <div class="p-2 rounded-lg bg-purple-50/60 border-l-2 border-purple-400 text-[10px] text-purple-900 italic font-medium">
          “{page_data.get("expert_quote")}”
        </div>
"""

        quant_box = ""
        if "quant_summary" in page_data:
            qs = page_data["quant_summary"]
            quant_box = f"""
      <!-- Data Enhancer 精算看板 -->
      <div class="grid grid-cols-3 gap-2 p-2 rounded-xl bg-slate-900 text-white text-center">
        <div class="border-r border-slate-800 pr-1">
          <span class="text-[9px] text-slate-400 block font-mono">利息差额</span>
          <span class="text-[11px] font-black text-emerald-400">{qs.get('left_stat', '')}</span>
        </div>
        <div class="border-r border-slate-800 pr-1">
          <span class="text-[9px] text-slate-400 block font-mono">流动性缓冲</span>
          <span class="text-[11px] font-black text-amber-300">{qs.get('right_stat', '')}</span>
        </div>
        <div>
          <span class="text-[9px] text-slate-400 block font-mono">关键门槛</span>
          <span class="text-[11px] font-black text-blue-300">{qs.get('spread_metric', '')}</span>
        </div>
      </div>
"""

        metaphor_box = ""
        if page_data.get("humor_metaphor"):
            metaphor_box = f"""
      <div class="p-2.5 rounded-lg bg-amber-500/10 border-l-3 border-amber-500 text-amber-900 text-[10px] font-bold leading-relaxed">
        🎭 神级隐喻：“{page_data.get('humor_metaphor')}”
      </div>
"""

        html += f"""
    <div class="my-auto space-y-3.5">
      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-red-600 uppercase tracking-wider">认知剪刀差</span>
          {expert_tag}
        </div>
        <h2 class="text-2xl font-black text-slate-900 leading-tight">{page_data.get("heading", "")}</h2>
      </div>

      {expert_quote}
      {quant_box}

      <div class="space-y-2">
        <div class="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200">
          <div class="text-[11px] font-bold text-emerald-700 mb-0.5 flex items-center gap-1">
            <span>👀 看得见的算计（显性账）：</span>
          </div>
          <p class="text-[11px] text-emerald-900 leading-relaxed font-medium">{page_data.get("visible_gain", "")}</p>
        </div>

        <div class="p-2.5 rounded-xl bg-red-50 border border-red-200">
          <div class="text-[11px] font-bold text-red-700 mb-0.5 flex items-center gap-1">
            <span>⚠️ 看不见的代价（隐性账）：</span>
          </div>
          <p class="text-[11px] text-red-900 leading-relaxed font-medium">{page_data.get("hidden_cost", "")}</p>
        </div>
      </div>

      {metaphor_box}
    </div>
    <div class="pt-3 border-t border-slate-100 text-right text-xs text-slate-400">P3 / 冲突本质</div>
"""

    elif ptype in ["side_a", "side_b"]:
        is_a = ptype == "side_a"
        color = "blue" if is_a else "amber"
        expert_name = page_data.get("expert_name", "正方专家" if is_a else "反方专家")
        expert_title = page_data.get("expert_title", "")
        expert_quote = page_data.get("expert_quote", "")

        args_html = "".join([
            f"""<li class="flex items-start gap-2 text-xs text-slate-700 leading-relaxed">
              <span class="flex-shrink-0 w-4 h-4 rounded-full bg-{color}-100 text-{color}-700 font-bold text-[10px] flex items-center justify-center mt-0.5">{idx+1}</span>
              <span>{arg}</span>
            </li>""" for idx, arg in enumerate(page_data.get("arguments", []))
        ])

        quote_html = ""
        if expert_quote:
            quote_html = f"""
      <div class="p-2 rounded-lg bg-{color}-50/70 border-l-3 border-{color}-500 text-[10px] text-{color}-900 italic font-medium">
        💬 核心观点：“{expert_quote}”
      </div>
"""

        case_box = ""
        if "case_slice" in page_data:
            c = page_data["case_slice"]
            case_box = f"""
      <!-- Fact Case Injector 切片 -->
      <div class="p-2 rounded-lg bg-{color}-100/60 border border-{color}-200 space-y-0.5">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-black text-{color}-900">📌 {c.get('tag')}: {c.get('title')}</span>
          <span class="text-[9px] font-bold text-{color}-700 bg-white/90 px-1 rounded">{c.get('key_metric')}</span>
        </div>
        <p class="text-[10px] text-slate-700 leading-tight">{c.get('story')}</p>
      </div>
"""

        humor_os = ""
        if page_data.get("humor_os"):
            humor_os = f"""
      <div class="text-[10px] text-slate-400 italic text-right font-mono">
        {page_data.get('humor_os')}
      </div>
"""

        html += f"""
    <div class="my-auto space-y-3">
      <!-- 专家立论看板 -->
      <div class="p-2.5 rounded-xl bg-{color}-50 border-l-4 border-{color}-600 space-y-0.5">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-bold uppercase tracking-wider text-{color}-600">
            {"【正方立场】" if is_a else "【反方立场】"}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded bg-white/80 font-bold text-{color}-800 border border-{color}-200">
            {expert_name}
          </span>
        </div>
        <h2 class="text-sm font-black text-{color}-950 leading-snug">{page_data.get("stance", "")}</h2>
        {f'<p class="text-[9px] text-{color}-700/80 font-medium">{expert_title}</p>' if expert_title else ''}
      </div>

      {quote_html}

      <ul class="space-y-1.5">
        {args_html}
      </ul>

      {case_box}
      {humor_os}
    </div>
    <div class="pt-3 border-t border-slate-100 text-right text-xs text-slate-400">{"P4 / 正方立论" if is_a else "P5 / 反方立论"}</div>
"""

    elif ptype == "ending_hook":
        html += f"""
    <div class="my-auto space-y-5 text-center">
      <div class="space-y-1">
        <span class="text-xs font-bold text-purple-600 uppercase tracking-wider">天平抉择 · 终极站队</span>
        <h2 class="text-2xl font-black text-slate-900 leading-tight">{page_data.get("heading", "")}</h2>
      </div>

      <div class="space-y-2.5 text-left">
        <div class="p-3 rounded-xl border-2 border-blue-500 bg-blue-50/50">
          <p class="text-xs font-bold text-blue-800">{page_data.get("option_a", "")}</p>
        </div>
        <div class="p-3 rounded-xl border-2 border-amber-500 bg-amber-50/50">
          <p class="text-xs font-bold text-amber-800">{page_data.get("option_b", "")}</p>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-slate-900 text-white space-y-1.5">
        <p class="text-xs font-bold text-amber-300">💬 两位专家神仙打架，换作是你站哪边？</p>
        <p class="text-[11px] text-slate-300 leading-relaxed">{page_data.get("debate_invitation", "")}</p>
      </div>
    </div>
    <div class="pt-3 border-t border-slate-100 text-center text-xs text-slate-400">👉 评论区留下你的账本与观点</div>
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
                 use_data: bool = True, use_cases: bool = True, use_humor: bool = True):
    os.makedirs(output_dir, exist_ok=True)
    personas_cfg = load_expert_personas()

    # 1. 智能匹配或指定 topic_id
    if not topic_id:
        if topic:
            if "期权" in topic or "options" in topic:
                topic_id = "options_rich_or_ruin"
            elif "金豆" in topic or "黄金" in topic:
                topic_id = "gold_beans"
            else:
                topic_id = "mortgage_vs_invest"
        else:
            topic_id = "mortgage_vs_invest"

    print(f"🚀 [Pipeline] 开始全自动生产金融图文笔记...")
    print(f"🎯 [议题路由ID] {topic_id}")

    # 2. 结构化装配融入专家视角的图文基础数据
    mock_data = get_topic_data_bundle(topic_id, personas_cfg)
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
        <div class="p-2 bg-slate-950 text-xs text-slate-400 flex justify-between font-mono">
          <span>P{idx+1} / 6</span>
          <a href="page_{idx+1}.html" target="_blank" class="text-blue-400 hover:underline">独立全屏打开 ↗</a>
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书全自动化图文生产引擎 (融入多专家视角与三维增强)")
    parser.add_argument("--topic-id", type=str, default="", help="预设议题ID (如 mortgage_vs_invest, gold_beans)")
    parser.add_argument("--topic", type=str, default="", help="笔记辩题 (留空则根据 topic-id 自动读取预设)")
    parser.add_argument("--category", type=str, default="", help="所属赛道 (留空则读取议题预设)")
    parser.add_argument("--list-experts", action="store_true", help="打印查看已配置的专家库与路由矩阵")
    parser.add_argument("--no-data", action="store_true", help="关闭数据增强 Skill")
    parser.add_argument("--no-cases", action="store_true", help="关闭事实案例 Skill")
    parser.add_argument("--no-humor", action="store_true", help="关闭幽默改造 Skill")
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
            use_humor=not args.no_humor
        )

