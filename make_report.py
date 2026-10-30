import json
from collections import defaultdict
from datetime import datetime, timedelta

STORE = "papers.jsonl"
RECENT_DAYS = 14          # 报告只显示最近多少天

CAT_NAME = {
    "cs.AI": "人工智能", "cs.LG": "机器学习", "cs.RO": "机器人",
    "math.PR": "概率论", "math.OC": "优化与控制", "physics.optics": "光学",
    "新闻联播": "新闻联播", "求是": "求是", "求是·科教": "求是·科教",
}

SUBTYPES = {
    "智能体与交互": ["agent", "agentic", "human-ai", "human-llm", "collaborat"],
    "模型训练":     ["training", "distillat", "fine-tun", "pretrain", "sampler"],
    "理论与校准":   ["calibration", "generaliz", "sample complexity", "bound"],
    "视觉与多模态": ["visual", "vision", "image", "segmentation", "lidar", "3d"],
    "隐私与安全":   ["privacy", "private", "watermark", "attack", "robust"],
}


def subtype(rec):
    text = (rec["title"] + " " + rec["summary"]).lower()
    best, best_hits = None, 0
    for name, kws in SUBTYPES.items():
        hits = sum(1 for kw in kws if kw in text)
        if hits > best_hits:
            best, best_hits = name, hits
    return best


# ---------- 读 ----------
records = []
with open(STORE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

if not records:
    raise SystemExit("没有数据")

# ---------- 以数据里最新的一天为锚点，往前推 ----------
all_dates = sorted({r["date"] for r in records})
latest = all_dates[-1]
cutoff = (datetime.strptime(latest, "%Y-%m-%d")
          - timedelta(days=RECENT_DAYS - 1)).strftime("%Y-%m-%d")
recent = [r for r in records if r["date"] >= cutoff]

by_cat_all = defaultdict(int)
by_cat_recent = defaultdict(int)
for r in records:
    by_cat_all[r["category"]] += 1
    if r["date"] >= cutoff:
        by_cat_recent[r["category"]] += 1

by_date = defaultdict(int)
for r in recent:
    by_date[r["date"]] += 1

# ---------- 写 ----------
out = ["# 前沿简报\n"]

out.append(f"> 归档共 **{len(records)}** 条，覆盖 **{len(all_dates)}** 天。"
           f"本页只展示最近 {RECENT_DAYS} 天（{cutoff} 起）的 **{len(recent)}** 条。\n")

out.append("## 来源分布\n")
out.append("| 来源 | 总共 | 最近 {} 天 |".format(RECENT_DAYS))
out.append("|------|------|-----------|")
for cat, n in sorted(by_cat_all.items(), key=lambda x: -x[1]):
    out.append(f"| {CAT_NAME.get(cat, cat)} | {n} | {by_cat_recent.get(cat, 0)} |")
out.append("")

out.append(f"## 最近 {RECENT_DAYS} 天每日数量\n")
out.append("| 日期 | 条数 |")
out.append("|------|------|")
for d in sorted(by_date, reverse=True):
    out.append(f"| {d} | {by_date[d]} |")
out.append("")

# ---------- 按分类列出（只列最近） ----------
for cat in sorted(by_cat_recent, key=lambda c: -by_cat_recent[c]):
    papers = [r for r in recent if r["category"] == cat]
    papers.sort(key=lambda r: r["date"], reverse=True)
    name = CAT_NAME.get(cat, cat)

    out.append(f"## {name}（{len(papers)} 条）\n")

    if cat in ("cs.AI", "cs.LG"):
        groups = defaultdict(list)
        for p in papers:
            groups[subtype(p) or "其他"].append(p)
        for sub, ps in sorted(groups.items(), key=lambda x: -len(x[1])):
            out.append(f"### {sub}（{len(ps)} 条）\n")
            for p in ps:
                out.append(f"- {p['date']} · [{p['title']}]({p['id']})")
            out.append("")
    else:
        for p in papers:
            out.append(f"- {p['date']} · [{p['title']}]({p['id']})")
        out.append("")

with open("report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"归档 {len(records)} 条 / {len(all_dates)} 天")
print(f"本页显示最近 {RECENT_DAYS} 天（{cutoff} 起）的 {len(recent)} 条")
print(f"来源：{', '.join(f'{CAT_NAME.get(c,c)} {by_cat_recent.get(c,0)}' for c in by_cat_recent)}")