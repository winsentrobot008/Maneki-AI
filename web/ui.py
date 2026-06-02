"""
web/ui.py — Maneki-AI Web UI Components

Streamlit-based visual components for:
  1. Task Submission Form — "Submit Task" button → status "PENDING"
  2. Task Dashboard — Real-time status overview of all tasks
  3. Report Viewer — Dynamic rendering of execution reports from logs/
"""

import os
import streamlit as st
from datetime import datetime, timezone

from web.api import (
    submit_task,
    list_all_tasks,
    get_task_status,
    read_task_report,
    read_task_log,
)


# ── Page Configuration ────────────────────────────────────────────────────

def configure_page():
    """Set Streamlit page config (call once at app start)."""
    st.set_page_config(
        page_title="Maneki-AI 任务控制台",
        page_icon="🐱",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ── Sidebar ───────────────────────────────────────────────────────────────

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.image(
            "https://img.icons8.com/fluency/96/cat-head.png",
            width=64,
        )
        st.markdown("## 🐱 Maneki-AI")
        st.markdown("**招财猫任务工厂**")
        st.divider()

        # Navigation
        page = st.radio(
            "导航",
            ["📋 提交任务", "📊 任务看板", "📄 执行报告"],
            label_visibility="collapsed",
        )
        st.divider()

        # System status indicator
        st.caption("系统状态")
        st.markdown("🟢 **API Gateway** — 在线" if _gateway_healthy() else "🔴 **API Gateway** — 离线")

        st.divider()
        st.caption(f"v1.0.0 · {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")

    return page


def _gateway_healthy() -> bool:
    """Quick health check against the API Gateway."""
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    from web.api import API_GATEWAY_URL

    try:
        req = Request(f"{API_GATEWAY_URL}/api/health", method="GET")
        resp = urlopen(req, timeout=2)
        return resp.status == 200
    except (URLError, OSError):
        return False


# ── Page 1: Task Submission ───────────────────────────────────────────────

def render_task_submission():
    """Render the 'Submit Task' form."""
    st.header("📋 提交新任务")
    st.markdown("填写以下表单以向 Maneki-AI 工厂提交一个新的执行任务。")

    with st.form("task_submit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            task_id = st.text_input(
                "任务 ID",
                value=f"TASK_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                help="唯一任务标识符。自动生成，可手动修改。",
            )
            script_name = st.text_input(
                "脚本名称",
                value="scripts/example_worker.py",
                help="相对于项目根目录的脚本路径。",
            )

        with col2:
            extra_params_raw = st.text_area(
                "额外参数 (JSON)",
                value='{\n  "description": "Example task"\n}',
                height=120,
                help="可选的 JSON 格式额外参数。",
            )

        submitted = st.form_submit_button(
            "🚀 提交任务",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not task_id.strip():
            st.error("任务 ID 不能为空。")
            return
        if not script_name.strip():
            st.error("脚本名称不能为空。")
            return

        # Parse extra params
        extra_params = {}
        if extra_params_raw.strip():
            import json
            try:
                extra_params = json.loads(extra_params_raw)
            except json.JSONDecodeError as e:
                st.error(f"额外参数 JSON 格式错误: {e}")
                return

        # Submit the task
        with st.spinner(f"正在提交任务 {task_id} ..."):
            result = submit_task(task_id, script_name.strip(), extra_params)

        if result["success"]:
            st.success(f"✅ **{result['message']}**")
            st.info(f"任务状态已设置为 **{result['status']}**，等待工厂处理。")
        else:
            st.error(f"❌ 提交失败: {result['message']}")

    # Show recent submissions
    st.divider()
    st.subheader("最近提交的任务")
    all_tasks = list_all_tasks()
    if all_tasks:
        # Sort by created_at descending, show top 5
        sorted_tasks = sorted(
            all_tasks,
            key=lambda t: t.get("created_at", ""),
            reverse=True,
        )[:5]
        for t in sorted_tasks:
            status_emoji = {
                "PENDING": "⏳",
                "PROCESSING": "🔄",
                "SUCCESS": "✅",
                "FAILED": "❌",
                "COMPLETED": "📦",
            }.get(t["status"], "❓")
            st.markdown(
                f"{status_emoji} **{t['task_id']}** — `{t['status']}` "
                f"({t.get('created_at', 'N/A')})"
            )
    else:
        st.info("暂无任务记录。")


# ── Page 2: Task Dashboard ────────────────────────────────────────────────

def render_task_dashboard():
    """Render the task status dashboard with filtering."""
    st.header("📊 任务看板")
    st.markdown("所有任务的实时状态概览。")

    all_tasks = list_all_tasks()

    if not all_tasks:
        st.info("暂无任务。请前往「提交任务」页面创建新任务。")
        return

    # ── Summary stats ──
    col1, col2, col3, col4 = st.columns(4)
    statuses = [t["status"] for t in all_tasks]
    with col1:
        st.metric("总任务数", len(all_tasks))
    with col2:
        st.metric("待处理", statuses.count("PENDING"))
    with col3:
        st.metric("处理中", statuses.count("PROCESSING"))
    with col4:
        st.metric("已完成", statuses.count("SUCCESS") + statuses.count("COMPLETED"))

    st.divider()

    # ── Filter ──
    filter_status = st.selectbox(
        "按状态筛选",
        ["全部", "PENDING", "PROCESSING", "SUCCESS", "FAILED", "COMPLETED"],
    )

    filtered = all_tasks
    if filter_status != "全部":
        filtered = [t for t in all_tasks if t["status"] == filter_status]

    # ── Task table ──
    for task in sorted(
        filtered,
        key=lambda t: t.get("created_at", ""),
        reverse=True,
    ):
        status_emoji = {
            "PENDING": "⏳",
            "PROCESSING": "🔄",
            "SUCCESS": "✅",
            "FAILED": "❌",
            "COMPLETED": "📦",
            "NOT_FOUND": "🔍",
        }.get(task["status"], "❓")

        with st.expander(
            f"{status_emoji} **{task['task_id']}** — `{task['status']}`",
            expanded=False,
        ):
            cols = st.columns([1, 2])
            with cols[0]:
                st.markdown(f"**状态**: `{task['status']}`")
                st.markdown(f"**创建时间**: {task.get('created_at', 'N/A')}")
                st.markdown(f"**更新时间**: {task.get('updated_at', 'N/A')}")
            with cols[1]:
                params = task.get("parameters", {})
                if params:
                    st.markdown("**参数**:")
                    st.json(params)
                if task.get("result_log"):
                    st.markdown(f"**报告文件**: `{task['result_log']}`")

            # Quick action: View report
            if task["status"] in ("SUCCESS", "FAILED", "COMPLETED"):
                if st.button(
                    "📄 查看执行报告",
                    key=f"view_report_{task['task_id']}",
                ):
                    st.session_state["view_task_id"] = task["task_id"]
                    st.session_state["navigate_to"] = "📄 执行报告"
                    st.rerun()


# ── Page 3: Report Viewer ─────────────────────────────────────────────────

def render_report_viewer():
    """Render the execution report viewer."""
    st.header("📄 执行报告")
    st.markdown("查看任务的详细执行日志和结构化报告。")

    all_tasks = list_all_tasks()
    completed_tasks = [
        t for t in all_tasks
        if t["status"] in ("SUCCESS", "FAILED", "COMPLETED")
    ]

    if not completed_tasks:
        st.info("暂无已完成的任务报告。")
        return

    # Task selector
    task_options = {t["task_id"]: t for t in completed_tasks}
    default_task = st.session_state.get("view_task_id", list(task_options.keys())[0])

    selected_task_id = st.selectbox(
        "选择任务",
        options=list(task_options.keys()),
        index=list(task_options.keys()).index(default_task)
        if default_task in task_options
        else 0,
    )

    if not selected_task_id:
        return

    # ── Structured Report ──
    report = read_task_report(selected_task_id)
    if report:
        st.subheader("📋 结构化报告")
        col1, col2, col3 = st.columns(3)
        with col1:
            status_val = report.get("status", "UNKNOWN")
            status_icon = "✅" if status_val == "SUCCESS" else "❌"
            st.metric("状态", f"{status_icon} {status_val}")
        with col2:
            st.metric("任务 ID", report.get("task_id", "N/A"))
        with col3:
            st.metric("时间戳", report.get("timestamp", "N/A"))

        # Show full report JSON
        with st.expander("查看完整报告 JSON", expanded=False):
            st.json(report)
    else:
        st.warning(f"未找到任务 {selected_task_id} 的结构化报告。")

    st.divider()

    # ── Full Execution Log ──
    log_content = read_task_log(selected_task_id)
    if log_content:
        st.subheader("📜 执行日志")
        st.text_area(
            "日志内容",
            value=log_content,
            height=400,
            disabled=True,
            label_visibility="collapsed",
        )

        # Download button
        st.download_button(
            label="⬇️ 下载日志文件",
            data=log_content,
            file_name=f"task_{selected_task_id}.log",
            mime="text/plain",
        )
    else:
        st.info(f"未找到任务 {selected_task_id} 的详细执行日志。")

    # ── Raw log file path ──
    st.caption(
        f"日志路径: `logs/task_{selected_task_id}.log`  |  "
        f"报告路径: `logs/task_{selected_task_id}_report.json`"
    )


# ── Main App ──────────────────────────────────────────────────────────────

def main():
    """Main entry point for the Maneki-AI Web UI."""
    configure_page()

    # Navigation
    page = render_sidebar()

    # Handle navigation from dashboard "View Report" button
    if st.session_state.get("navigate_to"):
        page = st.session_state["navigate_to"]
        st.session_state["navigate_to"] = None

    # Render selected page
    if page == "📋 提交任务":
        render_task_submission()
    elif page == "📊 任务看板":
        render_task_dashboard()
    elif page == "📄 执行报告":
        render_report_viewer()


if __name__ == "__main__":
    main()
