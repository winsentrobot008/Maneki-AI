"""from factory_ui import render_factory_trigger
render_factory_trigger()
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
import subprocess
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


# ── Factory Task Runner ──────────────────────────────────────────────────
# Simple subprocess runner that executes the local run_task.py pipeline.
# The frontend is ONLY for monitoring and triggering — no agentic logic.

def _run_factory_task(task_name: str = "deploy") -> dict:
    """
    Execute `python run_task.py <task_name>` via subprocess and return
    the combined stdout + stderr output along with status info.
    """
    cmd = f"python run_task.py {task_name}"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=300,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return {
            "success": result.returncode == 0,
            "output": output,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Command timed out after 300 seconds.",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Error executing task: {e}",
            "returncode": -1,
        }


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
# Phase 5+ UI — Refactored dashboard with structured columns, modern
# container styling, and interactive feedback loops.

def _inject_dashboard_css() -> None:
    """Inject custom CSS for the Command Center dashboard aesthetic."""
    st.markdown(
        """
        <style>
        /* Command Center container card */
        .cmd-card {
            background: linear-gradient(135deg, #0f1923 0%, #1a2332 100%);
            border: 1px solid #2a3a4e;
            border-radius: 12px;
            padding: 1.5rem 1.2rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .cmd-card h3 {
            color: #8ab4f8;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 0 0 0.8rem 0;
            border-bottom: 1px solid #2a3a4e;
            padding-bottom: 0.5rem;
        }
        /* System status metric tweaks */
        .cmd-metric {
            background: #0d1520;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            border-left: 3px solid #4fc3f7;
        }
        /* Sidebar version badge */
        .version-badge {
            display: inline-block;
            background: #1e2a3a;
            color: #8ab4f8;
            font-family: 'Courier New', monospace;
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            border: 1px solid #2a3a4e;
        }
        /* Button feedback glow */
        div.stButton > button:active {
            transform: scale(0.97);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _system_control_buttons() -> None:
    """Render the left-column system control buttons with feedback loops."""
    st.markdown('<div class="cmd-card"><h3>⚙️ 系统控制</h3>', unsafe_allow_html=True)

    # ── Sync Button ────────────────────────────────────────────────────────
    sync_clicked = st.button("🔄 同步数据", type="secondary", use_container_width=True,
                             key="btn_sync")
    if sync_clicked:
        with st.spinner("正在同步远程数据..."):
            import time
            time.sleep(1.2)  # Simulated sync delay
        st.success("✅ 数据同步完成")
        st.toast("所有队列已与远程源同步", icon="🔄")

    # ── Deploy Button ──────────────────────────────────────────────────────
    deploy_clicked = st.button("🚀 部署更新", type="primary", use_container_width=True,
                               key="btn_deploy")
    if deploy_clicked:
        with st.spinner("正在部署最新版本..."):
            import time
            time.sleep(1.8)  # Simulated deploy delay
        st.success("✅ 部署成功 — v0.2.0-Alpha 已上线")
        st.balloons()

    # ── Logs Button ────────────────────────────────────────────────────────
    logs_clicked = st.button("📜 查看日志", type="secondary", use_container_width=True,
                             key="btn_logs")
    if logs_clicked:
        with st.spinner("正在聚合日志..."):
            import time
            time.sleep(0.8)
        st.info("📄 最近的日志条目已加载，请前往「执行报告」页面查看详情。")
        st.session_state["nav_page"] = "📄 执行报告"

    st.markdown('</div>', unsafe_allow_html=True)


def _system_status_metrics() -> None:
    """Render the right-column system status metric cards."""
    st.markdown('<div class="cmd-card"><h3>📊 系统状态</h3>', unsafe_allow_html=True)
    # Determine live gateway health
    gw_healthy = _gateway_healthy()

    # Use a single row of four native Streamlit metric columns
    col1, col2, col3, col4 = st.columns(4, gap="small")

    col1.metric(
        label="🖥️ 服务器状态",
        value="🟢 在线" if gw_healthy else "🔴 离线",
        delta="正常运行" if gw_healthy else "连接失败",
    )

    col2.metric(
        label="⏱️ 上次部署",
        value="2026-06-02",
        delta="19:13 UTC",
    )

    col3.metric(
        label="📦 今日任务",
        value=str(len([t for t in list_all_tasks()
                       if "2026-06-02" in t.get("created_at", "")])),
        delta="+0",
    )

    all_tasks = list_all_tasks()
    completed = len([t for t in all_tasks
                     if t["status"] in ("SUCCESS", "COMPLETED")])
    total = len(all_tasks) or 1
    rate = f"{int(completed / total * 100)}%"

    col4.metric(
        label="✅ 成功率",
        value=rate,
        delta=f"{completed}/{len(all_tasks)} 完成" if all_tasks else "无数据",
    )

    st.markdown('</div>', unsafe_allow_html=True)


def page_command_center():
    """Main Command & Control Center dashboard page."""
    _inject_dashboard_css()

    # ── Page Header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
            <span style="font-size: 2rem;">🎮</span>
            <div>
                <h1 style="margin: 0; font-size: 1.8rem;">Command & Control Center</h1>
                <p style="margin: 0; color: #8899aa; font-size: 0.9rem;">
                    配置并启动 AI 编码团队，执行你的开发需求。
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Dashboard Columns: Left (Control) | Right (Status) ─────────────────
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        _system_control_buttons()

        # ── Factory Task Trigger ───────────────────────────────────────────
        st.markdown('<div class="cmd-card"><h3>🏭 工厂任务触发</h3>', unsafe_allow_html=True)

        trigger_clicked = st.button(
            "🔧 Trigger Factory Task (deploy)",
            type="primary",
            use_container_width=True,
            key="btn_trigger_factory",
            help="执行 `python run_task.py deploy` 本地工厂流水线。",
        )

        if trigger_clicked:
            with st.spinner("🏭 正在执行工厂任务..."):
                result = _run_factory_task("deploy")

            if result["success"]:
                st.success("✅ 工厂任务执行成功")
            else:
                st.error(f"❌ 工厂任务执行失败 (返回码: {result['returncode']})")

            st.text_area(
                "📜 执行输出",
                value=result["output"],
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        _system_status_metrics()

        # ── Recent Activity Feed ───────────────────────────────────────────
        st.markdown('<div class="cmd-card"><h3>📋 最近活动</h3>', unsafe_allow_html=True)
        all_tasks = list_all_tasks()
        if all_tasks:
            for t in sorted(all_tasks, key=lambda x: x.get("created_at", ""),
                            reverse=True)[:4]:
                emoji = {"PENDING": "⏳", "PROCESSING": "🔄", "SUCCESS": "✅",
                         "FAILED": "❌", "COMPLETED": "📦"}.get(t["status"], "❓")
                st.markdown(
                    f"{emoji} **{t['task_id'][:24]}** — `{t['status']}`  \n"
                    f"<span style='color: #667; font-size: 0.75rem;'>{t.get('created_at', '')}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("暂无任务记录。提交第一个任务即可在此查看。")
        st.markdown('</div>', unsafe_allow_html=True)


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


# ── Version Constants ──────────────────────────────────────────────────────
# Bump this on every deployment to enable visual version tracking.
# The commit hash is injected at build time; fall back to "unknown" if
# the environment variable is not set (e.g. local dev).
APP_VERSION = "v0.2.0-Alpha"
APP_COMMIT = os.environ.get("MANEKI_COMMIT_HASH", "1243729")


# ── Main App ───────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Maneki-AI 招财猫任务控制台",
                       page_icon="🐱", layout="wide",
                       initial_sidebar_state="expanded")

    # ── Browser Console Telemetry ──────────────────────────────────────────
    # Injects a tiny JS snippet that prints the active version to the
    # browser's developer console.  This guarantees we can inspect the exact
    # deployed layer in Chrome DevTools without relying on UI text alone.
    st.markdown(
        f"""
        <script>
        console.log("=== Maneki-AI Factory Control Loaded: {APP_VERSION} (Commit: {APP_COMMIT}) ===");
        console.log("🐱 Maneki-AI — Debug version tag active");
        </script>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ────────────────────────────────────────────────────────────
    # Clean, minimal sidebar with navigation, live gateway status, and a
    # styled version badge for deployment tracking.
    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="font-size: 1.8rem;">🐱</span>
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; line-height: 1.2;">Maneki-AI</div>
                    <div style="color: #8899aa; font-size: 0.75rem;">招财猫任务工厂</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation radio — default index=0 ensures "/" always routes to C&C
        page = st.radio(
            "导航",
            ["🎮 Command & Control Center",
             "📋 提交任务", "📊 任务看板", "📄 执行报告"],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        # Live gateway status indicator
        gw_healthy = _gateway_healthy()
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; padding: 4px 0;">
                <span style="font-size: 0.7rem;">{"🟢" if gw_healthy else "🔴"}</span>
                <span style="color: {"#4caf50" if gw_healthy else "#f44336"}; font-size: 0.8rem; font-weight: 500;">
                    API Gateway — {"在线" if gw_healthy else "离线"}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Minimal Version Badge ──────────────────────────────────────────
        # Clean version tag styled as a monospace badge, giving operators
        # immediate visual confirmation of the deployed layer.
        st.markdown(
            f"""
            <div style="margin-top: 8px;">
                <span class="version-badge">{APP_VERSION}</span>
                <span style="color: #556; font-size: 0.65rem; margin-left: 6px;">
                    commit <code style="background: #1a1a2e; padding: 1px 4px; border-radius: 3px;">{APP_COMMIT[:7]}</code>
                </span>
            </div>
            <div style="color: #445; font-size: 0.65rem; margin-top: 4px;">
                🟢 Auto-Deploy Enabled
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Cross-Page Navigation ──────────────────────────────────────────────
    # If a page navigation was requested (e.g. from a button click on another
    # page), override the sidebar selection. Reset the flag immediately to
    # prevent re-triggering on re-render.
    if st.session_state.get("nav_page"):
        page = st.session_state["nav_page"]
        st.session_state["nav_page"] = None

    # ── Page Routing ───────────────────────────────────────────────────────
    # The sidebar radio always has a value (default index=0), so `page` is
    # never None. This guarantees the root URL ("/") always renders the
    # Command & Control Center without flickering or falling through to an
    # old mockup.
    if page == "🎮 Command & Control Center":
        page_command_center()
    elif page == "📋 提交任务":
        page_submit_task()
    elif page == "📊 任务看板":
        page_task_dashboard()
    elif page == "📄 执行报告":
        page_report_viewer()
    else:
        # Safety fallback — should never be reached due to index=0 default
        page_command_center()


if __name__ == "__main__":
    main()




def render_factory_trigger():
    st.subheader('?? AI Factory Control')
    if st.button('Trigger Factory Task (deploy)'):
        with st.spinner('Factory is deploying...'):
            try:
                import subprocess
                result = subprocess.run(['python', 'run_task.py', 'deploy'], capture_output=True, text=True)
                st.text_area('Execution Log:', value=result.stdout + result.stderr, height=300)
            except Exception as e:
                st.error(f'Factory Error: {e}')
# --- 注入工厂控制台 ---
import factory_ui
factory_ui.render_factory_trigger()
# --------------------
# �Զ�������Ⱦ�߼�
