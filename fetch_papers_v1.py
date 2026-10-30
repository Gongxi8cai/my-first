import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

# ---------- 配置 ----------
CATEGORY = "cs.AI"      # 想换方向就改这里，比如 math.AG、cs.LG、physics.optics
HOW_MANY = 20           # 每次抓多少篇
STORE    = "papers.jsonl"

# ---------- 抓取 ----------
url = (f"http://export.arxiv.org/api/query"
       f"?search_query=cat:{CATEGORY}"
       f"&start=0&max_results={HOW_MANY}"
       f"&sortBy=submittedDate&sortOrder=descending")

print(f"正在连接 arXiv（{CATEGORY}，最多 {HOW_MANY} 篇）...")
raw = urllib.request.urlopen(url, timeout=30).read()
root = ET.fromstring(raw)
ns = {"a": "http://www.w3.org/2005/Atom"}

# ---------- 读已有记录（用来去重）----------
old_ids = set()
if os.path.exists(STORE):
    with open(STORE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                old_ids.add(json.loads(line)["id"])
print(f"本地已有 {len(old_ids)} 篇")

# ---------- 逐条处理 ----------
new_count = 0
with open(STORE, "a", encoding="utf-8") as f:
    for entry in root.findall("a:entry", ns):
        paper_id = entry.find("a:id", ns).text
        if paper_id in old_ids:
            continue

        record = {
            "id":      paper_id,
            "title":   " ".join(entry.find("a:title", ns).text.split()),
            "date":    entry.find("a:published", ns).text[:10],
            "summary": " ".join(entry.find("a:summary", ns).text.split())[:300],
            "category": CATEGORY,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        new_count += 1
        print(f"  + {record['date']}  {record['title'][:60]}")

print(f"\n新增 {new_count} 篇，已写入 {STORE}")