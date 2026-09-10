# tuwengongzuoliu (图文工作流) 🚀

> **小红书图文内容工业化与全自动化生产工作流系统**  
> 对标小红书官方「理性讨论」活动创作指导标准（单篇 10万～20万 官方投流扶持），实现**“从种子议题到 6 页高清 3:4 图文卡片、合规自检、文案打包”**的端到端无人值守生产闭环。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.0+-38bdf8.svg)](https://tailwindcss.com)
[![Platform](https://img.shields.io/badge/Platform-Xiaohongshu%20%7C%20小红书-ff2442.svg)](https://xiaohongshu.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 核心特性 (Features)

1. **全自动化流水线 (Full-Automation Pipeline)**：输入任意财经或垂类种子关键词，一键全自动生成 6 页 3:4 比例高清大字报与对比账本卡片。
2. **专属质检 Skill (`xhs-discussion-audit`)**：内置对标小红书官方新版创作指导规则的合规审核引擎，逐项排查 6 大卡点，自动拦截“个人流水账、教程攻略、励志鸡汤、消费态度”四大投流死穴。
3. **三维金融知识图谱 (Knowledge Graph)**：覆盖个人财务、资产配置、宏观周期、商业公司、金融史话、时代辩题 6 大母模块及 18 个核心二级领域的爆款对立议题库。
4. **标准 6 页图文结构法 (6-Page Slide Deck Architecture)**：
   * **P1 封面**：大字报对撞标题，黄金 1 秒直击痛点。
   * **P2 痛点**：显性账本对比，具体数字呈现冲突。
   * **P3 反差**：认知剪刀差，揭秘常识盲区与隐性代价。
   * **P4 正方**：立场 A 的 3 条不可反驳的硬核立论。
   * **P5 反方**：立场 B 的 3 条反周期、抗风险立论。
   * **P6 站队**：A/B 投票箱，直击灵魂二选一促评 Hook。
5. **官方履约风控集成**：自动打包小红书发布文案、官方指定活动标签、作者前 5 分钟置顶神评及腾讯文档收集表直达链接。
6. **多专家视角交锋矩阵 (Expert Personas Matrix)**：针对不同金融议题，自动路由并注入 6 大硬核专家角色（注册理财规划师/精算视角、宏观经济周期学者、硬核价值投资人、商业战略CFO、平民反收割官、法律风控律师），在封面 P1 展示交锋 Badge、P3 深度穿透认知剪刀差、P4/P5 注入专家专属立论与标志金句，彻底告别单一口吻与假大空教程。
7. **三维内容增强 Skill 矩阵 (3-Dimensional Content Boosters)**：
   * **事实案例 Skill (`fact-case-injector`)**：自动嵌入典型中产财务切片、避坑事实警示与商业历史对照样本，让抽象理论落地为“具体的真人账本”；
   * **数据精算 Skill (`data-enhancer`)**：内置房贷提前还款省利息精算、存贷利差计算器、黄金买入工艺溢价与变现折价率公式，提供硬核数据背书；
   * **幽默网感 Skill (`humor-refiner`)**：融入神级通俗隐喻、当代打工人扎心自嘲与反讽括号内心戏 OS，在严守小红书合规底线的前提下极大提升趣味度与完读率。

---

## 📂 项目目录结构 (Directory Structure)

```text
tuwengongzuoliu/
├── docs/                                          # 核心规范与体系规划文档
│   ├── expert_perspectives_framework.md           # 六大金融专家视角体系设计与路由框架
│   ├── campaign_workflow_sop.md                   # 小红书社群活动规则与创作者SOP
│   ├── finance_knowledge_graph_planning.md        # 金融知识图谱与50+话题矩阵规划
│   ├── finance_note_production_workflow.md        # 金融图文工业化生产全流程工作流
│   └── automated_image_text_workflow_architecture.md # 全自动化技术架构与数据流规范
├── skills/                                        # 四大标准化工业级 Skill 引擎
│   ├── xhs-discussion-audit/                      # 1. 官方合规自检与改写 Skill (拦截四大死穴)
│   │   ├── SKILL.md
│   │   ├── rules.json
│   │   └── scripts/audit_note.py
│   ├── fact-case-injector/                        # 2. 事实案例与中产切片 Skill (增强代入感)
│   │   ├── SKILL.md
│   │   ├── database/case_library.json
│   │   └── scripts/inject_cases.py
│   ├── data-enhancer/                             # 3. 数据精算与量化利差 Skill (增强权威信任)
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── finance_math.py                    # 房贷利差、黄金溢价等数学引擎
│   │       └── enhance_data.py
│   └── humor-refiner/                             # 4. 幽默改造与网感赋能 Skill (提升完读率)
│       ├── SKILL.md
│       └── scripts/refine_humor.py                # 神级比喻、打工人自嘲与括号OS
├── pipeline/
│   ├── auto_generate_note.py                      # 核心全自动装配主流水线 (串联四大 Skill)
│   └── expert_personas.json                       # 专家视角角色库与议题路由配置表
├── templates/                                     # 交互式组件与模板
│   ├── incentive_calculator.html                  # 活动收益测算与冲档助手 (Generative UI)
│   ├── finance_graph_explorer.html                # 交互式知识图谱话题罗盘
│   └── pipeline_controller.html                   # 全自动化流水线交互控制器
├── examples/
│   ├── mortgage_vs_invest/                        # 示例1：提前还贷 vs 买理财 (三维增强版)
│   │   ├── page_1.html ~ page_6.html              # 融入案例、精算看板、幽默金句的卡片
│   │   ├── all_pages_viewer.html                  # 包含四大 Skill 装配状态的全景看板
│   │   ├── audit_report.json                      # 自动化体检达标报告 (100分 PASS)
│   │   └── publish_pack.txt                       # 完整发布文案包 (含神级比喻与置顶神评)
│   └── gold_beans/                                # 示例2：年轻人攒金豆争议 (三维增强版)
│       ├── page_1.html ~ page_6.html
│       ├── all_pages_viewer.html
│       ├── audit_report.json
│       └── publish_pack.txt
└── README.md
```

---

## 🚀 快速启动指南 (Quick Start)

### 1. 运行全自动图文生产 (默认全开四大 Skill 赋能)

在终端中执行以下命令，即可针对特定议题一键完成**专家路由 + 数据精算 + 案例注入 + 幽默改造 + 合规自检 + 3:4 卡片渲染 + 物料打包**：

```bash
# 运行提前还贷 vs 理财议题 (平民反收割官 VS 注册理财规划师 | 宏观学者穿透)
python3 pipeline/auto_generate_note.py --topic-id mortgage_vs_invest --output examples/mortgage_vs_invest

# 运行攒金豆议题 (宏观经济学者 VS 平民反收割官 | 价值投资人穿透)
python3 pipeline/auto_generate_note.py --topic-id gold_beans --output examples/gold_beans
```

### 2. 独立调用四大 Skill

```bash
# ① 运行小红书「理性讨论」合规体检 Skill
python3 skills/xhs-discussion-audit/scripts/audit_note.py --title "手头有50万闲钱，提前还贷还是买理财？"

# ② 运行事实案例库检索 Skill
python3 skills/fact-case-injector/scripts/inject_cases.py --topic-id mortgage_vs_invest

# ③ 运行金融精算模型 Skill (如测算50万4%房贷30年省息账本)
python3 skills/data-enhancer/scripts/finance_math.py --calc mortgage --amount 500000 --rate 0.040

# ④ 运行幽默比喻与扎心金句库 Skill
python3 skills/humor-refiner/scripts/refine_humor.py --list-quotes
```

### 3. 查看全景卡片看板与发布物料

生成完毕后，双击打开 `examples/mortgage_vs_invest/all_pages_viewer.html`：
* 查看顶部 **四大 Skill 装配流水线状态** 与 **专家交锋矩阵**；
* 同步并排预览 P1 至 P6 高清大字报卡片；
* 底部一键复制标题、正文、Hashtag 与作者置顶神评。

---

## 🎁 小红书官方活动阶梯奖励对照

| 奖励名称 | 考核门槛（双指标同时满足） | 官方奖励额度 | 策略定位 |
| :--- | :--- | :--- | :--- |
| **基础单篇扶持** | 单篇笔记符合新版内容范式 | **10万 ～ 20万 曝光扶持** | 保底流量池 |
| **新人首发奖** | 历史从未提过有效稿 + 本周发 1 篇 | **1 张** 1000 流量券 | 破冰保底 |
| **创作参与奖** | 当周 2～4 篇 且 有效评论 ≥ 20 条 | **1 张** 1000 流量券 | 轻量创作者 |
| **持续创作奖** | 当周 5～9 篇 且 有效评论 ≥ 50 条 | **2 张** 1000 流量券 | 主力日更档 |
| **优质共创奖** | 当周 ≥ 10 篇 且 有效评论 ≥ 150 条 | **3 张** 1000 流量券 | 头部冲榜档 |
| **高热讨论奖** | **单篇**有效评论 ≥ 500 条 | **5 张** 1000 流量券 | 爆款冲刺大奖 |
| **每周双榜 TOP3** | 活跃创作榜 / 讨论热度榜前 3 名 | **活动专属限定 T 恤** | 荣誉周边 |

> ⚠️ **关键履约生命线**：发布后必须第一时间前往 [官方腾讯文档收集表](https://doc.weixin.qq.com/forms/ANAAyQcbAAgAbEAGAb_AKoCNPRTWz2o5f) 提交笔记链接！**不填表 ＝ 未参与活动**。

---

## 📄 开源协议 (License)

本项目采用 [MIT License](LICENSE) 协议开源。
