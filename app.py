"""
app.py — Maneki-AI 招财猫任务控制台 (Render Deployment Entry)

A Streamlit single-page application deployed at https://maneki-ai.onrender.com/.

Provides:
  1. Task Submission — user submits a task → status "PENDING"
  2. Task Dashboard — real-time status overview of all tasks
  3. Report Viewer — dynamic rendering of execution logs & reports

Data is stored as lightweight JSON files in task_queue/ and logs/.
No external database required.

Tunnel Discovery:
  The local factory publishes its active localtunnel URL to a private GitHub
  Gist (the "cloud bulletin board").  When submit_task() runs, it fetches the
  tunnel URL from this Gist and routes the task submission through the tunnel
  to the local API gateway — bypassing Render's single-port limitation.
"""

import os
import sys
import json
import glob
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

import streamlit as st

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PENDING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "pending")
PROCESSING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "processing")
COMPLETED_DIR = os.path.join(PROJECT_ROOT, "task_queue", "completed")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")

# ── Cloud Bulletin Board (GitHub Gist) ─────────────────────────────────────
# The tunnel URL is published to a private GitHub Gist by the local factory.
# We fetch it dynamically when routing task submissions, falling back to the
# static API_GATEWAY_URL env-var if the Gist is unreachable or unset.

GIST_API_BASE = "https://api.github.com/gists"
GIST_FILENAME = "maneki_tunnel_url.json"
GIST_ID = os.environ.get("MANEKI_TUNNEL_GIST_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# In-memory cache for the tunnel URL (refreshed on each submit_task call)
_tunnel_gateway_url: str | None = None


# ── Helpers ────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_dirs():
    for d in [PENDING_DIR, PROCESSING_DIR, COMPLETED_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)


def _gateway_healthy() -> bool:
    try:
        req = Request(f"{API_GATEWAY_URL}/api/health", method="GET")
        resp = urlopen(req, timeout=2)
        return resp.status == 200
    except (URLError, OSError):
        return False


# ── Tunnel Gateway Discovery (GitHub Gist) ─────────────────────────────────
# Instead of an embedded HTTP server on a secondary port (which Render blocks),
# we use a private GitHub Gist as a lightweight cloud "bulletin board".
# The local factory writes the tunnel URL to the Gist; we read it here.

def _fetch_tunnel_url_from_gist() -> str | None:
    """
    Fetch the active tunnel URL from the GitHub Gist bulletin board.

    Returns the tunnel URL string, or None if the Gist is unreachable,
    unconfigured, or contains no valid URL.
    """
    if not GIST_ID:
        return None

    url = f"{GIST_API_BASE}/{GIST_ID}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Maneki-AI/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        req = Request(url, headers=headers, method="GET")
        resp = urlopen(req, timeout=10)
        resp_data = json.loads(resp.read().decode("utf-8"))
        resp.close()

        files = resp_data.get("files", {})
        gist_file = files.get(GIST_FILENAME, {})
        content = gist_file.get("content", "")

        if content:
            data = json.loads(content)
            tunnel_url = data.get("tunnel_url", "")
            if tunnel_url:
                return tunnel_url
    except (URLError, json.JSONDecodeError, OSError) as e:
        print(f"[app] ⚠️  Failed to fetch tunnel URL from Gist: {e}", file=sys.stderr)

    return None


def _get_active_gateway_url() -> str:
    """
    Return the tunnel gateway URL if available, else the static env-var.

    The tunnel URL is fetched from the GitHub Gist bulletin board on every
    call, ensuring we always use the most recently published tunnel address.
    """
    global _tunnel_gateway_url

    # Try fetching from Gist first
    gist_url = _fetch_tunnel_url_from_gist()
    if gist_url:
        _tunnel_gateway_url = gist_url
        return gist_url

    # Fall back to in-memory cache (from a previous successful fetch)
    if _tunnel_gateway_url:
        return _tunnel_gateway_url

    # Final fallback: static env-var
    return API_GATEWAY_URL


# ── Data Store Interface ───────────────────────────────────────────────────
# Lightweight file-based store. Each task is a JSON file.
# Schema:
#   {
#     "task_id":     str  — unique identifier
#     "status":      str  — PENDING | PROCESSING | SUCCESS | FAILED
#     "parameters":  dict — script_name, description, etc.
#     "result_log":  str  — path to logs/task_[id]_report.json
#     "created_at":  str  — ISO-8601
#     "updated_at":  str  — ISO-8601
#   }

def submit_task(task_id: str, script_name: str, extra_params: dict = None) -> dict:
    """
    Submit a new task. Writes to task_queue/pending/ with status PENDING
    and best-effort POST to the API Gateway via the tunnel.
    """
    _ensure_dirs()
    now = _now_iso()
    payload = {
        "task_id": task_id,
        "status": "PENDING",
        "parameters": {
            "script_name": script_name,
            **(extra_params or {}),
        },
        "result_log": None,
        "created_at": now,
        "updated_at": now,
    }

    # Write to pending queue
    pending_path = os.path.join(PENDING_DIR, f"task_{task_id}.json")
    try:
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except IOError as e:
        return {"success": False, "task_id": task_id, "status": "ERROR",
                "message": f"Failed to write task file: {e}"}

    # Best-effort POST to the active gateway (tunnel URL from Gist if
    # available, otherwise the static API_GATEWAY_URL env-var).
    active_gateway = _get_active_gateway_url()
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(f"{active_gateway}/api/task", data=data,
                      headers={"Content-Type": "application/json"}, method="POST")
        urlopen(req, timeout=5)
    except (URLError, OSError):
        pass

    return {"success": True, "task_id": task_id, "status": "PENDING",
            "message": f"Task {task_id} submitted. Status set to PENDING."}


# ── Command & Control Mission Dispatch ────────────────────────────────────
# Wires the C&C Center UI inputs into the task submission pipeline.
# Harvests user_demand, ai_director, coder_count, and coder_roles from the
# UI, bundles them into a structured payload, and dispatches it through the
# tunnel gateway to the local factory.

def submit_team_mission(
    user_demand: str,
    ai_director: str,
    coder_count: int,
    coder_roles: list[str],
) -> dict:
    """
    Dispatch a team mission from the Command & Control Center.

    Builds a task payload with the C&C inputs, writes it to the pending
    queue, and best-effort POSTs it to the active factory gateway via the
    tunnel (discovered dynamically from the GitHub Gist bulletin board).
    """
    _ensure_dirs()
    now = _now_iso()
    task_id = f"MISSION_{_now_iso()[:10].replace('-','')}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

    payload = {
        "task_id": task_id,
        "status": "PENDING",
        "parameters": {
            "script_name": "agents/orchestrator.py",
            "user_demand": user_demand,
            "ai_director": ai_director,
            "coder_count": coder_count,
            "coder_roles": coder_roles,
        },
        "result_log": None,
        "created_at": now,
        "updated_at": now,
    }

    # Write to pending queue
    pending_path = os.path.join(PENDING_DIR, f"task_{task_id}.json")
    try:
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except IOError as e:
        return {"success": False, "task_id": task_id, "status": "ERROR",
                "message": f"Failed to write mission file: {e}"}

    # Best-effort POST to the active gateway via tunnel discovery
    active_gateway = _get_active_gateway_url()
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(f"{active_gateway}/api/task", data=data,
                      headers={"Content-Type": "application/json"}, method="POST")
        urlopen(req, timeout=5)
    except (URLError, OSError):
        pass

    return {"success": True, "task_id": task_id, "status": "PENDING",
            "message": f"Mission {task_id} dispatched to factory."}


def list_all_tasks() -> list[dict]:
    """Aggregate all tasks from all queues and logs."""
    _ensure_dirs()
    tasks: dict[str, dict] = {}

    def _ingest(filepath: str, inferred_status: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        tid = data.get("task_id", os.path.basename(filepath).replace(".json", ""))
        tasks[tid] = {
            "task_id": tid,
            "status": data.get("status", inferred_status),
            "parameters": data.get("parameters", {}),
            "result_log": data.get("result_log", None),
            "created_at": data.get("created_at", data.get("timestamp", "")),
            "updated_at": data.get("updated_at", data.get("timestamp", "")),
        }

    for fp in glob.glob(os.path.join(PENDING_DIR, "*.json")):
        _ingest(fp, "PENDING")
    for fp in glob.glob(os.path.join(PROCESSING_DIR, "*.json")):
        _ingest(fp, "PROCESSING")
    for fp in glob.glob(os.path.join(COMPLETED_DIR, "*.json")):
        _ingest(fp, "COMPLETED")
    for fp in glob.glob(os.path.join(LOGS_DIR, "*_report.json")):
        _ingest(fp, "UNKNOWN")

    return list(tasks.values())


def read_task_report(task_id: str) -> dict | None:
    """Read logs/task_[task_id]_report.json."""
    path = os.path.join(LOGS_DIR, f"task_{task_id}_report.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def read_task_log(task_id: str) -> str | None:
    """Read logs/task_[task_id].log."""
    path = os.path.join(LOGS_DIR, f"task_{task_id}.log")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return None


# ── Page: Command & Control Center ─────────────────────────────────────────
# Phase 5 UI — Frontend-only input controls. Backend orchestration wiring
# will be added in a subsequent step.

def page_command_center():
    st.header("🎮 Command & Control Center")
    st.markdown("配置并启动 AI 编码团队，执行你的开发需求。")

    # ── User Demand ────────────────────────────────────────────────────────
    user_demand = st.text_area(
        "📝 用户需求 (User Demand)",
        value="",
        height=150,
        placeholder="描述你想要实现的功能或修复的问题…",
        help="输入自然语言描述的需求，AI 团队将据此生成代码。",
    )

    st.divider()

    # ── AI Director Selection ──────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        ai_director = st.selectbox(
            "🧠 AI 主管 (AI Director)",
            options=[
                "Claude 3.5 Sonnet (default)",
                "Claude 4 Opus",
                "GPT-4o",
                "Gemini 2.5 Pro",
                "DeepSeek-V3",
            ],
            index=0,
            help="选择负责拆解需求、分配任务、审查代码的 AI 主管模型。",
        )

    with col_right:
        coder_quantity = st.slider(
            "👨‍💻 编码员数量 (Coder Quantity)",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="并行工作的 AI 编码员数量。数量越多，任务并行度越高。",
        )

    st.divider()

    # ── Coder Roles (Multi-Select) ─────────────────────────────────────────
    coder_roles = st.multiselect(
        "🛠️ 编码员角色 (Coder Roles)",
        options=[
            "Frontend Developer",
            "Backend Developer",
            "Full-Stack Developer",
            "DevOps Engineer",
            "Data Engineer",
            "Security Engineer",
            "QA / Test Engineer",
            "UI/UX Designer",
        ],
        default=["Frontend Developer", "Backend Developer"],
        help="选择编码员的专业角色。每个角色将专注于其擅长的领域。",
    )

    # ── Launch Team Button (wired to factory dispatch) ─────────────────────
    st.divider()
    launch_col1, launch_col2 = st.columns([3, 1])
    with launch_col2:
        launch_disabled = not (user_demand.strip() and coder_roles)
        launch_clicked = st.button(
            "🚀 启动团队",
            type="primary",
            use_container_width=True,
            disabled=launch_disabled,
            help="将当前配置打包为任务，通过隧道发送到本地工厂执行。",
        )

    # Handle launch — harvest all UI inputs and dispatch
    if launch_clicked:
        with st.spinner("正在编排 AI 团队并发送任务到工厂..."):
            result = submit_team_mission(
                user_demand=user_demand.strip(),
                ai_director=ai_director,
                coder_count=coder_quantity,
                coder_roles=coder_roles,
            )

        if result["success"]:
            st.success(f"✅ **{result['message']}**")
            st.info(f"任务 **{result['task_id']}** 已写入待处理队列，"
                    f"状态: **{result['status']}**。工厂将通过隧道接收并执行。")
            # Show the dispatched payload for transparency
            with st.expander("📦 已发送的任务载荷", expanded=True):
                st.json({
                    "task_id": result["task_id"],
                    "user_demand": user_demand.strip(),
                    "ai_director": ai_director,
                    "coder_count": coder_quantity,
                    "coder_roles": coder_roles,
                })
        else:
            st.error(f"❌ 调度失败: {result['message']}")

    # Preview panel (read-only summary of current config)
    with st.expander("📋 当前配置预览", expanded=False):
        preview = {
            "需求摘要": user_demand[:80] + "..." if len(user_demand) > 80 else user_demand,
            "AI 主管": ai_director,
            "编码员数量": coder_quantity,
            "编码员角色": coder_roles,
        }
        st.json(preview)


# ── Page: Submit Task ──────────────────────────────────────────────────────

def page_submit_task():
    st.header("📋 提交新任务")
    st.markdown("填写表单以向 Maneki-AI 工厂提交一个新的执行任务。")

    with st.form("task_submit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_id = st.text_input(
                "任务 ID",
                value=f"TASK_{_now_iso()[:10].replace('-','')}_{datetime.now(timezone.utc).strftime('%H%M%S')}",
                help="唯一任务标识符。自动生成，可手动修改。")
            script_name = st.text_input(
                "脚本名称", value="scripts/example_worker.py",
                help="相对于项目根目录的脚本路径。")
        with col2:
            extra_raw = st.text_area(
                "额外参数 (JSON)", value='{\n  "description": "Example task"\n}',
                height=120, help="可选的 JSON 格式额外参数。")

        submitted = st.form_submit_button("🚀 提交任务", type="primary",
                                          use_container_width=True)

    if submitted:
        if not task_id.strip():
            st.error("任务 ID 不能为空。")
            return
        if not script_name.strip():
            st.error("脚本名称不能为空。")
            return
        extra_params = {}
        if extra_raw.strip():
            try:
                extra_params = json.loads(extra_raw)
            except json.JSONDecodeError as e:
                st.error(f"额外参数 JSON 格式错误: {e}")
                return

        with st.spinner(f"正在提交任务 {task_id} ..."):
            result = submit_task(task_id, script_name.strip(), extra_params)

        if result["success"]:
            st.success(f"✅ **{result['message']}**")
            st.info(f"任务状态已设置为 **{result['status']}**，等待工厂处理。")
        else:
            st.error(f"❌ 提交失败: {result['message']}")

    # Recent submissions
    st.divider()
    st.subheader("最近提交的任务")
    all_tasks = list_all_tasks()
    if all_tasks:
        for t in sorted(all_tasks, key=lambda x: x.get("created_at", ""),
                        reverse=True)[:5]:
            emoji = {"PENDING": "⏳", "PROCESSING": "🔄", "SUCCESS": "✅",
                     "FAILED": "❌", "COMPLETED": "📦"}.get(t["status"], "❓")
            st.markdown(f"{emoji} **{t['task_id']}** — `{t['status']}` "
                        f"({t.get('created_at', 'N/A')})")
    else:
        st.info("暂无任务记录。")


# ── Page: Task Dashboard ───────────────────────────────────────────────────

def page_task_dashboard():
    st.header("📊 任务看板")
    st.markdown("所有任务的实时状态概览。")

    all_tasks = list_all_tasks()
    if not all_tasks:
        st.info("暂无任务。请前往「提交任务」页面创建新任务。")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    statuses = [t["status"] for t in all_tasks]
    col1.metric("总任务数", len(all_tasks))
    col2.metric("待处理", statuses.count("PENDING"))
    col3.metric("处理中", statuses.count("PROCESSING"))
    col4.metric("已完成", statuses.count("SUCCESS") + statuses.count("COMPLETED"))

    st.divider()

    # Filter
    filter_status = st.selectbox(
        "按状态筛选",
        ["全部", "PENDING", "PROCESSING", "SUCCESS", "FAILED", "COMPLETED"])
    filtered = all_tasks if filter_status == "全部" else \
        [t for t in all_tasks if t["status"] == filter_status]

    # Task list
    for task in sorted(filtered, key=lambda t: t.get("created_at", ""),
                       reverse=True):
        emoji = {"PENDING": "⏳", "PROCESSING": "🔄", "SUCCESS": "✅",
                 "FAILED": "❌", "COMPLETED": "📦", "NOT_FOUND": "🔍"}.get(
                     task["status"], "❓")
        with st.expander(f"{emoji} **{task['task_id']}** — `{task['status']}`",
                         expanded=False):
            cols = st.columns([1, 2])
            with cols[0]:
                st.markdown(f"**状态**: `{task['status']}`")
                st.markdown(f"**创建时间**: {task.get('created_at', 'N/A')}")
                st.markdown(f"**更新时间**: {task.get('updated_at', 'N/A')}")
            with cols[1]:
                if task.get("parameters"):
                    st.markdown("**参数**:")
                    st.json(task["parameters"])
                if task.get("result_log"):
                    st.markdown(f"**报告文件**: `{task['result_log']}`")

            if task["status"] in ("SUCCESS", "FAILED", "COMPLETED"):
                if st.button("📄 查看执行报告",
                             key=f"view_{task['task_id']}"):
                    st.session_state["view_task_id"] = task["task_id"]
                    st.session_state["nav_page"] = "📄 执行报告"
                    st.rerun()


# ── Page: Report Viewer ────────────────────────────────────────────────────

def page_report_viewer():
    st.header("📄 执行报告")
    st.markdown("查看任务的详细执行日志和结构化报告。")

    all_tasks = list_all_tasks()
    completed = [t for t in all_tasks
                 if t["status"] in ("SUCCESS", "FAILED", "COMPLETED")]
    if not completed:
        st.info("暂无已完成的任务报告。")
        return

    task_opts = {t["task_id"]: t for t in completed}
    default = st.session_state.get("view_task_id", list(task_opts.keys())[0])
    idx = list(task_opts.keys()).index(default) if default in task_opts else 0
    selected = st.selectbox("选择任务", options=list(task_opts.keys()), index=idx)
    if not selected:
        return

    # Structured report
    report = read_task_report(selected)
    if report:
        st.subheader("📋 结构化报告")
        c1, c2, c3 = st.columns(3)
        icon = "✅" if report.get("status") == "SUCCESS" else "❌"
        c1.metric("状态", f"{icon} {report.get('status', 'UNKNOWN')}")
        c2.metric("任务 ID", report.get("task_id", "N/A"))
        c3.metric("时间戳", report.get("timestamp", "N/A"))
        with st.expander("查看完整报告 JSON", expanded=False):
            st.json(report)
    else:
        st.warning(f"未找到任务 {selected} 的结构化报告。")

    st.divider()

    # Execution log
    log_content = read_task_log(selected)
    if log_content:
        st.subheader("📜 执行日志")
        st.text_area("日志内容", value=log_content, height=400,
                     disabled=True, label_visibility="collapsed")
        st.download_button("⬇️ 下载日志文件", data=log_content,
                           file_name=f"task_{selected}.log", mime="text/plain")
    else:
        st.info(f"未找到任务 {selected} 的详细执行日志。")

    st.caption(f"日志路径: `logs/task_{selected}.log`  |  "
               f"报告路径: `logs/task_{selected}_report.json`")


# ── Main App ───────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Maneki-AI 招财猫任务控制台",
                       page_icon="🐱", layout="wide",
                       initial_sidebar_state="expanded")

    # Sidebar
    with st.sidebar:
        st.markdown("## 🐱 Maneki-AI")
        st.markdown("**招财猫任务工厂**")
        st.divider()
        page = st.radio("导航", ["🎮 Command & Control Center",
                                 "📋 提交任务", "📊 任务看板", "📄 执行报告"],
                        label_visibility="collapsed")
        st.divider()
        st.caption("系统状态")
        st.markdown("🟢 **API Gateway** — 在线" if _gateway_healthy()
                    else "🔴 **API Gateway** — 离线")
        st.divider()
        st.caption(f"v1.0.0 · {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")

    # Handle cross-page navigation
    if st.session_state.get("nav_page"):
        page = st.session_state["nav_page"]
        st.session_state["nav_page"] = None

    # Route to page
    if page == "🎮 Command & Control Center":
        page_command_center()
    elif page == "📋 提交任务":
        page_submit_task()
    elif page == "📊 任务看板":
        page_task_dashboard()
    elif page == "📄 执行报告":
        page_report_viewer()


if __name__ == "__main__":
    main()
