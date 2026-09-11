# tuwengongzuoliu 项目运行 SOP

> **文档类型**：Standard Operating Procedure
> **生成时间**：2026-09-09
> **版本**：v1.0
> **适用对象**：项目使用者、新加入协作者

---

## 目录

1. [运行总览](#一-运行总览)
2. [环境准备](#二-环境准备一次性)
3. [3 种 CLI 入口](#三-3-种-cli-入口按场景选择)
4. [典型工作流 SOP](#四-典型工作流-sop)
5. [运行故障排查](#五-运行故障排查)
6. [文件输出位置速查](#六-文件输出位置速查)
7. [一句话最小启动](#七-一句话最小启动)

---

## 一、运行总览

```mermaid
graph LR
    A[环境检查] --> B[跑通测试案例]
    B --> C[自定义新议题]
    C --> D[独立体检]
    D --> E[浏览器预览交付物]
    E --> F[可选:打开交互式工具]
```

项目提供 **3 种 CLI 入口** + **3 个浏览器交互工具**，互相独立，按需调用。

---

## 二、环境准备（一次性）

### 2.1 检查 Python 版本

**Windows PowerShell**：

```powershell
python --version
# 或
python3 --version
```

期望输出：`Python 3.9.x` 或更高。如未安装：<https://www.python.org/downloads/>

### 2.2 进入项目根目录

```powershell
cd D:\cadabra_tools003\AgentPro\tuwengongzuoliu
```

### 2.3 验证目录结构

```powershell
Get-ChildItem -Name
```

期望看到：`docs/`、`pipeline/`、`skills/`、`templates/`、`examples/`、`README.md`、`prds/`。

> **重要**：项目**无第三方依赖**，不需要 `pip install`，全部使用 Python 标准库。

---

## 三、3 种 CLI 入口（按场景选择）

### 入口 A：端到端图文生产流水线（最常用）

**适用**：从零生成一套完整的 6 页图文卡片 + 审核 + 文案包。

#### A.1 跑通内置示例（首次必跑）

```powershell
python pipeline/auto_generate_note.py `
  --topic "手头有50万闲钱：提前还4.0%房贷，还是留着买理财？" `
  --category "财经/理财" `
  --output "examples/mortgage_vs_invest"
```

#### A.2 自定义新议题

```powershell
python pipeline/auto_generate_note.py `
  --topic "你新发的辩题文本" `
  --category "你选择的赛道" `
  --output "examples/你自定义的输出目录名"
```

**参数说明**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--topic` | 提前还贷示例辩题 | 笔记辩题文本（会作为标题参考） |
| `--category` | `财经/理财` | 赛道标签，影响审核时的垂类判定 |
| `--output` | `examples/mortgage_vs_invest` | 输出目录，自动创建 |

#### A.3 执行成功标志

控制台应输出：

```
🚀 [Pipeline] 开始全自动生产金融图文笔记...
🔍 [Audit] 正在调用 xhs-discussion-audit 进行 6 项卡点质检...
📊 [Audit 结果] 评分: 100 分 | 状态: PASS (推荐投流 ✅)
🎨 [Render] 正在渲染 6 张标准 3:4 图文卡片 (HTML+Tailwind)...
   ➔ 已生成: page_1.html
   ... (page_2 ~ page_6)
🎉 [Success] 全套图文笔记生产完成！
```

#### A.4 产出物清单

指定输出目录下应有 9 个文件：

| 文件 | 用途 |
|------|------|
| `page_1.html` ~ `page_6.html` | 6 张独立 3:4 卡片（封面/痛点/认知差/正方/反方/站队） |
| `all_pages_viewer.html` | 全景看板（6 卡片并排预览） |
| `audit_report.json` | 审核结果 JSON |
| `publish_pack.txt` | 一键复制发布物料包 |

---

### 入口 B：独立合规审核工具

**适用**：手里已有标题/草稿，先做合规自检再决定是否投入制作。

```powershell
python skills/xhs-discussion-audit/scripts/audit_note.py `
  --title "你的标题文本" `
  --content "可选：笔记正文或大纲" `
  --category "职场"
```

**参数说明**：

| 参数 | 是否必填 | 说明 |
|------|---------|------|
| `--title` | 必填 | 待审核的标题 |
| `--content` | 选填 | 笔记正文/大纲（提升审核准确性） |
| `--category` | 选填 | 垂类，默认 `通用` |

**输出**：Markdown 格式的体检报告，含 6 卡点状态、扣分诊断、改写建议。

---

### 入口 C：浏览器交互工具（零代码）

`templates/` 目录下 3 个 HTML 文件，**双击即用**：

| 工具 | 文件 | 用途 |
|------|------|------|
| 流水线控制器 | `templates/pipeline_controller.html` | 可视化选择议题、查看流水线状态 |
| 活动收益测算 | `templates/incentive_calculator.html` | 输入篇数/评论数，测算活动冲档奖励 |
| 金融知识图谱 | `templates/finance_graph_explorer.html` | 浏览 6 大母模块 × 18 子领域选题库 |

---

## 四、典型工作流 SOP

### 场景 1：创作者日常发布一篇新笔记

```
步骤1. 选题
  ↓ 浏览 templates/finance_graph_explorer.html 选议题
步骤2. 合规预审
  ↓ 用入口 B 跑标题/草稿
  ↓ 通过 (PASS) → 进入步骤3
  ↓ 需优化 (NEEDS_OPTIMIZATION) → 按改写建议调整后回到步骤2
步骤3. 一键生产
  ↓ 用入口 A 生成完整物料包
步骤4. 浏览器预览
  ↓ 双击 all_pages_viewer.html 查看全景
步骤5. 复制发布
  ↓ 从 publish_pack.txt 复制标题/正文/Hashtag/置顶神评到小红书
步骤6. 提交收集表（必做）
  ↓ 访问 https://doc.weixin.qq.com/forms/ANAAyQcbAAgAbEAGAb_AKoCNPRTWz2o5f
```

### 场景 2：批量冲档（如周更 5 篇冲"持续创作奖"）

```
步骤1. 一次性规划 5 个议题（参考知识图谱）
步骤2. 循环跑入口 A 5 次（每次 output 不同）
步骤3. 浏览 templates/incentive_calculator.html 估算奖励
步骤4. 按场次发布并填表
```

### 场景 3：团队复盘/演示

```
步骤1. 浏览器打开 templates/pipeline_controller.html
步骤2. 展示已有 examples/mortgage_vs_invest/all_pages_viewer.html
步骤3. 用入口 B 演示审核能力
```

---

## 五、运行故障排查

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| `python: command not found` | Python 未安装或未加入 PATH | 安装 Python 3.9+ 并勾选「Add to PATH」 |
| `ModuleNotFoundError: No module named 'audit_note'` | 脚本路径问题 | 必须在项目根目录执行，或确保 `skills/xhs-discussion-audit/scripts/` 在 `sys.path` 中（脚本已自动处理） |
| 卡片排版错乱（文字拥挤/无样式） | Tailwind CDN 加载失败 | 检查网络（需要访问 `gstatic.com` 和 `fonts.googleapis.com`） |
| 中文显示为方框 | 系统缺少中文字体 | Windows 自带微软雅黑/SimSun 通常无问题；macOS 安装「Noto Sans SC」；Linux 安装 `fonts-noto-cjk` |
| `all_pages_viewer.html` iframe 显示空白 | 浏览器跨文件 iframe 限制 | 直接打开 `page_1.html` ~ `page_6.html` 单独查看 |
| 审核评分异常低 | 标题/正文命中四大死穴特征词 | 参考 `audit_report.json` 的 `penalties` 字段，按 `rewrite_suggestions` 改写 |

---

## 六、文件输出位置速查

| 你要做什么 | 跑哪个命令 | 输出在哪 |
|-----------|-----------|---------|
| 生成一套 6 页卡片 | `python pipeline/auto_generate_note.py ...` | `--output` 指定的目录 |
| 单独审核一个标题 | `python skills/xhs-discussion-audit/scripts/audit_note.py ...` | 控制台 Markdown 输出 |
| 浏览全景看板 | 双击 `all_pages_viewer.html` | 浏览器 |
| 看流水线交互控制器 | 双击 `templates/pipeline_controller.html` | 浏览器 |
| 测算活动奖励 | 双击 `templates/incentive_calculator.html` | 浏览器 |
| 浏览选题库 | 双击 `templates/finance_graph_explorer.html` | 浏览器 |

---

## 七、一句话最小启动

```powershell
cd D:\cadabra_tools003\AgentPro\tuwengongzuoliu && python pipeline/auto_generate_note.py
```

（不带任何参数会跑内置默认示例，输出到 `examples/mortgage_vs_invest/`。）

---

## 八、零命令行一键预览（推荐日常使用）

> **适用**：只想看前端效果，不想每次敲 PowerShell 命令。

项目根目录提供 4 个**双击即用**脚本：

| 脚本 | 作用 |
|------|------|
| `start_viewer.bat` | 开本地 HTTP 服务器（端口 8765）+ 弹出菜单让你选页面 + 自动打开浏览器 |
| `stop_server.bat` | 一键关闭服务器（按端口 8765 找进程并停止） |
| `start_viewer.ps1` | 同 bat，PowerShell 原生版本（适合进阶用户） |
| `stop_server.ps1` | 同上 |

### 用法

1. 在文件资源管理器里双击 `start_viewer.bat`
2. 弹出菜单输入 `1`（默认就是 1，直接回车）
3. 浏览器自动打开 `http://localhost:8765/examples/mortgage_vs_invest/all_pages_viewer.html`
4. 看完了双击 `stop_server.bat` 关闭服务器

### 特性

- 零依赖（只用 Python 自带的 `http.server`）
- 中文不乱码（`.bat` 里加了 `chcp 65001`）
- 端口占用自动检测（已被占用时会跳过启动直接用）
- 菜单支持 6 卡片单页 / 全景看板 / 3 个交互工具 共 10 种入口

### 为什么不用直接 `file://` 双击 HTML

HTML 里引用了 `fonts.googleapis.com` 和 `gstatic.com` 的 CDN，部分浏览器对 `file://` 协议下跨域资源限制更严。用本地 HTTP 协议（`http://localhost`）能 100% 复现真实部署环境。

---

## 文档版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0 | 2026-09-09 | 首次发布运行 SOP 文档 |
| v1.1 | 2026-09-09 | 新增第八章「零命令行一键预览」,补 start_viewer.bat / stop_server.bat 双击脚本 |

**SOP 结束**
