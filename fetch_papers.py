import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import time
from datetime import datetime

# ---------- 配置 ----------
CATEGORIES = ["cs.AI", "cs.LG", "cs.RO", "math.PR", "math.OC", "physics.optics"]
HOW_MANY   = 10          # 每个分类抓多少篇
STORE      = "papers.jsonl"
NS = {"a": "http://www.w3.org/2005/Atom"}

# ---------- 读已有记录 ----------
old_ids = set()
if os.path.exists(STORE):
    with open(STORE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                old_ids.add(json.loads(line)["id"])
print(f"本地已有 {len(old_ids)} 篇")

# ---------- 逐分类抓取 ----------
seen = set()          # 本次运行内已见过的，防止同一篇跨分类重复
new_count = 0
total_fetched = 0

with open(STORE, "a", encoding="utf-8") as f:
    for cat in CATEGORIES:
        url = (f"http://export.arxiv.org/api/query"
               f"?search_query=cat:{cat}"
               f"&start=0&max_results={HOW_MANY}"
               f"&sortBy=submittedDate&sortOrder=descending")
        print(f"  抓取 {cat} ...")
        try:
            raw = urllib.request.urlopen(url, timeout=30).read()
        except Exception as e:
            print(f"  [跳过] {cat} 失败：{e}")
            continue

        root = ET.fromstring(raw)
        entries = root.findall("a:entry", NS)
        total_fetched += len(entries)

        for entry in entries:
            pid = entry.find("a:id", NS).text
            if pid in old_ids or pid in seen:
                continue
            seen.add(pid)

            record = {
                "id":         pid,
                "title":      " ".join(entry.find("a:title", NS).text.split()),
                "date":       entry.find("a:published", NS).text[:10],
                "summary":    " ".join(entry.find("a:summary", NS).text.split())[:300],
                "category":   cat,
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            new_count += 1
            print(f"  + [{cat}] {record['title'][:55]}")

        time.sleep(3)   # 礼貌等待：arXiv 不欢迎连发请求

print(f"\n取回 {total_fetched} 条，新增 {new_count} 篇，已写入 {STORE}")