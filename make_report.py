import json
from collections import defaultdict

STORE = "papers.jsonl"

# arXiv 分类代码 → 人能读的名字
CAT_NAME = {
    "cs.AI": "人工智能", "cs.LG": "机器学习", "cs.RO": "机器人",
    "math.PR": "概率论",   "math.OC": "优化与控制", "physics.optics": "光学",
}

# 只在 cs.AI / cs.LG 这两个大类内部再细分（它们太杂）
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

# ---------- 一级：按 arXiv 分类 ----------
by_cat = defaultdict(list)
for r in records:
    by_cat[r["category"]].append(r)

by_date = defaultdict(int)
for r in records:
    by_date[r["date"]] += 1

# ---------- 写 ----------
out = ["# 前沿简报\n",
       f"共 **{len(records)}** 篇，覆盖 **{len(by_date)}** 天、**{len(by_cat)}** 个学科。\n",
       "## 学科分布\n",
       "| 学科 | arXiv 分类 | 篇数 |",
       "|------|-----------|------|"]

for cat, papers in sorted(by_cat.items(), key=lambda x: -len(x[1])):
    out.append(f"| {CAT_NAME.get(cat, cat)} | `{cat}` | {len(papers)} |")
out.append("")

out.append("## 每日数量\n| 日期 | 篇数 |\n|------|------|")
for d in sorted(by_date, reverse=True):
    out.append(f"| {d} | {by_date[d]} |")
out.append("")

# ---------- 按学科列出，cs.AI / cs.LG 内部再细分 ----------
for cat, papers in sorted(by_cat.items(), key=lambda x: -len(x[1])):
    name = CAT_NAME.get(cat, cat)
    out.append(f"## {name}（`{cat}`，{len(papers)} 篇）\n")
    papers.sort(key=lambda r: r["date"], reverse=True)

    if cat in ("cs.AI", "cs.LG"):
        groups = defaultdict(list)
        for p in papers:
            groups[subtype(p) or "其他"].append(p)
        for sub, ps in sorted(groups.items(), key=lambda x: -len(x[1])):
            out.append(f"### {sub}（{len(ps)} 篇）\n")
            for p in ps:
                out.append(f"- {p['date']} · [{p['title']}]({p['id']})")
            out.append("")
    else:
        for p in papers:
            out.append(f"- {p['date']} · [{p['title']}]({p['id']})")
        out.append("")

with open("report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"读入 {len(records)} 条 → 生成 {len(by_cat)} 个学科、{len(by_date)} 天")