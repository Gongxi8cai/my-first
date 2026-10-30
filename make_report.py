import json
from collections import defaultdict

# ---------- 读数据 ----------
records = []
with open("papers.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

print(f"读入 {len(records)} 条记录")

# ---------- 按日期分组 ----------
by_date = defaultdict(list)
by_cat  = defaultdict(int)
for r in records:
    by_date[r["date"]].append(r)
    by_cat[r["category"]] += 1

# ---------- 生成 Markdown ----------
out = []
out.append("# arXiv 论文存档\n")
out.append(f"共 **{len(records)}** 篇，覆盖 **{len(by_date)}** 天。\n")

out.append("## 分类统计\n")
out.append("| 分类 | 篇数 |")
out.append("|------|------|")
for cat, n in sorted(by_cat.items(), key=lambda x: -x[1]):
    out.append(f"| `{cat}` | {n} |")
out.append("")

out.append("## 按日期\n")
for date in sorted(by_date, reverse=True):
    papers = by_date[date]
    out.append(f"### {date}（{len(papers)} 篇）\n")
    for p in papers:
        out.append(f"- [{p['title']}]({p['id']}) — `{p['category']}`")
    out.append("")

with open("report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("已生成 report.md")