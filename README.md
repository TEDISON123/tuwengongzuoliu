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

---

## 📂 项目目录结构 (Directory Structure)

```text
tuwengongzuoliu/
├── docs/                                          # 核心规范与体系规划文档
│   ├── campaign_workflow_sop.md                   # 小红书社群活动规则与创作者SOP
│   ├── finance_knowledge_graph_planning.md        # 金融知识图谱与50+话题矩阵规划
│   ├── finance_note_production_workflow.md        # 金融图文工业化生产全流程工作流
│   └── automated_image_text_workflow_architecture.md # 全自动化技术架构与数据流规范
├── skills/
│   └── xhs-discussion-audit/                      # 官方合规自检与改写 Skill 引擎
│       ├── SKILL.md                               # 技能标准规范与判定树
│       ├── rules.json                             # 规则、死穴特征词与垂类配置
│       └── scripts/
│           └── audit_note.py                      # 自动化体检与诊断打分 Python 脚本
├── pipeline/
│   └── auto_generate_note.py                      # 核心自动化调度脚本 (端到端流水线)
├── templates/                                     # 交互式组件与模板
│   ├── incentive_calculator.html                  # 活动收益测算与冲档助手 (Generative UI)
│   ├── finance_graph_explorer.html                # 交互式知识图谱话题罗盘
│   └── pipeline_controller.html                   # 全自动化流水线交互控制器
├── examples/
│   └── mortgage_vs_invest/                        # 实测交付物示例 (提前还贷vs理财)
│       ├── page_1.html ~ page_6.html              # 标准 3:4 独立图文卡片 (HTML+Tailwind)
│       ├── all_pages_viewer.html                  # 6 卡片全景预览看板
│       ├── audit_report.json                      # 自动化体检达标报告 (100分 PASS)
│       └── publish_pack.txt                       # 复制即发文案包 (含置顶神评)
└── README.md
```

---

## 🚀 快速启动指南 (Quick Start)

### 1. 运行单篇全自动图文生成

在终端中执行以下命令，即可针对特定议题一键完成脚本生成、质量体检、3:4卡片渲染与文案打包：

```bash
python3 pipeline/auto_generate_note.py \
  --topic "手头有50万闲钱：提前还4.0%房贷，还是留着买理财？" \
  --category "财经/理财" \
  --output "examples/mortgage_vs_invest"
```

### 2. 独立运行内容合规体检工具

你可以直接使用审核引擎检验任意标题或笔记草稿是否符合官方投流标准：

```bash
python3 skills/xhs-discussion-audit/scripts/audit_note.py \
  --title "博士求职日记：今天去面试了大厂，建了个交流群" \
  --category "职场"
```

输出示例：
```markdown
# 📋 小红书「理性讨论」活动合规审核报告
- 审核结论：REJECTED (非活动投流范式 ❌)
- 议题指数评分：10 / 100 分
- 违规项：命中死穴【个人流水账】，读者无法展开立场对辩，不予投流。
- 改写建议：改为《博士求职时，学校背景和顶级顶刊经历，哪个更关键？》
```

### 3. 查看全景卡片看板与发布物料

生成完毕后，双击打开 `examples/mortgage_vs_invest/all_pages_viewer.html`：
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
