import streamlit as st
from dotenv import load_dotenv
from radar.tavily_client import tavily_search
from radar.synthesizer import fuse_radar_data
from analyst.strategist_agent import StrategistAgent
from warroom.report_generator import generate_markdown_report
import yaml

load_dotenv()
with open("config/settings.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title="Maneki-AI 招财猫情报局", layout="wide")
st.title("🐱 Maneki-AI 市场情报智能体")

if st.button("🔍 立即扫描商机"):
    with st.spinner("情报雷达运转中..."):
        raw_results = []
        for kw in config["keywords"]:
            res = tavily_search(kw, max_results=3)
            raw_results.extend(res)
        fused = fuse_radar_data(raw_results, [], [])
        strategist = StrategistAgent()
        opportunities = []
        for item in fused:
            score = strategist.analyze({"raw": item}).get("score", 0)
            if score >= config["alert_threshold"]:
                opportunities.append({
                    "title": item.get("title") or item.get("query", ""),
                    "source": "tavily",
                    "summary": item.get("content", "")[:200],
                    "score": score
                })
        report_path = generate_markdown_report(opportunities)
        st.success(f"报告已生成：{report_path}")
        for opp in opportunities:
            with st.expander(f"📌 {opp['title']} (置信度: {opp['score']})"):
                st.write(opp['summary'])
                st.caption(f"来源: {opp['source']}")
