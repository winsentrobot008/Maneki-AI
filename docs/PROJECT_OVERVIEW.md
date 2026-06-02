# 🐱 Maneki-AI：AI 工厂操作系统（AI Factory OS）

> **版本**: v0.3.0-factory · **架构**: Async AI Factory · **自治度**: 35% Built

Maneki-AI 是一个面向开发者与团队的 **AI 工厂操作系统**，通过"多层智能 + 多 Worker 执行 + 可视化调度"的方式，将 AI 的能力从单点工具升级为可控的自动化工厂。

---

## 📋 目录

1. [核心愿景](#1-核心愿景)
2. [极简作业指南](#2-极简作业指南)
3. [系统架构](#3-系统架构)
4. [角色职能](#4-角色职能)
5. [标准作业流程](#5-标准作业流程)
6. [核心引擎组件](#6-核心引擎组件)
7. [工厂集成架构](#7-工厂集成架构)
8. [AI 编排策略](#8-ai-编排策略)
9. [扩展模块](#9-扩展模块)
10. [项目结构](#10-项目结构)
11. [快速开始](#11-快速开始)
12. [开发路线图](#12-开发路线图)

---

## 1. 核心愿景

### 1.1 使命

Maneki-AI 的目标**不是一个 AI 工具**，而是一个**可控、可扩展、可插拔的 AI 工厂操作系统（AI Factory OS）**。

### 1.2 核心链路

```
用户 → Maneki-AI → AI 总监 → MSSAGENT → CLINE / Worker
```

| 层级 | 角色 | 职责 |
|------|------|------|
| **用户层** | 任务发布者 | 发布任务、查看状态、干预执行 |
| **Maneki-AI（总部 HQ）** | 控制台 | 用户系统、任务调度、Worker 管理、链路可视化 |
| **AI 总监（AI Director）** | 决策层 | 理解任务、拆解计划、决定执行策略 |
| **MSSAGENT（调度层）** | 中间层 | 分发任务、监控 Worker、收集反馈 |
| **Worker 层** | 执行层 | 写代码、改文件、跑命令、生成 PR |

### 1.3 核心目标

通过 `DevDirector-Tasks` 队列实现**全自动代码生产与交付**。

### 1.4 设计原则

- **零基础设施消息总线**：GitHub Issues 作为持久化、可审计、免费的异步消息队列
- **解耦调度与执行**：云端和本地独立运行，互不影响
- **离线韧性**：本地离线时任务自动累积，重连后批量处理
- **自纠正闭环**：失败自动重试、绕行、升级或终止

---

## 2. 极简作业指南

### 2.1 面向最终用户的操作协议

1. **输入意图**：在输入框说出你的目标（例如："帮我做一份 AI 视频出海的推广方案"）
2. **确认产出**：点击下方生成的唯一执行按钮（例如："开始一键生产"）
3. **获取成果**：系统自动完成从调研到交付的全流程，成果会直接通过 GitHub Issue 同步给你

### 2.2 机器执行规则

- 严禁擅自修改核心架构，所有变动需先更新依赖映射图
- 自动化失败时，直接回传报错 Issue 到 `DevDirector-Tasks`
- 操作严格限定在 `task_queue/`、`scripts/`、`logs/` 目录

---

## 3. 系统架构

### 3.1 双平面架构

Maneki-AI 采用异步的 **"GitHub-Driven Dispatch"** 模型，系统解耦为两个独立平面：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ASYNC AI FACTORY — TWO PLANES                           │
│                                                                               │
│   🌐 RENDER CLOUD (Issue Dispatcher)                                         │
│   ┌──────────────────────────────────────────┐                               │
│   │  • Streamlit Dashboard (app.py)          │                               │
│   │  • factory_ui.py — UI trigger interface  │                               │
│   │  • github_issue.py — Issue creation API  │                               │
│   │                                          │                               │
│   │  Role: Accept user input, create GitHub  │                               │
│   │  Issues as production orders             │                               │
│   └──────────────────┬───────────────────────┘                               │
│                      │                                                       │
│                      │ POST /repos/DevDirector-Tasks/issues                  │
│                      ▼                                                       │
│              ┌──────────────────┐                                            │
│              │  GitHub Issues   │  Durable, auditable, async message queue   │
│              │  DevDirector-    │                                            │
│              │  Tasks           │                                            │
│              └────────┬─────────┘                                            │
│                       │                                                     │
│                       │ Poll for new Issues                                  │
│                       ▼                                                     │
│   🏭 LOCAL MACHINE (Autonomous Execution Engine)                             │
│   ┌──────────────────────────────────────────┐                               │
│   │  • watcher.py — polls repo for orders    │                               │
│   │  • run_task.py — execution pipeline      │                               │
│   │  • commands.json — task registry         │                               │
│   │  • workshop/ — ECC & OpenClaw engines    │                               │
│   │  • agent_engine/ — Agent-S integration   │                               │
│   │                                          │                               │
│   │  Role: Detect orders, strategize via     │                               │
│   │  ECC, execute via OpenClaw, scout via    │                               │
│   │  Agent-S                                 │                               │
│   └──────────────────────────────────────────┘                               │
│                                                                               │
│   🔄 The Flow: UI Trigger → GitHub Issue → Poll → Strategize → Execute → Log │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 关键设计决策

| 决策 | 理由 |
|------|------|
| **GitHub Issues 作为消息总线** | 零基础设施、持久化、可审计、免费 — 无需 RabbitMQ、Redis 或 SQS |
| **解耦调度与执行** | 云端和本地独立运行；各自可独立更新或重启 |
| **离线韧性** | 本地离线时任务累积；重连后批量处理积压任务 |
| **无隧道依赖** | 隧道仅用于实时流和回调，任务调度不依赖隧道 |

---

## 4. 角色职能

### 4.1 团队构成

| 角色 | 代号 | 职能 | 类比 |
|------|------|------|------|
| **ECC** | 🧠 大脑 | 任务分解与逻辑调度 | Central Nervous System |
| **OpenClaw** | 🔧 双手 | 代码落地与 Git 操作 | Lobster Claw (Mechanical Arm) |
| **Agent-S** | 👁️ 侦察兵 | 外部 SaaS 与 Web 交互 | Specialized Scout/Eye |

### 4.2 三层领域

| 领域 | 组件 | 范围 | 能力 |
|------|------|------|------|
| **🧠 策略** | **ECC** | 内部编排 | 任务分解、依赖排序、安全执行、结果验证 |
| **🔧 内部执行** | **OpenClaw** | 代码库操作 | CLI 命令、文件 I/O、代码转换、输出捕获 |
| **👁️ 外部情报** | **Agent-S** | Web 与 SaaS 环境 | 浏览器自动化、表单交互、数据提取、平台集成 |

---

## 5. 标准作业流程

### 5.1 完整执行流程

```
1. Dispatch     → factory_ui.py → github_issue.py → DevDirector-Tasks (GitHub Issue)
2. Poll & Ingest → watcher.py → run_task.py
3. Strategize   → Agency-Agents analyze task, evaluate strategies
4. Decompose    → ECC receives task + strategic context → structured steps
5. Consult      → ECC & OpenClaw query Codex for documentation & patterns
6. Execute Int. → ECC → OpenClaw (ClawWork/HKUDS) → CLI/file operations
7. Execute Ext. → ECC → Agent-S → web navigation & SaaS interaction
8. Verify       → ECC collects results → validates → decides next action
9. Log          → Structured execution log → logs/
```

### 5.2 数据流

```
User Input (UI)
      │
      ▼
factory_ui.py ──→ github_issue.py ──→ GitHub Issue (DevDirector-Tasks)
                                              │
                                              │ (poll)
                                              ▼
                                        watcher.py
                                              │
                                              ▼
                                        run_task.py
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                         ECC (Brain)   OpenClaw (Claw)  Agent-S (Eye)
                         • Decompose    • Generate cmd   • Navigate web
                         • Sequence     • Execute        • Interact SaaS
                         • Verify       • Capture output • Gather intel
                              │               │               │
                              └───────────────┼───────────────┘
                                              │
                                              ▼
                                          logs/
```

### 5.3 三一协作模型

ECC、OpenClaw 和 Agent-S 作为紧密耦合的**三一体（Trinity）**运作：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ECC + OPENCLAW + AGENT-S TRINITY                       │
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────┐        │
│   │                    ECC (The Brain)                            │        │
│   │                                                              │        │
│   │  1. Receive task from run_task.py                            │        │
│   │  2. Decompose into steps: analyze → plan → execute → verify  │        │
│   │  3. Determine step dependencies and ordering                 │        │
│   │  4. Dispatch internal steps to OpenClaw                      │        │
│   │  5. Dispatch external steps to Agent-S                       │        │
│   │  6. Verify results and decide next action                    │        │
│   └──────────┬──────────────────────────────────┬───────────────┘        │
│              │                                  │                         │
│              │ "Execute: deploy"                │ "Scout: check status"   │
│              ▼                                  ▼                         │
│   ┌─────────────────────┐          ┌──────────────────────┐              │
│   │  OpenClaw (The Claw)│          │ Agent-S (The Eye)    │              │
│   │                     │          │                      │              │
│   │  • CLI commands     │          │  • Web navigation    │              │
│   │  • File operations  │          │  • SaaS interaction  │              │
│   │  • Code transforms  │          │  • Data extraction   │              │
│   │  • Output capture   │          │  • Intel gathering   │              │
│   └──────────┬──────────┘          └──────────┬───────────┘              │
│              │                                  │                         │
│              └──────────┬───────────────────────┘                        │
│                         ▼                                                │
│   ┌─────────────────────────────────────────────────────────────┐        │
│   │              ECC (Verification Loop)                          │        │
│   │                                                              │        │
│   │  • Result OK    → proceed to next step or mark complete      │        │
│   │  • Result FAIL  → retry, escalate, or abort                  │        │
│   │  • All steps done → write final log to logs/                 │        │
│   └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│   🧠 ECC directs the strategy (The "What" and "When")                    │
│   🔧 OpenClaw executes internal code operations (The "How" — inside)     │
│   👁️ Agent-S performs external web intelligence (The "Where" — outside)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 核心引擎组件

### 6.1 ECC（Execution Control Core）— 中央神经系统

**文件**: `workshop/ecc_core.py`

ECC 是工厂的**中央神经系统**，编排整个执行生命周期 — 从任务接收到完成。

| 功能 | 描述 |
|------|------|
| **任务分解** | 将高级生产请求分解为结构化、可执行的步骤 |
| **上下文管理** | 跨子任务维护执行上下文，确保连续性和状态感知 |
| **依赖排序** | 管理任务间依赖关系 — 确定执行顺序 |
| **安全编排** | 强制执行操作护栏，验证前置条件，防止不安全执行路径 |
| **策略指导** | 决定**做什么**和**何时做** — 工厂的"大脑" |

### 6.2 OpenClaw（"龙虾钳"）— 机械臂

**文件**: `workshop/openclaw_core.py`

OpenClaw 是工厂的**机械臂** — 专门与代码库直接交互的代理。

| 功能 | 描述 |
|------|------|
| **CLI 命令生成** | 将战术指令转化为精确的 CLI 命令 |
| **代码库交互** | 读取、写入和修改工作区文件 |
| **输出捕获** | 捕获 stdout、stderr、返回码和执行时间 |
| **任务抓取** | 从执行队列中拉取任务并针对文件系统执行 |
| **战术执行** | 决定**如何做** — 工厂的"双手" |

### 6.3 Agent-S（"侦察兵/眼睛"）— 浏览器代理

**目录**: `agent_engine/`

Agent-S 是工厂的**侦察兵/眼睛** — 基于浏览器的自主代理。

| 功能 | 描述 |
|------|------|
| **网页导航** | 自主浏览网站、填写表单、从 Web 界面提取数据 |
| **SaaS 交互** | 通过 Web UI 与第三方平台交互（GitHub、Slack、Jira 等） |
| **情报收集** | 侦察外部信息源、监控仪表板、收集信号 |
| **桥接通信** | 通过 agent_engine 桥接队列与 ECC 和 OpenClaw 通信 |
| **外部操作** | 决定**看哪里**和**收集什么** — 工厂的"眼睛" |

---

## 7. 工厂集成架构

### 7.1 六组件集成架构

| # | 组件 | 来源 | 目录 | 角色 |
|---|------|------|------|------|
| 1 | **ECC** | `workshop/ecc_core.py` | `workshop/ecc/` | 🧠 中央神经系统 — 策略编排 |
| 2 | **OpenClaw** | `workshop/openclaw_core.py` | `workshop/agents/openclaw/` | 🔧 机械臂 — 代码库执行代理 |
| 3 | **Agent-S** | `agent_engine/` (Simular AI) | `agent_engine/` | 👁️ 侦察兵/眼睛 — 浏览器代理 |
| 4 | **Codex** | `oh-my-codex` | `workshop/lib/codex/` | 📚 文档与知识依赖 |
| 5 | **DevDirector-Tasks** | GitHub Issues | `winsentrobot008/DevDirector-Tasks` | 📨 中央 Issue 调度器（持久消息总线） |
| 6 | **Agency-Agents** | `agency-agents` | `workshop/ecc/strategy/` | 🧠 战略决策层 |

### 7.2 依赖映射

```
Layer 0 (Foundation):    DevDirector-Tasks ───── Codex
                                │                   │
                                │ dispatch          │ knowledge
                                ▼                   ▼
Layer 1 (Strategy):      ┌─────────────┐     Agency-Agents
                                │             │         │
                                │             │ strategic context
                                │             ▼
Layer 2 (Orchestration): │    ECC Core    │
                                │  ┌───────────┐ │
                                │  │ Decompose  │ │
                                │  │ Sequence   │ │
                                │  │ Verify     │ │
                                │  └─────┬─────┘ │
                                └────────┼────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │ consult            │ internal           │ external
                    ▼                    ▼                    ▼
Layer 3 (Execution):  Codex          OpenClaw            Agent-S
                                   ┌──────────┐      ┌──────────┐
                                   │ clawwork │      │ bridge   │
                                   │ hkuds    │      │ daemon   │
                                   └──────────┘      │ worker   │
                                                     └──────────┘
```

### 7.3 OpenClaw 变体

| 变体 | 路径 | 角色 |
|------|------|------|
| **ClawWork** | `workshop/agents/openclaw/clawwork/` | 核心 OpenClaw 实现 — 战术 CLI 执行和文件操作 |
| **ClawWork-HKUDS** | `workshop/agents/openclaw/hkuds/` | HKUDS 变体 — 增强的代码库交互与深度分析 |

### 7.4 完整架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      MANEKI-AI FACTORY INTEGRATION ARCHITECTURE                  │
│                                                                                   │
│   🌐 RENDER CLOUD (Issue Dispatcher)                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐         │
│   │  factory_ui.py → github_issue.py → DevDirector-Tasks (GitHub Issues)│         │
│   └──────────────────────────────────────────────────┬──────────────────┘         │
│                                                      │                             │
│                                                      ▼                             │
│   🏭 LOCAL FACTORY (Execution Engine)                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐         │
│   │  ┌──────────────────────────────────────────────────────────────┐  │         │
│   │  │                    ECC (workshop/ecc/)                        │  │         │
│   │  │  ┌─────────────────────────────────────────────────────────┐ │  │         │
│   │  │  │  Agency-Agents (workshop/ecc/strategy/)                 │ │  │         │
│   │  │  │  • Strategic analysis & risk evaluation                 │ │  │         │
│   │  │  │  • Multi-path recommendation                            │ │  │         │
│   │  │  └───────────────────────┬─────────────────────────────────┘ │  │         │
│   │  │                          │ strategic context                  │  │         │
│   │  │  ┌───────────────────────▼─────────────────────────────────┐ │  │         │
│   │  │  │  ECC Core — Decompose → Sequence → Verify               │ │  │         │
│   │  │  │  • Task decomposition into structured steps             │ │  │         │
│   │  │  │  • Dependency sequencing & safety enforcement           │ │  │         │
│   │  │  │  • Result verification & decision loop                  │ │  │         │
│   │  │  └──┬──────────────┬──────────────────┬───────────────────┘ │  │         │
│   │  │     │              │                  │                      │  │         │
│   │  │     │ consult      │ dispatch          │ dispatch            │  │         │
│   │  │     ▼              ▼                   ▼                     │  │         │
│   │  │  ┌────────┐ ┌────────────────┐ ┌────────────────────┐      │  │         │
│   │  │  │ Codex  │ │ OpenClaw       │ │ Agent-S            │      │  │         │
│   │  │  │(lib/   │ │(agents/        │ │(agent_engine/)     │      │  │         │
│   │  │  │ codex/)│ │ openclaw/)     │ │ • bridge.py        │      │  │         │
│   │  │  │ • Docs │ │ • clawwork/    │ │ • cline_daemon.py  │      │  │         │
│   │  │  │ • Pats │ │ • hkuds/       │ │ • cline_worker.py  │      │  │         │
│   │  │  │ • Know │ │ • CLI gen/exec │ │ • Web nav/SaaS     │      │  │         │
│   │  │  └────────┘ └────────────────┘ └────────────────────┘      │  │         │
│   │  └──────────────────────────────────────────────────────────────┘  │         │
│   └─────────────────────────────────────────────────────────────────────┘         │
│                                                                                   │
│   🔄 Flow: Dispatch → Strategize → Decompose → Consult → Execute → Verify → Log  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. AI 编排策略

### 8.1 多模型编排模式

Maneki-AI 采用 **"多模型编排"** 模式，专门的 AI 总监与操作代理（ECC、OpenClaw、Agent-S）共存协作。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-MODEL ORCHESTRATION PATTERN                          │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐       │
│   │              ORCHESTRATOR (Project Director / General AI)          │       │
│   │                                                                   │       │
│   │  Role: High-Level Strategist                                      │       │
│   │  • Architectural design & requirement interpretation              │       │
│   │  • High-level task decomposition into mission directives          │       │
│   │  • Defines the "Battle Plan" from user intent                     │       │
│   │  • Adapts strategy in real-time based on agent feedback           │       │
│   └──────────────────────────┬────────────────────────────────────────┘       │
│                              │                                               │
│                              │ delegates granular steps                      │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────┐       │
│   │              ENGINE ROOM (Operational Agents)                      │       │
│   │                                                                   │       │
│   │  ┌──────────────┐  ┌────────────────┐  ┌────────────────────┐   │       │
│   │  │    ECC        │  │   OpenClaw     │  │    Agent-S         │   │       │
│   │  │  (Brain)      │  │  (Claw)        │  │   (Eye)           │   │       │
│   │  │  • Sequence   │  │  • Execute CLI │  │  • Browse web     │   │       │
│   │  │  • Verify     │  │  • File ops    │  │  • SaaS interact  │   │       │
│   │  │  • Safety     │  │  • Transform   │  │  • Intel gather   │   │       │
│   │  └──────────────┘  └────────────────┘  └────────────────────┘   │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                              │                                               │
│                              │ report success/failure                        │
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────┐       │
│   │              ORCHESTRATOR (Feedback Loop)                         │       │
│   │                                                                   │       │
│   │  • Analyzes operational results from Engine Room                  │       │
│   │  • Adapts strategy: retry, re-route, escalate, or abort          │       │
│   │  • Generates next set of directives                               │       │
│   │  • Maintains high-level context across iterations                 │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                                                               │
│   🔄 Strategy Phase → Execution Phase → Feedback Loop → Adapt → Repeat      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 三阶段协作

#### 阶段 1：🧠 策略阶段 — 编排者定义"作战计划"

编排者（项目总监/通用 AI）分析用户意图并生成高级战略计划：

- **需求解读**：将模糊的用户请求转化为结构化任务目标
- **架构设计**：确定系统架构、组件边界和集成点
- **任务分解**：将任务分解为高级阶段
- **风险评估**：识别潜在故障点并定义回退策略
- **资源分配**：决定使用哪些操作代理及其能力范围

**输出**：结构化的"作战计划" — 一组准备执行的任务指令

#### 阶段 2：⚙️ 执行阶段 — 引擎室精确执行

编排者将粒度步骤委托给专门的操作代理（"引擎室"）：

| 代理 | 执行阶段角色 |
|------|-------------|
| **ECC** | 接收任务指令 → 分解为可执行步骤 → 排序依赖 → 执行安全护栏 |
| **OpenClaw** | 执行代码库操作 — CLI 命令、文件转换、输出捕获 |
| **Agent-S** | 执行外部操作 — 网页导航、SaaS 交互、情报收集 |

#### 阶段 3：🔄 反馈循环 — 实时策略调整

执行后，操作代理向编排者报告成功/失败：

- **成功路径**：结果验证 → 编排者确认任务进展 → 下一阶段开始
- **失败路径**：代理报告失败及上下文 → 编排者分析根因 → 调整策略：
  - **重试**：相同方法，不同参数
  - **绕行**：替代执行路径
  - **升级**：需要人工干预
  - **终止**：任务终止，记录部分结果
- **部分成功**：部分步骤成功，部分失败 → 编排者决定重试哪些、跳过哪些

### 8.3 为什么是多模型编排？

| 优势 | 描述 |
|------|------|
| **🧠 并行智能** | 高级抽象思考（编排者）和低级代码执行（引擎室）同时发生 |
| **🛡️ 关注点分离** | 编排者关注"做什么"和"为什么"；引擎室关注"怎么做" |
| **🔄 自纠正** | 反馈循环实现实时策略调整，无需重启整个流水线 |
| **🔌 可插拔总监** | 不同编排者（项目总监、代码架构师、QA 总监）可根据任务类型切换 |
| **📈 可扩展** | 新操作代理可添加到引擎室，无需更改编排层 |

### 8.4 编排者 ↔ 引擎室契约

```
┌─────────────────────────────────────────────────────────────────┐
│                    COLLABORATION CONTRACT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Orchestrator → Engine Room:                                      │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │ {                                                          │   │
│  │   "mission_id": "M-20260602-001",                         │   │
│  │   "directive": "Deploy v2.1 to staging",                  │   │
│  │   "phases": [                                              │   │
│  │     {"phase": 1, "action": "build",   "agent": "openclaw"},│   │
│  │     {"phase": 2, "action": "test",    "agent": "openclaw"},│   │
│  │     {"phase": 3, "action": "verify",  "agent": "agent-s"}, │   │
│  │     {"phase": 4, "action": "deploy",  "agent": "openclaw"} │   │
│  │   ],                                                        │   │
│  │   "fallback": "rollback",                                   │   │
│  │   "context": { ... }                                        │   │
│  │ }                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Engine Room → Orchestrator:                                      │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │ {                                                          │   │
│  │   "mission_id": "M-20260602-001",                         │   │
│  │   "phase": 2,                                              │   │
│  │   "status": "failed",                                      │   │
│  │   "error": "Test suite: 3/47 failures in auth module",     │   │
│  │   "recommendation": "retry_with_fix",                      │   │
│  │   "artifacts": { ... }                                     │   │
│  │ }                                                          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. 扩展模块

| 模块 | 路径 | 角色 |
|------|------|------|
| **`factory_ui.py`** | `./factory_ui.py` | 前端界面逻辑 — 渲染工厂触发按钮和用户控件 |
| **`github_issue.py`** | `./github_issue.py` | GitHub API 客户端 — 在 `DevDirector-Tasks` 中创建 Issue |
| **`run_task.py`** | `./run_task.py` | 执行流水线 — 读取 `commands.json`，通过 subprocess 调度 CLI 命令 |
| **`commands.json`** | `./commands.json` | 系统任务注册表 — 将任务名称映射到 CLI 命令、引擎和超时 |
| **`workshop/`** | `./workshop/` | 引擎核心 — 包含 `ecc_core.py` 和 `openclaw_core.py` |
| **`agent_engine/`** | `./agent_engine/` | Agent-S 集成层 — 桥接队列、Cline 守护进程/工作进程、安全协议 |

---

## 10. 项目结构

```
Maneki-AI/
├── app.py                      # Streamlit 云端仪表板（Render 入口）
├── factory_ui.py               # 前端界面逻辑（Issue 调度器）
├── github_issue.py             # GitHub API 客户端（Issue 创建）
├── run_task.py                 # 执行流水线（commands.json → subprocess）
├── commands.json               # 系统任务注册表（ECC + OpenClaw + Agent-S）
├── start_factory.py            # 本地工厂编排器
├── render.yaml                 # Render 部署配置
├── requirements.txt            # Python 依赖
├── runtime.txt                 # Python 运行时版本
├── .env.example                # 环境变量模板
├── .clinerules                 # Cline 代理操作规则
│
├── workshop/                   # 引擎核心
│   ├── ecc_core.py             # ECC — 中央神经系统
│   ├── openclaw_core.py        # OpenClaw — 机械臂
│   └── factory_integration_map.json  # 依赖映射图
│
├── agent_engine/               # Agent-S — 侦察兵/眼睛
│   ├── bridge.py               # 代理间桥接队列
│   ├── cline_daemon.py         # Agent-S 守护进程
│   ├── cline_worker.py         # Agent-S 工作进程
│   └── safety/                 # 浏览器安全协议
│
├── core/                       # 基础设施
│   ├── api_gateway.py          # HTTP API 网关（端口 8000）
│   └── task_listener.py        # 任务队列轮询器与执行器
│
├── scripts/                    # 工具脚本
│   ├── start_tunnel.py         # localtunnel 隧道
│   ├── trigger_deploy.py       # Render 部署钩子触发
│   ├── example_worker.py       # 示例工作进程
│   └── test_factory_startup.py # 启动测试套件
│
├── agents/                     # AI 总监编排
│   └── orchestrator.py
│
├── task_queue/                 # 任务生命周期
│   ├── pending/                # 待处理任务
│   ├── processing/             # 处理中任务
│   └── completed/              # 已完成任务
│
├── logs/                       # 执行日志
├── config/                     # 应用配置
├── state/                      # 代理状态持久化
├── docs/                       # 文档
│   ├── PROJECT_OVERVIEW.md     # 项目说明书（本文档）
│   └── WEB_ARCHITECTURE.md     # Web 前端架构文档
├── deliveries/                 # 任务交付物
├── analyst/                    # 战略分析
├── radar/                      # 信号扫描
└── warroom/                    # 报告生成
```

---

## 11. 快速开始

### 前置条件

- Python 3.12+
- Node.js（用于 `npx localtunnel`）
- GitHub 账号，需 `GITHUB_TOKEN`（gist + repo:issues 权限）

### 设置

```bash
git clone https://github.com/winsentrobot008/Maneki-AI.git
cd Maneki-AI
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 GITHUB_TOKEN 和 MANEKI_TUNNEL_GIST_ID
```

### 启动工厂

```bash
python start_factory.py
```

启动 API 网关（端口 8000）、任务监听器和本地隧道。

### 本地运行任务

```bash
python run_task.py <task_name> --log
```

可用任务：`deploy`、`build`、`test`、`start`、`analyze`、`scan`、`report`、`orchestrate`、`bridge`、`worker`

### 打开仪表板

访问 **[https://maneki-ai.onrender.com/](https://maneki-ai.onrender.com/)** 调度生产订单。

### 必需的环境变量

| 变量 | 必需 | 用途 |
|------|------|------|
| `GITHUB_TOKEN` | ✅ **是** | GitHub PAT，需 `gist` 和 `repo:issues` 权限 |
| `MANEKI_TUNNEL_GIST_ID` | ✅ **是** | 隧道 URL 公告板的私有 Gist ID |
| `MANEKI_ENABLE_TUNNEL` | ❌ 否 | 设为 `0` 禁用隧道（默认：`1`） |
| `MANEKI_TUNNEL_PORT` | ❌ 否 | 隧道本地端口（默认：`8000`） |
| `API_GATEWAY_URL` | ❌ 否 | 静态回退隧道 URL |

---

## 12. 开发路线图

### 阶段 1（当前）：Messenger-Agent（MSSAGENT 本地实现）
- [x] ECC 核心引擎 — 任务分解与编排
- [x] OpenClaw 核心引擎 — CLI 命令生成与执行
- [x] Agent-S 集成 — 桥接队列与浏览器自动化
- [x] API 网关 — HTTP 端点用于任务注入
- [x] 任务监听器 — 轮询待处理队列并执行
- [x] Web 仪表板 — Streamlit 前端用于任务调度
- [x] 隧道服务 — localtunnel 用于云端