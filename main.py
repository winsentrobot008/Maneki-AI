import sys
import yaml
from dotenv import load_dotenv
from radar.tavily_client import tavily_search
from radar.synthesizer import fuse_radar_data
from analyst.strategist_agent import StrategistAgent
from warroom.report_generator import generate_markdown_report

load_dotenv()
with open("config/settings.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

def main():
    print("🐱 Maneki-AI 情报军团启动…")
    raw_results = []
    for kw in config["keywords"]:
        print(f"🔍 搜索关键词: {kw}")
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
    print(f"✅ 简报已生成: {report_path}")
    for opp in opportunities:
        print(f"   - {opp['title']}")

if __name__ == "__main__":
    main()
