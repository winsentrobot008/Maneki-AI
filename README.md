<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Architecture-Async%20AI%20Factory-blue?style=flat-square" alt="Architecture">
  <img src="https://img.shields.io/badge/Deploy-Render%20%2B%20Local%20Factory-ff6f00?style=flat-square" alt="Deploy">
  <img src="https://img.shields.io/badge/Orchestration-GitHub%20Driven-purple?style=flat-square" alt="Orchestration">
  <img src="https://img.shields.io/badge/Autonomy-35%25%20Built-yellow?style=flat-square" alt="Autonomy">
</p>

<h1 align="center">🐱 Maneki-AI: The Autonomous Factory</h1>
<h3 align="center">Async AI Factory — GitHub-Driven Dispatch, Local Autonomous Execution</h3>

<p align="center">
  <strong>Command & Control Center:</strong> <a href="https://maneki-ai.onrender.com/">https://maneki-ai.onrender.com/</a>
  <br>
  <sub><strong>App Version:</strong> v0.3.0-factory · <strong>Architecture:</strong> Async AI Factory</sub>
</p>

---

# 📋 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Core Engine Components](#-core-engine-components)
3. [Strategic Integration](#-strategic-integration)
4. [Current Workflow](#-current-workflow)
5. [Factory Integration Architecture](#-factory-integration-architecture)
6. [AI Orchestration Strategy](#-ai-orchestration-strategy)
7. [Extension Modules](#-extension-modules)
8. [Project Structure](#-project-structure)
9. [Quick Start](#-quick-start)
10. [Required Environment Variables](#-required-environment-variables)

---

# 🏗️ Architecture Overview

Maneki-AI has transitioned to an asynchronous **"GitHub-Driven Dispatch"** model. The system is decoupled into two independent planes that communicate through GitHub Issues as a durable, persistent message bus.

### The Two Planes

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

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **GitHub Issues as Message Bus** | Zero-infrastructure, durable, auditable, free — no RabbitMQ, Redis, or SQS required |
| **Decoupled Dispatch & Execution** | Cloud and local operate independently; each can be updated or restarted without affecting the other |
| **Offline Resilience** | Issues accumulate while local is offline; watcher processes backlog on reconnection |
| **No Tunnel Dependency for Dispatch** | Tunnel is only needed for live streaming and callbacks, not for task dispatch |

---

# 🧠 Core Engine Components

The factory is powered by three complementary engines that form a trinity — ECC directs the mission, OpenClaw executes internal code operations, and Agent-S performs external web-based intelligence gathering and interaction.

## ECC (Execution Control Core) — The Central Nervous System

**File:** `workshop/ecc_core.py`

ECC is the factory's **Central Nervous System**. It orchestrates the entire execution lifecycle — from task ingestion to completion — ensuring that every production request is decomposed, sequenced, and executed safely.

| Function | Description |
|----------|-------------|
| **Task Decomposition** | Breaks high-level production requests into structured, executable steps |
| **Context Management** | Maintains execution context across sub-tasks, ensuring continuity and state awareness |
| **Dependency Sequencing** | Manages inter-task dependencies — determines what must run before what |
| **Safety Orchestration** | Enforces operational guardrails, validates preconditions, and prevents unsafe execution paths |
| **Strategic Direction** | Determines **what** to do and **when** to do it — the "brain" of the factory |

## OpenClaw (The "Lobster" Claw) — The Mechanical Arm

**File:** `workshop/openclaw_core.py`

OpenClaw is the factory's **Mechanical Arm** — a specialized agent designed to interact directly with the codebase. Like a lobster's claw, it reaches into the file system, "grabs" production tasks from the queue, and performs precise file/code transformations.

| Function | Description |
|----------|-------------|
| **CLI Command Generation** | Translates tactical instructions into precise CLI commands |
| **Codebase Interaction** | Reads, writes, and modifies files in the workspace |
| **Output Capture** | Captures stdout, stderr, return codes, and execution timing |
| **Task Grabbing** | Pulls tasks from the execution queue and executes them against the filesystem |
| **Tactical Execution** | Determines **how** to do it — the "hands" of the factory |

## Agent-S (The "Specialized Scout/Eye") — The Browser-Based Agent

**Directory:** `agent_engine/`

Agent-S is the factory's **Specialized Scout/Eye** — a browser-based autonomous agent designed to navigate external web environments, interact with SaaS platforms, and perform tasks beyond direct codebase access. It extends the factory's reach into the wider digital ecosystem.

| Function | Description |
|----------|-------------|
| **Web Navigation** | Autonomously browses websites, fills forms, and extracts data from web interfaces |
| **SaaS Interaction** | Interacts with third-party platforms (GitHub, Slack, Jira, etc.) via their web UIs |
| **Intelligence Gathering** | Scouts external sources for information, monitors dashboards, and collects signals |
| **Bridge Communication** | Communicates with ECC and OpenClaw via the agent_engine bridge queue |
| **External Operations** | Determines **where** to look and **what** to gather — the "eyes" of the factory |

## Workflow Integration: The Trinity

ECC, OpenClaw, and Agent-S operate as a tightly coupled **trinity**:

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

### Analogy

| Component | Analogy | Role |
|-----------|---------|------|
| **ECC** | 🧠 Central Nervous System | Strategic direction — decides what to do and when |
| **OpenClaw** | 🦞 Lobster Claw (Mechanical Arm) | Tactical execution — decides how to do it and performs the action |
| **Agent-S** | 👁️ Specialized Scout/Eye | External intelligence — determines where to look and what to gather |

---

# 🔗 Strategic Integration

These agents function as a **trinity**: ECC directs the mission, OpenClaw executes internal code operations, and Agent-S performs external web-based intelligence gathering and interaction.

### The Three Domains

| Domain | Component | Scope | Capability |
|--------|-----------|-------|------------|
| **🧠 Strategy** | **ECC** | Internal orchestration | Task decomposition, dependency sequencing, safety enforcement, verification |
| **🔧 Internal Execution** | **OpenClaw** | Codebase operations | CLI commands, file I/O, code transformation, output capture |
| **👁️ External Intelligence** | **Agent-S** | Web & SaaS environments | Browser automation, form interaction, data extraction, platform integration |

### How the Trinity Works Together

1. **ECC receives a mission** — A high-level production order arrives via GitHub Issues
2. **ECC decomposes the mission** — Breaks it into internal steps (code changes) and external steps (web research, SaaS operations)
3. **OpenClaw executes internal steps** — Performs file operations, runs CLI commands, transforms code
4. **Agent-S executes external steps** — Browses documentation, checks SaaS dashboards, gathers intelligence
5. **ECC verifies all results** — Validates outputs from both agents, decides next actions
6. **The factory logs the outcome** — A structured execution log is written to `logs/`

### Communication Flow

```
                    ┌─────────────────┐
                    │   GitHub Issue  │  Mission input
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  ECC (Brain)    │  Strategic decomposition
                    └───┬─────────┬───┘
                        │         │
              ┌─────────┘         └─────────┐
              ▼                              ▼
    ┌──────────────────┐          ┌──────────────────┐
    │  OpenClaw (Claw) │          │ Agent-S (Eye)    │
    │  Internal Ops    │          │ External Ops     │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             └──────────┬──────────────────┘
                        ▼
               ┌─────────────────┐
               │  ECC (Verify)   │  Result validation
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │   logs/         │  Execution record
               └─────────────────┘
```

---

# ⚙️ Current Workflow

## Step-by-Step Execution

### 1. Dispatch — User Triggers via UI

The user triggers a production task through the Render dashboard. The frontend acts as an **Issue Dispatcher**:

- `factory_ui.py` renders the trigger interface
- `github_issue.py` creates a new GitHub Issue in the `winsentrobot008/DevDirector-Tasks` repository
- The Issue body contains the task specification, parameters, and metadata

### 2. Monitoring — Watcher Polls for Orders

A local **`watcher.py`** agent continuously polls the `DevDirector-Tasks` repository for new production orders:

- Detects unprocessed Issues
- Extracts task name and parameters from the Issue body
- Triggers the execution pipeline

### 3. Execution — Strategize & Operate

Once an order is detected, the `run_task.py` pipeline is triggered:

1. **Strategize (ECC)**: The task is decomposed into structured steps. Dependencies are resolved. A safe execution plan is formulated.
2. **Operate (OpenClaw)**: Each internal step is executed against the codebase via CLI commands. Output is captured and reported back.
3. **Scout (Agent-S)**: Each external step is executed via browser-based web navigation and SaaS interaction.
4. **Verify (ECC)**: Results are validated. On success, the next step proceeds. On failure, the system retries, escalates, or aborts.
5. **Log**: A structured execution log is written to `logs/`.

### Data Flow Diagram

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

---

# 🏭 Factory Integration Architecture

The Maneki-AI Factory has been extended with a **six-component integration architecture** that layers strategic intelligence, knowledge management, and specialized execution variants under the ECC/OpenClaw/Agent-S trinity.

## Integrated Components

| # | Component | Source | Directory | Role |
|---|-----------|--------|-----------|------|
| 1 | **ECC** | `workshop/ecc_core.py` | `workshop/ecc/` | 🧠 Central Nervous System — Strategic Orchestration |
| 2 | **OpenClaw** | `workshop/openclaw_core.py` | `workshop/agents/openclaw/` | 🔧 Mechanical Arm — Codebase Execution Agent |
| 3 | **Agent-S** | `agent_engine/` (Simular AI) | `agent_engine/` | 👁️ Specialized Scout/Eye — Browser-Based External Agent |
| 4 | **Codex** | `oh-my-codex` | `workshop/lib/codex/` | 📚 Documentation & Knowledge Dependency |
| 5 | **DevDirector-Tasks** | GitHub Issues | `winsentrobot008/DevDirector-Tasks` | 📨 Central Issue Dispatcher (Durable Message Bus) |
| 6 | **Agency-Agents** | `agency-agents` | `workshop/ecc/strategy/` | 🧠 Strategic Decision-Making Layer |

## Dependency Map

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

## OpenClaw Variants (ClawWork & ClawWork-HKUDS)

OpenClaw now supports two execution variants under `workshop/agents/openclaw/`:

| Variant | Path | Role |
|---------|------|------|
| **ClawWork** | `workshop/agents/openclaw/clawwork/` | Core OpenClaw implementation — tactical CLI execution and file operations |
| **ClawWork-HKUDS** | `workshop/agents/openclaw/hkuds/` | HKUDS variant — enhanced codebase interaction with deeper analysis capabilities |

Both variants are dispatched by ECC and follow the same `generate_command()` → `execute()` → `capture()` contract.

## Codex Knowledge Base (oh-my-codex)

Mapped as a documentation/knowledge dependency at `workshop/lib/codex/`:

- **ECC** queries Codex for strategic context during task decomposition
- **OpenClaw** references Codex for code patterns, examples, and best practices
- **Agency-Agents** consume Codex for informed strategic decision-making

## Agency-Agents Strategic Layer

Integrated at `workshop/ecc/strategy/` as the strategic decision-making layer:

- **Input**: Task from DevDirector-Tasks + knowledge from Codex
- **Process**: Strategic analysis → risk evaluation → multi-path recommendation
- **Output**: Strategic context injected into ECC decomposition
- **Relationship**: Agency-Agents sit *above* ECC, feeding strategic intelligence into the orchestration loop

## Complete Execution Flow

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

## Architecture Diagram

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

## Dependency Map (JSON)

A machine-readable dependency map is available at:
[`workshop/factory_integration_map.json`](workshop/factory_integration_map.json)

This JSON file contains:
- Full component definitions with roles, responsibilities, and integration points
- Directed dependency graph with layered node structure
- Target directory layout for all six components
- Complete 9-step execution flow specification
- ASCII architecture diagram

---

# 🤖 AI Orchestration Strategy

The Maneki-AI Factory utilizes a **"Multi-Model Orchestration"** pattern where specialized AI directors (like the Project Director) coexist and collaborate with operational agents (ECC, OpenClaw, Agent-S).

## Orchestrator Collaboration Model

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

## The Three Phases of Collaboration

### 1. 🧠 Strategy Phase — The Orchestrator Defines the "Battle Plan"

The Orchestrator (Project Director / General AI) analyzes the user's intent and produces a high-level strategic plan:

- **Requirement Interpretation**: Translates ambiguous user requests into structured mission objectives
- **Architectural Design**: Determines the system architecture, component boundaries, and integration points
- **Task Decomposition**: Breaks the mission into high-level phases — what needs to happen and in what order
- **Risk Assessment**: Identifies potential failure points and defines fallback strategies
- **Resource Allocation**: Decides which operational agents to engage and in what capacity

**Output**: A structured "Battle Plan" — a set of mission directives ready for execution.

### 2. ⚙️ Execution Phase — The Engine Room Executes with Precision

The Orchestrator delegates granular steps to the specialized operational agents, which function as the **"Engine Room"**:

| Agent | Role in Execution Phase |
|-------|------------------------|
| **ECC** | Receives mission directives → decomposes into executable steps → sequences dependencies → enforces safety guardrails |
| **OpenClaw** | Executes codebase operations — CLI commands, file transformations, output capture |
| **Agent-S** | Performs external operations — web navigation, SaaS interaction, intelligence gathering |

The Engine Room operates with **technical precision**, executing the Orchestrator's high-level directives without needing to re-interpret the original user intent.

### 3. 🔄 Feedback Loop — Real-Time Strategy Adaptation

After execution, operational agents report success/failure back to the Orchestrator:

- **Success Path**: Results are validated → Orchestrator confirms mission progress → next phase begins
- **Failure Path**: Agent reports failure with context → Orchestrator analyzes root cause → adapts strategy:
  - **Retry**: Same approach, different parameters
  - **Re-route**: Alternative execution path
  - **Escalate**: Human intervention required
  - **Abort**: Mission terminated with partial results logged
- **Partial Success**: Some steps succeed, others fail → Orchestrator decides which to retry and which to skip

This **self-correcting loop** ensures the system can handle unexpected failures without human intervention.

## Why Multi-Model Orchestration?

| Benefit | Description |
|---------|-------------|
| **🧠 Parallel Intelligence** | High-level abstract thinking (Orchestrator) and low-level code execution (Engine Room) occur simultaneously, not sequentially |
| **🛡️ Separation of Concerns** | Orchestrator focuses on "what" and "why"; Engine Room focuses on "how" — each optimized for its domain |
| **🔄 Self-Correcting** | The feedback loop enables real-time strategy adaptation without restarting the entire pipeline |
| **🔌 Pluggable Directors** | Different Orchestrators (Project Director, Code Architect, QA Director) can be swapped in depending on the mission type |
| **📈 Scalable** | New operational agents can be added to the Engine Room without changing the Orchestration layer |

## Orchestrator ↔ Engine Room Contract

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

This parallel structure ensures that high-level abstract thinking and low-level code execution occur simultaneously, enabling a self-correcting autonomous system that can handle complex, multi-step production workflows without human intervention.

---

# 🧩 Extension Modules

| Module | Path | Role |
|--------|------|------|
| **`factory_ui.py`** | `./factory_ui.py` | Frontend interface logic — renders the factory trigger button and user controls on the Render dashboard |
| **`github_issue.py`** | `./github_issue.py` | GitHub API client — creates Issues in `winsentrobot008/DevDirector-Tasks` as production orders |
| **`run_task.py`** | `./run_task.py` | Execution pipeline — reads `commands.json`, dispatches CLI commands via subprocess, writes structured logs |
| **`commands.json`** | `./commands.json` | System task registry — maps task names to CLI commands, engines (ECC/OpenClaw/Agent-S), and timeouts |
| **`workshop/`** | `./workshop/` | Engine core — contains `ecc_core.py` (ECC) and `openclaw_core.py` (OpenClaw) |
| **`agent_engine/`** | `./agent_engine/` | Agent-S integration layer — bridge queue, Cline daemon/worker, safety protocols for browser-based autonomous operations |

---

# 📁 Project Structure

```
Maneki-AI/
├── app.py                      # Streamlit cloud dashboard (Render entry point)
├── factory_ui.py               # Frontend interface logic (Issue dispatcher)
├── github_issue.py             # GitHub API client for Issue creation
├── run_task.py                 # Execution pipeline (commands.json → subprocess)
├── commands.json               # System task registry (ECC + OpenClaw + Agent-S)
├── start_factory.py            # Local factory orchestrator
├── render.yaml                 # Render deployment configuration
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python runtime version
├── .env.example                # Environment variable template
├── .clinerules                 # Cline agent operational rules
│
├── workshop/                   # Engine core
│   ├── ecc_core.py             # ECC — Central Nervous System
│   └── openclaw_core.py        # OpenClaw — Mechanical Arm
│
├── agent_engine/               # Agent-S — Specialized Scout/Eye
│   ├── bridge.py               # Inter-agent bridge queue
│   ├── cline_daemon.py         # Agent-S daemon process
│   ├── cline_worker.py         # Agent-S worker process
│   └── safety/                 # Browser safety protocols
│
├── core/                       # Legacy infrastructure
│   ├── api_gateway.py          # HTTP API Gateway (port 8000)
│   └── task_listener.py        # Task queue poller & executor
│
├── scripts/                    # Utility scripts
│   ├── start_tunnel.py         # localtunnel provisioner
│   ├── trigger_deploy.py       # Render deploy hook trigger
│   └── test_factory_startup.py # Startup test suite
│
├── agents/                     # AI Director orchestration
│   └── orchestrator.py
│
├── task_queue/                 # Task lifecycle
│   ├── pending/
│   ├── processing/
│   └── completed/
│
├── logs/                       # Execution logs
├── config/                     # Application configuration
├── state/                      # Agent state persistence
├── docs/                       # Documentation
├── deliveries/                 # Task delivery artifacts
├── analyst/                    # Strategic analysis
├── radar/                      # Signal scanning
└── warroom/                    # Report generation
```

---

# 🏁 Quick Start

### Prerequisites

- Python 3.12+
- Node.js (for `npx localtunnel`)
- GitHub account with `GITHUB_TOKEN` (gist + repo:issues scopes)

### Setup

```bash
git clone https://github.com/winsentrobot008/Maneki-AI.git
cd Maneki-AI
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GITHUB_TOKEN and MANEKI_TUNNEL_GIST_ID
```

### Start Factory

```bash
python start_factory.py
```

Launches API Gateway (port 8000), Task Listener, and local tunnel.

### Run a Task Locally

```bash
python run_task.py <task_name> --log
```

Available tasks: `deploy`, `build`, `test`, `start`, `analyze`, `scan`, `report`, `orchestrate`, `bridge`, `worker`.

### Open Dashboard

Navigate to **[https://maneki-ai.onrender.com/](https://maneki-ai.onrender.com/)** to dispatch production orders.

---

# 📋 Required Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_TOKEN` | ✅ **Yes** | GitHub PAT with `gist` and `repo:issues` scopes |
| `MANEKI_TUNNEL_GIST_ID` | ✅ **Yes** | Private Gist ID for tunnel URL bulletin board |
| `MANEKI_ENABLE_TUNNEL` | ❌ No | Set to `0` to disable tunnel (default: `1`) |
| `MANEKI_TUNNEL_PORT` | ❌ No | Local port to tunnel (default: `8000`) |
| `API_GATEWAY_URL` | ❌ No | Static fallback tunnel URL |

---

<p align="center">
  <strong>Maneki-AI</strong> — The Autonomous Factory 🐱
</p>
<p align="center">
  <sub>v0.3.0-factory · Async AI Factory · GitHub-Driven Dispatch</sub>
</p>
