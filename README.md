<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Architecture-Hybrid%20Cloud%20AI%20Factory-blue?style=flat-square" alt="Architecture">
  <img src="https://img.shields.io/badge/Deploy-Render%20%2B%20Local%20Factory-ff6f00?style=flat-square" alt="Deploy">
  <img src="https://img.shields.io/badge/Orchestration-Gist%20Bulletin%20Board-purple?style=flat-square" alt="Orchestration">
  <img src="https://img.shields.io/badge/Autonomy-35%25%20Built-yellow?style=flat-square" alt="Autonomy">
</p>

<h1 align="center">🐱 Maneki-AI</h1>
<h3 align="center">Hybrid Cloud AI Factory — Orchestrate High-Performance Local Agent Execution from the Cloud</h3>

<p align="center">
  <strong>Command & Control Center:</strong> <a href="https://maneki-ai.onrender.com/">https://maneki-ai.onrender.com/</a>
  <br>
  <sub><strong>App Version:</strong> v0.2.0-debug · <strong>Commit:</strong> <code>1243729</code></sub>
</p>

---

# 📋 Table of Contents

1. [🌌 The Polaris Vision](#-the-polaris-vision)
2. [📊 Current Progress Assessment (State: 35% Built)](#-current-progress-assessment-state-35-built)
3. [🗺️ The 4-Phase Roadmap to 100% Autonomy](#%EF%B8%8F-the-4-phase-roadmap-to-100-autonomy)
4. [🏗️ Architectural Evolution (The Gist Bulletin Board)](#%EF%B8%8F-architectural-evolution-the-gist-bulletin-board)
5. [🎛️ Command & Control Center (Cloud UI Dashboard)](#%EF%B8%8F-command--control-center-cloud-ui-dashboard)
6. [🛡️ Production Safeguards & Process Reliability](#%EF%B8%8F-production-safeguards--process-reliability)
7. [🎛️ Telemetry & Versioning Standard](#%EF%B8%8F-telemetry--versioning-standard)
8. [📋 Required Environment Variables](#-required-environment-variables)
9. [🏁 Quick Start](#-quick-start)
10. [📁 Project Structure](#-project-structure)

---

# 🌌 The Polaris Vision

> **"A self-correcting, autonomous agentic loop — where the Cloud Director AI possesses real-time awareness of network and browser states, and can programmatically drive the local Cline engine to write code, execute tasks, and self-heal without human intervention."**

### The Ultimate Objective

Maneki-AI's **Polaris Vision** is to create a fully autonomous **closed-loop black-box factory**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE AUTONOMOUS CLOSED-LOOP FACTORY                      │
│                                                                           │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
│   │  🌐 Cloud     │     │  📡 Tunnel   │     │  🏭 Local    │             │
│   │  Director AI  │────▶│  (Bidirectional)│──▶│  Cline Engine│             │
│   │  (Render)     │     │  (Gist Disc.)│     │  (Your PC)   │             │
│   │               │◀────│              │◀────│              │             │
│   │  • Perceives  │     │  • State     │     │  • Executes  │             │
│   │  • Decides    │     │  • Telemetry │     │  • Reports   │             │
│   │  • Commands   │     │  • Callbacks │     │  • Self-heals│             │
│   └──────────────┘     └──────────────┘     └──────────────┘             │
│                                                                           │
│   🔄 The Loop: Perceive → Decide → Command → Execute → Report → Perceive │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Principles Guiding Every Decision

| Principle | Description |
|-----------|-------------|
| **Zero Human-in-the-Loop** | The system must eventually self-correct, self-debug, and self-deploy without requiring a human operator to intervene |
| **Bidirectional Awareness** | The Cloud Director must see what the local machine sees — network state, browser state, file system state — in real time |
| **Programmatic Reverse Control** | The Cloud Director must be able to inject commands, keystrokes, and file writes into the local Cline engine as if a human were typing |
| **Fail-Safe by Design** | Every autonomous action must have a circuit breaker — the system must know when to stop and escalate |
| **Incremental Autonomy** | Each phase adds a layer of self-sufficiency; no phase leaps ahead without the previous one being battle-tested |

---

# 📊 Current Progress Assessment (State: 35% Built)

### ✅ Infrastructure Foundation — 100% Ready

The secure **Cloud-to-Local tunneling layer** is fully operational and production-hardened:

| Component | Status | Details |
|-----------|--------|---------|
| GitHub Gist Bulletin Board | ✅ **Production** | Private Gist handshake protocol, token-authenticated, zero middleware |
| localtunnel Provisioning | ✅ **Production** | Automatic tunnel creation, URL publication, orphan cleanup |
| API Gateway (port 8000) | ✅ **Production** | Task ingestion, health checks, cross-platform process management |
| Task Listener | ✅ **Production** | Queue polling, execution dispatch, log/report generation |
| Factory Orchestrator | ✅ **Production** | Unified startup/shutdown of all local components |

### 🔧 Command & Dispatch Pipeline — 75% Ready

The system currently functions as a robust **"Command & Dispatch" pipeline**:

```
User Input (Cloud UI) → Parameterized Mission → Tunnel → Local Factory → Execution → Logs
```

- ✅ Multi-model AI Director selection (Claude, GPT, Gemini, DeepSeek)
- ✅ Coder team scaling (1–10 workers)
- ✅ Role-based specialization (Frontend, Backend, DevOps, etc.)
- ✅ Version-tagged deployment with browser console telemetry
- ⬜ **Live streaming logs** from local workshop back to cloud UI
- ⬜ **Real-time pipeline status matrix** with per-stage latency metrics

### 🧗 The Next Mountain: Perception & Reverse Control

The core **"Perception & Reverse Control"** loop is the critical missing piece:

| Capability | Status | Why It Matters |
|-----------|--------|----------------|
| Live browser state streaming | ⬜ **Not started** | Cloud Director cannot see what the local browser renders |
| Real-time file system awareness | ⬜ **Not started** | Cloud Director cannot detect file changes or build errors |
| Programmatic Cline injection | ⬜ **Not started** | Cloud Director cannot type commands into the local Cline agent |
| Self-healing circuit breakers | ⬜ **Not started** | No automated rollback or error recovery mechanism |
| Bidirectional callback channel | ⬜ **Not started** | Local factory cannot push status updates to the cloud UI |

---

# 🗺️ The 4-Phase Roadmap to 100% Autonomy

## Phase 1: Cloud-to-Local Bridge ✅ (100% Done)

**Objective:** Establish a secure, zero-middleware communication channel between the Render cloud dashboard and the local factory.

### Deliverables

| Deliverable | Status | Description |
|-------------|--------|-------------|
| GitHub Gist Bulletin Board | ✅ **Done** | Private Gist-based handshake protocol for tunnel URL discovery |
| localtunnel Integration | ✅ **Done** | Automatic tunnel provisioning with `npx localtunnel` |
| API Gateway (port 8000) | ✅ **Done** | Local HTTP server for task ingestion and health checks |
| Task Listener | ✅ **Done** | File-system-based queue polling and execution dispatch |
| Factory Orchestrator | ✅ **Done** | Unified `start_factory.py` with PID-based cleanup |
| Cross-Platform Process Safety | ✅ **Done** | Strict PID-based subprocess management (no image-name killing) |

### Key Architectural Decision

> **Why a Gist instead of a WebSocket relay?** Render's free tier exposes only one public port. A secondary HTTP server behind a second port is impossible without a paid plan. The Gist bulletin board provides a **zero-infrastructure, token-authenticated, decentralized handshake** that costs nothing to maintain.

---

## Phase 2: Command & Control Center 🔄 (In Progress)

**Objective:** Build a parameterized cloud dashboard that allows operators to configure, dispatch, and monitor AI coding missions with full version telemetry.

### Deliverables

| Deliverable | Status | Description |
|-------------|--------|-------------|
| Multi-Model Director Selection | ✅ **Done** | Claude, GPT, Gemini, DeepSeek selector |
| Coder Team Scaling | ✅ **Done** | 1–10 worker slider with role specialization |
| Mission Dispatch Pipeline | ✅ **Done** | `submit_team_mission()` → tunnel → factory |
| Task Dashboard & Report Viewer | ✅ **Done** | Real-time status overview, structured report rendering |
| Debug Version Tagging | ✅ **Done** | UI sidebar version label + browser console telemetry |
| Live Streaming Logs | ⬜ **Next** | Real-time log push from local workshop to cloud UI |
| Pipeline Status Matrix | ⬜ **Next** | Per-stage latency metrics and worker utilization heatmap |

### Current Version

```
App Version: v0.2.0-debug
Commit: 1243729
```

---

## Phase 3: Live Visual Matrix & Callbacks ⬜ (Next)

**Objective:** Inject real-time feedback loops and live streaming logs from the local workshop back to the cloud UI, enabling operators to observe execution as it happens.

### Planned Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  🏭 Local        │     │  📡 Tunnel       │     │  🌐 Cloud UI     │
│  Workshop        │────▶│  (Bidirectional) │────▶│  (Render)        │
│                  │     │                  │     │                  │
│  • Live log      │     │  • WebSocket     │     │  • Real-time     │
│    streaming     │     │    upgrade       │     │    log viewer    │
│  • Status        │     │  • Chunked       │     │  • Pipeline      │
│    heartbeat     │     │    HTTP/2 push   │     │    status matrix │
│  • Report        │     │  • Gist state    │     │  • Latency       │
│    notifications │     │    sync          │     │    metrics       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### Key Challenges

| Challenge | Proposed Solution |
|-----------|-------------------|
| Render's single-port limitation for inbound callbacks | Use the Gist as a **bidirectional state sync** — local factory writes status updates to the Gist; cloud UI polls for changes |
| Real-time log streaming without WebSocket | Implement **Server-Sent Events (SSE)** via the existing tunnel, or use **chunked HTTP transfer encoding** |
| Worker utilization tracking | Instrument `cline_worker.py` with periodic heartbeat writes to a shared state file |

---

## Phase 4: Autonomous Perception & Reverse Hook ⬜ (Ultimate)

**Objective:** Deploy local Agent Runners that allow the Cloud Director AI to **reverse-trigger local execution**, completing the full closed-loop black-box factory.

### The Ultimate Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: FULL AUTONOMOUS LOOP                           │
│                                                                           │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐     │
│   │  🌐 Cloud     │         │  📡 Tunnel   │         │  🏭 Local    │     │
│   │  Director AI  │◀════════▶  (Full-Duplex)│════════▶│  Cline Engine│     │
│   │               │         │              │         │              │     │
│   │  • Perceives  │         │  • State     │         │  • Executes  │     │
│   │    browser    │         │    sync      │         │    code      │     │
│   │    state      │         │  • Command   │         │  • Self-     │     │
│   │  • Detects    │         │    relay     │         │    debugs    │     │
│   │    errors     │         │  • Telemetry │         │  • Reports   │     │
│   │  • Decides    │         │  • Callbacks │         │  • Self-     │     │
│   │    fix        │         │              │         │    heals     │     │
│   └──────┬───────┘         └──────────────┘         └──────┬───────┘     │
│          │                                                  │            │
│          └─────────────────── 🔄 The Loop ──────────────────┘            │
│                                                                           │
│   1. Cloud Director detects build error in local output                   │
│   2. Cloud Director formulates fix command                                │
│   3. Command is injected into local Cline engine via reverse hook         │
│   4. Cline executes fix, writes updated code                              │
│   5. Local factory reports success/failure back to Cloud Director         │
│   6. Loop repeats until task is complete or circuit breaker trips         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Required Capabilities

| Capability | Description | Complexity |
|-----------|-------------|------------|
| **Browser State Perception** | Cloud Director captures screenshots/DOM snapshots from the local browser via the tunnel | 🔴 High |
| **File System Awareness** | Cloud Director monitors file changes, build outputs, and error logs in real time | 🟡 Medium |
| **Programmatic Cline Injection** | Cloud Director sends keystroke-equivalent commands to the local Cline agent process | 🔴 High |
| **Self-Healing Circuit Breaker** | Automatic rollback to last known-good state when an autonomous action fails | 🟡 Medium |
| **Bidirectional State Sync** | Full-duplex communication channel with state reconciliation | 🟢 Low |

---

# 🏗️ Architectural Evolution (The Gist Bulletin Board)

## The Problem: Render's Single-Port Limitation

Render's free-tier web services expose only **one public port** — the one serving the Streamlit dashboard. Running a secondary HTTP server (e.g., the API Gateway on port 8000) behind a second port is impossible without a paid Render plan or an external middleware service.

## The Solution: GitHub Gist Bulletin Board

We bypass this limitation with a **secure, decentralized handshake protocol** using a private GitHub Gist as a lightweight cloud "bulletin board":

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE GIST BULLETIN BOARD PROTOCOL                   │
└─────────────────────────────────────────────────────────────────────┘

  ┌───────────────────┐          ┌───────────────────┐
  │  🏭 Local Factory  │          │  🌐 Render Cloud   │
  │  (Your PC)         │          │  (maneki-ai.onrender.com)
  │                    │          │                    │
  │  1. Start API      │          │                    │
  │     Gateway (8000) │          │                    │
  │                    │          │                    │
  │  2. Start          │          │                    │
  │     localtunnel    │          │                    │
  │     → gets URL     │          │                    │
  │                    │          │                    │
  │  3. Publish URL    │          │                    │
  │     to private     │──────────▶  GitHub Gist       │
  │     Gist via       │          │  (bulletin board)  │
  │     PATCH /gists   │          │                    │
  │                    │          │                    │
  │                    │          │  4. User submits   │
  │                    │          │     task via UI    │
  │                    │          │                    │
  │                    │          │  5. app.py fetches │
  │                    │          │     tunnel URL     │
  │                    │◀─────────│     from Gist      │
  │                    │          │     (GET /gists)   │
  │                    │          │                    │
  │  6. Task POST      │          │                    │
  │     arrives via    │◀─────────│  6. Route task     │
  │     tunnel → API   │          │     through tunnel │
  │     Gateway        │          │     URL            │
  │                    │          │                    │
  │  7. Execute task   │          │                    │
  │  8. Write report   │          │                    │
  └───────────────────┘          └───────────────────┘
```

### Handshake Protocol (Step by Step)

1. **Local Factory Startup** — `start_factory.py` launches the API Gateway (`core/api_gateway.py`) on port 8000 and the Task Listener (`core/task_listener.py`).

2. **Tunnel Provisioning** — `scripts/start_tunnel.py` uses `npx localtunnel` to create a public HTTPS URL pointing to `localhost:8000`.

3. **Gist Publication** — The tunnel URL is written to a **private GitHub Gist** via the GitHub API (`PATCH /gists/{id}`). The Gist contains a simple JSON payload:
   ```json
   {
     "tunnel_url": "https://some-random-name.loca.lt",
     "updated_at": "2026-06-02T16:00:00Z"
   }
   ```

4. **Cloud Discovery** — When a user submits a task through the Render dashboard (`app.py`), the `_fetch_tunnel_url_from_gist()` function reads the Gist (`GET /gists/{id}`) to discover the active tunnel URL.

5. **Task Routing** — The task payload is POSTed through the discovered tunnel URL to the local API Gateway, which queues it in `task_queue/pending/`.

6. **Execution & Reporting** — The Task Listener picks up the task, executes it, writes logs and reports, and moves the task to `task_queue/completed/`.

### Why This Architecture?

| Approach | Drawback | Our Solution |
|----------|----------|--------------|
| Secondary Render port | Paid plan required | ✅ Free GitHub Gist |
| WebSocket relay server | Extra infrastructure to maintain | ✅ Zero middleware |
| ngrok static domain | Paid subscription | ✅ Free localtunnel |
| Direct IP exposure | Security risk | ✅ Private Gist + token auth |

---

# 🎛️ Command & Control Center (Cloud UI Dashboard)

The **Command & Control Center** is deployed at **[https://maneki-ai.onrender.com/](https://maneki-ai.onrender.com/)** and provides a full mission-control interface for orchestrating AI coding teams.

### Interface Pages

| Page | Function |
|------|----------|
| 🎮 **Command & Control Center** | Configure and launch AI coding teams with multi-director selection, coder scaling, and role specialization |
| 📋 **Submit Task** | Legacy single-task submission form for direct script execution |
| 📊 **Task Dashboard** | Real-time status overview of all tasks (PENDING / PROCESSING / SUCCESS / FAILED) |
| 📄 **Execution Report** | Detailed execution logs and structured JSON reports for completed tasks |

### Input Controls

#### 🧠 Multi-Director Selection

Choose the AI model that will act as the **Director** — responsible for decomposing user requirements, assigning tasks to coders, and reviewing output:

| Director Model | Description |
|----------------|-------------|
| **Claude 3.5 Sonnet** (default) | Balanced reasoning & code generation |
| **Claude 4 Opus** | Maximum capability for complex missions |
| **GPT-4o** | OpenAI's multimodal flagship |
| **Gemini 2.5 Pro** | Google's latest reasoning model |
| **DeepSeek-V3** | Open-weight high-performance alternative |

#### 👨‍💻 Coder Team Scaling

Scale your AI coding workforce from **1 to 10 parallel workers** using the slider control. More workers = higher parallelism for large-scale code generation tasks.

#### 🛠️ Multi-Role Specialized Configurations

Assign specific professional roles to your coder team via multi-select:

- Frontend Developer
- Backend Developer
- Full-Stack Developer
- DevOps Engineer
- Data Engineer
- Security Engineer
- QA / Test Engineer
- UI/UX Designer

### Task Lifecycle

```
User Input → submit_team_mission() → task_queue/pending/ → tunnel POST → API Gateway → task_queue/pending/ (local)
    → Task Listener picks up → processing/ → execute → logs/ → completed/
```

---

# 🛡️ Production Safeguards & Process Reliability

## ⚠️ CRITICAL RULE: NEVER Use Generic Image-Name Killing

This is the **most important operational rule** in the Maneki-AI project:

```diff
- ❌ taskkill /F /IM node.exe       ← ABSOLUTELY FORBIDDEN
- ❌ taskkill /F /IM python.exe     ← ABSOLUTELY FORBIDDEN
+ ✅ taskkill /F /T /PID <PID>      ← ALWAYS use PID-based termination
```

### Why?

On Windows, `taskkill /F /IM node.exe` kills **every** `node.exe` process on the system — including the **VS Code Extension Host** that runs the Cline agent engine. This causes:

- The Cline agent to disconnect mid-task
- The extension host to crash
- Loss of all in-progress work
- A hard-to-diagnose "friendly fire" bug

### Our Strict PID-Based Protocol

All subprocess management in Maneki-AI follows this strict protocol:

```python
# From start_factory.py — cleanup() function
for name, proc in processes:
    if proc.poll() is None:
        print(f"Stopping {name} (PID {proc.pid})...")
        if sys.platform == "win32":
            # PID-based process tree termination — safe, no friendly fire
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            os.kill(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5)
```

| Principle | Implementation |
|-----------|----------------|
| **PID Tracking** | Every subprocess is created via `subprocess.Popen()` and its `.pid` is recorded |
| **Process Tree Termination** | `/T` flag kills the entire process tree rooted at the tracked PID |
| **Graceful Shutdown** | `SIGTERM` on Unix, `taskkill /F` on Windows, with 5-second timeout |
| **Orphan Cleanup** | If a tunnel fails to start, the orphaned process is killed by PID — never by image name |
| **Cross-Platform** | `os.kill()` on Unix, `taskkill /PID` on Windows — both target specific PIDs |

### Continuous Uptime Guarantee

This protocol ensures **both** the extension engine (VS Code / Cline) and the local listener remain online through all factory start/stop/restart cycles.

---

# 🎛️ Telemetry & Versioning Standard

## Mandatory Debug Version Tagging

Every deployment **must** include explicit version identification to enable operators to verify which build is active on the target environment. This is a **non-negotiable production standard**.

### UI Sidebar Version Label

The sidebar footer renders a visible version tag using `st.caption()`:

```
App Version: v0.2.0-debug
Commit: 1243729
```

**Implementation** (`app.py`):

```python
APP_VERSION = "v0.2.0-debug"
APP_COMMIT = os.environ.get("MANEKI_COMMIT_HASH", "1243729")

# In sidebar:
st.caption(
    f"**App Version:** {APP_VERSION}  \n"
    f"**Commit:** `{APP_COMMIT}`"
)
```

### Browser Console Telemetry

A JavaScript snippet is injected into every page load to print the active version to the browser's developer console:

```javascript
console.log("=== Maneki-AI Factory Control Loaded: v0.2.0-debug (Commit: 1243729) ===");
```

**How to verify:**

1. Open the deployed application in Chrome
2. Press `F12` → **Console** tab
3. Look for the `=== Maneki-AI Factory Control Loaded:` log entry
4. Confirm the version and commit hash match the expected deployment

### Version Bump Protocol

| Action | When | How |
|--------|------|-----|
| **Bump `APP_VERSION`** | Every deployment with functional changes | Update the `APP_VERSION` constant in `app.py` |
| **Update `APP_COMMIT`** | Automatically via CI/CD | Set `MANEKI_COMMIT_HASH` environment variable at build time |
| **Verify on Render** | After each deployment | Check sidebar label + browser console log |

---

# 📋 Required Environment Variables

## Local Factory (`.env` file in project root)

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_TOKEN` | ✅ **Yes** | GitHub Personal Access Token with `gist` scope. Used by `start_tunnel.py` and `start_factory.py` to publish the tunnel URL to the private Gist bulletin board. |
| `MANEKI_TUNNEL_GIST_ID` | ✅ **Yes** | The ID of the private GitHub Gist used as the cloud bulletin board. Created automatically on first run; set this to reuse an existing Gist. |
| `MANEKI_ENABLE_TUNNEL` | ❌ No (default: `1`) | Set to `0` to disable automatic tunnel provisioning (for local-only development). |
| `MANEKI_TUNNEL_PORT` | ❌ No (default: `8000`) | The local port to tunnel. |
| `MANEKI_TUNNEL_SUBDOMAIN` | ❌ No | Request a specific localtunnel subdomain. |
| `N8N_CALLBACK_URL` | ❌ No | Optional outbound callback URL for n8n webhook integration. |

### Setting Up `GITHUB_TOKEN`

1. Go to **GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **"Generate new token"**
3. Set **Repository access** to "Only select repositories" → select your repo
4. Under **Permissions → Account permissions**, enable **"Gists"** with **"Read and write"** access
5. Generate the token and copy it
6. Add to your `.env` file:
   ```bash
   GITHUB_TOKEN=github_pat_xxxxxxxxxxxx
   ```

### Setting Up `MANEKI_TUNNEL_GIST_ID`

1. Create a **private** Gist on GitHub with filename `maneki_tunnel_url.json`
2. Copy the Gist ID from the URL: `https://gist.github.com/yourname/`**`THIS_IS_THE_GIST_ID`**
3. Add to your `.env` file:
   ```bash
   MANEKI_TUNNEL_GIST_ID=your_gist_id_here
   ```

> **Note:** If `MANEKI_TUNNEL_GIST_ID` is not set, the factory will create a new Gist on first startup and print the ID to the console.

## Render Dashboard (Environment Variables)

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_TOKEN` | ✅ **Yes** | Same token as above. Used by `app.py` to authenticate when fetching the tunnel URL from the Gist. |
| `MANEKI_TUNNEL_GIST_ID` | ✅ **Yes** | Same Gist ID as above. Tells `app.py` which Gist to read for the tunnel URL. |
| `API_GATEWAY_URL` | ❌ No (fallback) | Static fallback URL if the Gist is unreachable. Default: `http://localhost:8000` |

### Setting Up Render Environment Variables

1. Go to your Render dashboard → **Environment**
2. Add the following:
   ```
   GITHUB_TOKEN=github_pat_xxxxxxxxxxxx
   MANEKI_TUNNEL_GIST_ID=your_gist_id_here
   ```
3. Deploy or restart the service

---

# 🏁 Quick Start

### Prerequisites

- Python 3.12+
- Node.js (for `npx localtunnel`)
- A GitHub account (for the Gist bulletin board)

### 1. Clone & Install

```bash
git clone https://github.com/winsentrobot008/Maneki-AI.git
cd Maneki-AI
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your GITHUB_TOKEN and MANEKI_TUNNEL_GIST_ID
```

### 3. Start the Local Factory

```bash
python start_factory.py
```

This launches:
- ✅ API Gateway on `http://localhost:8000`
- ✅ Task Listener polling `task_queue/pending/`
- ✅ Local tunnel (public HTTPS URL published to Gist)

### 4. Open the Cloud Dashboard

Navigate to **[https://maneki-ai.onrender.com/](https://maneki-ai.onrender.com/)** and start dispatching missions!

### 5. (Optional) Start Tunnel Only

```bash
python scripts/start_tunnel.py --port 8000
```

---

# 🚀 CI/CD Deployment Pipeline

## Standard Operational Protocol

The Maneki-AI deployment chain follows a strict **3-step continuous workflow**:

```
git commit  →  git push  →  python scripts/trigger_deploy.py
```

### Step-by-Step

| Step | Command | Description |
|------|---------|-------------|
| **1. Commit** | `git add . && git commit -m "message"` | Stage and commit your changes locally |
| **2. Push** | `git push origin main` | Push commits to GitHub (Render auto-detects changes) |
| **3. Deploy** | `python scripts/trigger_deploy.py` | Fire the Render Deploy Hook to trigger an immediate deployment |

### The Trigger Script

`scripts/trigger_deploy.py` is a zero-dependency Python script that:

1. Reads `RENDER_DEPLOY_HOOK` from the environment (set in `.env`)
2. Sends a **POST** request to Render's deploy hook API
3. Prints the HTTP response status code for verification

```bash
# Example output:
🚀 [Maneki-AI] Sending trigger pulse to Render...
✅ [Maneki-AI] Render responded with HTTP 200
🎯 [Maneki-AI] Deployment triggered successfully!
```

### Environment Setup

The deploy hook URL is stored **only** in the local `.env` file:

```bash
# .env (LOCAL ONLY — never committed to GitHub)
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-d8bjvjsm0tmc73dgnh70?key=rlWA0Q8ca4w
```

> ⚠️ **Security:** `.env` is listed in `.gitignore` and will **never** be pushed to GitHub. The deploy hook key is a sensitive credential.

### Verification

After triggering a deployment:

1. Check the terminal output for `HTTP 200` / `HTTP 202` success status
2. Visit **[https://dashboard.render.com](https://dashboard.render.com)** to monitor the live build progress
3. Once complete, verify the updated dashboard at **[https://maneki-ai.onrender.com/](https://maneki-ai.onrender.com/)**

---

# 📁 Project Structure

```
Maneki-AI/
├── app.py                      # Streamlit cloud dashboard (Render entry point)
├── start_factory.py            # Local factory orchestrator (API + Listener + Tunnel)
├── render.yaml                 # Render deployment configuration
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python runtime version
├── .env.example                # Environment variable template
├── .clinerules                 # Cline agent operational rules
│
├── core/
│   ├── api_gateway.py          # HTTP API Gateway (port 8000)
│   └── task_listener.py        # Task queue poller & executor
│
├── scripts/
│   ├── start_tunnel.py         # localtunnel provisioner + Gist publisher
│   ├── test_factory_startup.py # Factory startup test suite
│   └── example_worker.py       # Example worker script
│
├── agents/
│   └── orchestrator.py         # AI Director orchestration logic
│
├── agent_engine/               # Agent-S integration layer
│   ├── bridge.py               # Flask bridge server (port 5005)
│   ├── cline_daemon.py         # Cline daemon with forbidden pattern safety
│   ├── cline_worker.py         # Cline worker polling bridge queue
│   ├── app_ready.py            # Agent readiness check
│   ├── send_task.py            # Task submission helper
│   └── safety/                 # Safety rules & forbidden patterns
│
├── task_queue/
│   ├── pending/                # Tasks awaiting execution
│   ├── processing/             # Tasks currently being executed
│   └── completed/              # Finished tasks
│
├── logs/                       # Execution logs & status reports
│
├── config/
│   ├── env.template            # Environment template
│   └── settings.yaml           # Application settings
│
├── state/
│   └── ama_state.json          # Agent state persistence
│
├── docs/
│   ├── PROJECT_OVERVIEW.md     # Original project overview (Chinese)
│   └── WEB_ARCHITECTURE.md     # Web frontend architecture docs
│
└── deliveries/                 # Task delivery artifacts
```

---

<p align="center">
  <strong>Maneki-AI</strong> — Bringing Good Fortune to Your AI Factory 🐱
</p>
<p align="center">
  <sub>Built with ❤️ for the Hybrid Cloud AI Era</sub>
  <br>
  <sub>v0.2.0-debug · Commit <code>1243729</code></sub>
</p>
