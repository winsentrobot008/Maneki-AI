"""
app.py — Maneki-AI 招财猫任务控制台 (Render Deployment Entry)

A Streamlit single-page application deployed at https://maneki-ai.onrender.com/.

Provides:
  1. Task Submission — user submits a task → status "PENDING"
  2. Task Dashboard — real-time status overview of all tasks
  3. Report Viewer — dynamic rendering of execution logs & reports

Data is stored as lightweight JSON files in task_queue/ and logs/.
No external database required.
"""

import os
import sys
import json
import glob
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
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

# ── Dynamic Tunnel Gateway ────────────────────────────────────────────────
# The tunnel gateway URL is reported by the local factory via a best-effort
# POST to /api/config/tunnel-gateway.  It is stored in-memory and used to
# route task submissions to the correct local gateway.  Falls back to the
# static API_GATEWAY_URL env-var when no tunnel has been reported.
_tunnel_gateway_url: str | None = None
TUNNEL_GATEWAY_FILE = os.path.join(PROJECT_ROOT, "config", "tunnel_gateway.json")


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


# ── Tunnel Gateway Management ─────────────────────────────────────────────
# The tunnel gateway URL is dynamically reported by the local factory and
# persisted to a JSON file so it survives Render instance restarts.
# When routing a new task, submit_task() uses this dynamic address if set,
# falling back to the static API_GATEWAY_URL env-var.

def _get_active_gateway_url() -> str:
    """Return the tunnel gateway URL if reported, else the static env-var."""
    global _tunnel_gateway_url
    if _tunnel_gateway_url:
        return _tunnel_gateway_url
    # Try loading from persisted file on first call
    if os.path.isfile(TUNNEL_GATEWAY_FILE):
        try:
            with open(TUNNEL_GATEWAY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                url = data.get("tunnel_gateway_url", "")
                if url:
                    _tunnel_gateway_url = url
                    return url
        except (json.JSONDecodeError, IOError):
            pass
    return API_GATEWAY_URL


def _set_tunnel_gateway_url(url: str) -> None:
    """Store the tunnel gateway URL in memory and persist to disk."""
    global _tunnel_gateway_url
    _tunnel_gateway_url = url
    os.makedirs(os.path.dirname(TUNNEL_GATEWAY_FILE), exist_ok=True)
    try:
        with open(TUNNEL_GATEWAY_FILE, "w", encoding="utf-8") as f:
            json.dump({"tunnel_gateway_url": url, "updated_at": _now_iso()}, f)
    except IOError:
        pass  # best-effort persistence


# ── Embedded Config HTTP Server ───────────────────────────────────────────
# A lightweight background HTTP server that listens on a configurable port
# (default 9999) for the local factory to POST the tunnel gateway URL.
# This keeps the tunnel URL completely hidden from the Streamlit UI.

CONFIG_SERVER_PORT = int(os.environ.get("MANEKI_CONFIG_PORT", "9999"))


class ConfigHTTPHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that accepts tunnel gateway URL updates."""

    def _send_json(self, status_code: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict | None:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_POST(self) -> None:
        if self.path == "/api/config/tunnel-gateway":
            body = self._read_body()
            if body and isinstance(body.get("tunnel_gateway_url"), str):
                url = body["tunnel_gateway_url"].strip()
                if url:
                    _set_tunnel_gateway_url(url)
                    print(f"[config-server] ✅ Tunnel gateway updated: {url}")
                    self._send_json(200, {"status": "OK",
                                          "message": "Tunnel gateway updated."})
                    return
            self._send_json(400, {"status": "ERROR",
                                  "message": "Missing or invalid 'tunnel_gateway_url'."})
        else:
            self._send_json(404, {"status": "ERROR",
                                  "message": f"Not found: {self.path}"})

    def do_GET(self) -> None:
        if self.path == "/api/config/tunnel-gateway":
            self._send_json(200, {
                "tunnel_gateway_url": _get_active_gateway_url(),
                "updated_at": _now_iso(),
            })
        else:
            self._send_json(404, {"status": "ERROR",
                                  "message": f"Not found: {self.path}"})

    def log_message(self, fmt, *args) -> None:
        sys.stderr.write(f"[config-server] {args[0]} {args[1]} {args[2]}\n")


def _start_config_server() -> None:
    """Start the config HTTP server in a background daemon thread."""
    server = HTTPServer(("0.0.0.0", CONFIG_SERVER_PORT), ConfigHTTPHandler)
    print(f"[config-server] Listening on http://0.0.0.0:{CONFIG_SERVER_PORT}")
    print(f"[config-server] POST /api/config/tunnel-gateway — update tunnel URL")
    print(f"[config-server] GET  /api/config/tunnel-gateway — query tunnel URL")
    try:
        server.serve_forever()
    except Exception:
        pass


# Start the config server in background when module loads
_config_thread = Thread(target=_start_config_server, daemon=True)
_config_thread.start()


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
    and best-effort POST to the API Gateway.
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

    # Best-effort POST to the active gateway (tunnel URL if reported,
    # otherwise the static API_GATEWAY_URL env-var).
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
        page = st.radio("导航", ["📋 提交任务", "📊 任务看板", "📄 执行报告"],
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
    if page == "📋 提交任务":
        page_submit_task()
    elif page == "📊 任务看板":
        page_task_dashboard()
    elif page == "📄 执行报告":
        page_report_viewer()


if __name__ == "__main__":
    main()
