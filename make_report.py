import json
import re
from collections import defaultdict

STORE = "papers.jsonl"

# ---------- 主题定义：关键词命中越多，越可能属于这个主题 ----------
TOPICS = {
    "智能体与人机交互": ["agent", "agentic", "multi-agent", "human-ai", "interaction",
                       "collaborat", "user"],
    "模型训练与推理":   ["training", "distillat", "fine-tun", "post-training", "inference",
                       "training-free", "pretrain", "sampler"],
    "机器学习理论":     ["generaliz", "calibration", "convergence rate", "sample complexity",
                       "bound", "theoretical", "pruning"],
    "机器人与控制":     ["robot", "manipulat", "quadrotor", "drone", "servoing",
                       "trajectory", "reachability", "control"],
    "概率与随机过程":   ["random", "stochastic", "probability", "self-avoiding",
                       "iterated logarithm", "branching", "martingale"],
    "优化与算法":       ["optimization", "gradient", "algorithm", "complexity",
                       "quasi-newton", "approximation", "polynomial-space"],
    "光学与量子":       ["optical", "photon", "polariton", "laser", "quantum",
                       "interferometr", "wave localization"],
}

# ---------- 读数据 ----------
records = []
with open(STORE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))
print(f"读入 {len(records)} 条记录")

# ---------- 分类 ----------
def classify(rec):
    text = (rec["title"] + " " + rec["summary"]).lower()
    best, best_hits = "未分类", 0
    for topic, kws in TOPICS.items():
        hits = sum(1 for kw in kws if kw in text)
        if hits > best_hits:
            best, best_hits = topic, hits
    return best

by_topic = defaultdict(list)
for r in records:
    by_topic[classify(r)].append(r)

by_date = defaultdict(int)
for r in records:
    by_date[r["date"]] += 1

# ---------- 写 Markdown ----------
out = ["# 前沿简报\n",
       f"共 **{len(records)}** 篇，覆盖 **{len(by_date)}** 天、**{len(by_topic)}** 个主题。\n",
       "## 主题分布\n",
       "| 主题 | 篇数 |", "|------|------|"]

for topic, papers in sorted(by_topic.items(), key=lambda x: -len(x[1])):
    out.append(f"| {topic} | {len(papers)} |")
out.append("")

out.append("## 按日期\n")
out.append("| 日期 | 篇数 |")
out.append("|------|------|")
for d in sorted(by_date, reverse=True):
    out.append(f"| {d} | {by_date[d]} |")
out.append("")

# ---------- 按主题列出 ----------
for topic, papers in sorted(by_topic.items(), key=lambda x: -len(x[1])):
    out.append(f"## {topic}（{len(papers)} 篇）\n")
    papers.sort(key=lambda r: r["date"], reverse=True)
    for p in papers:
        out.append(f"- {p['date']} · [{p['title']}]({p['id']}) — `{p['category']}`")
    out.append("")

with open("report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("已生成 report.md")
print("\n主题分布：")
for topic, papers in sorted(by_topic.items(), key=lambda x: -len(x[1])):
    print(f"  {topic:<18} {len(papers):>3} 篇")