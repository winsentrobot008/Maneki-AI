import streamlit as st
import yaml
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from radar.tavily_client import tavily_search
from radar.synthesizer import fuse_radar_data
from analyst.strategist_agent import StrategistAgent
from warroom.report_generator import generate_markdown_report

load_dotenv()
with open("config/settings.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title="Maneki-AI 招财猫情报局", layout="wide")

if "opportunities" not in st.session_state:
    st.session_state.opportunities = []
if "approved" not in st.session_state:
    st.session_state.approved = []

APPROVED_FILE = "approved_projects.json"
def load_approved():
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, "r") as f:
            st.session_state.approved = json.load(f)
def save_approved():
    with open(APPROVED_FILE, "w") as f:
        json.dump(st.session_state.approved, f, indent=2)
load_approved()

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    TASKS_REPO = st.secrets["TASKS_REPO"]
except Exception as e:
    st.error(f"Secrets 读取失败: {e}")
    GITHUB_TOKEN = None
    TASKS_REPO = None

def create_github_issue(title, body):
    if not GITHUB_TOKEN or not TASKS_REPO:
        return False, "GITHUB_TOKEN 或 TASKS_REPO 未配置"
    url = f"https://api.github.com/repos/{TASKS_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body,
        "labels": ["auto-approved", "maneki-ai"]
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 201:
            return True, "成功"
        else:
            return False, f"状态码 {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

page = st.sidebar.radio("导航", ["🔍 情报扫描", "📋 商机决策", "✅ 已批准项目"])

if page == "🔍 情报扫描":
    st.title("🐱 Maneki-AI 市场情报智能体")
    if st.button("🔍 立即扫描商机"):
        with st.spinner("情报雷达运转中..."):
            raw_results = []
            for kw in config["keywords"]:
                res = tavily_search(kw, max_results=3)
                raw_results.extend(res)
            fused = fuse_radar_data(raw_results, [], [])
            strategist = StrategistAgent()
            opps = []
            for item in fused:
                score = strategist.analyze({"raw": item}).get("score", 0)
                if score >= config["alert_threshold"]:
                    opps.append({
                        "title": item.get("title") or item.get("query", ""),
                        "source": "tavily",
                        "summary": item.get("content", "")[:300],
                        "score": score,
                        "timestamp": datetime.now().isoformat()
                    })
            st.session_state.opportunities = opps
            report_path = generate_markdown_report(opps)
            st.success(f"报告已生成：{report_path}")
    if st.session_state.opportunities:
        st.subheader("最新商机列表")
        for opp in st.session_state.opportunities:
            with st.expander(f"📌 {opp['title']} (置信度: {opp['score']})"):
                st.write(opp['summary'])
                st.caption(f"来源: {opp['source']}")

elif page == "📋 商机决策":
    st.title("📋 商机决策看板")
    if not st.session_state.opportunities:
        st.info("暂未扫描商机，请先前往「情报扫描」页面获取数据。")
    else:
        # 显示当前配置状态（调试用）
        with st.expander("🔧 调试信息 (仅开发者可见)"):
            st.write("GitHub Token 已配置:", bool(GITHUB_TOKEN))
            st.write("目标仓库:", TASKS_REPO)
        for idx, opp in enumerate(st.session_state.opportunities):
            already = any(a['title'] == opp['title'] for a in st.session_state.approved)
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.write(f"**{opp['title']}** (置信度: {opp['score']})")
                st.caption(opp['summary'][:100] + "...")
            with col2:
                if not already:
                    if st.button("✅ 批准开发", key=f"approve_{idx}"):
                        issue_title = f"[商机] {opp['title']}"
                        issue_body = f"""**置信度**: {opp['score']}
**来源**: {opp['source']}
**摘要**: 
{opp['summary']}

---
*本 Issue 由 Maneki-AI 自动创建，CEO 已批准开发。*"""
                        success, msg = create_github_issue(issue_title, issue_body)
                        if success:
                            st.session_state.approved.append(opp)
                            save_approved()
                            st.success(f"✅ 已批准并创建 Issue: {opp['title']}")
                        else:
                            st.error(f"创建 Issue 失败: {msg}")
                        st.rerun()
                else:
                    st.button("✔️ 已批准", key=f"done_{idx}", disabled=True)
            with col3:
                st.write("")
        st.info("💡 批准开发后，将在独立仓库 `DevDirector-Tasks` 自动创建 Issue。")

elif page == "✅ 已批准项目":
    st.title("✅ 已批准开发项目清单")
    if not st.session_state.approved:
        st.info("暂无批准的项目。")
    else:
        for proj in st.session_state.approved:
            st.markdown(f"### 📌 {proj['title']}")
            st.write(f"**置信度**: {proj['score']}")
            st.write(f"**摘要**: {proj['summary']}")
            st.write(f"**批准时间**: {proj.get('timestamp', '未知')}")
            st.markdown("---")
