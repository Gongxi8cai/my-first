import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import time
from datetime import datetime
from email.utils import parsedate_to_datetime

STORE = "papers.jsonl"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36")

HOSTS = ["https://rsshub.rssforever.com", "https://rsshub.rss.tips"]

FEEDS = [
    ("新闻联播",  "/cctv/tv/lm/xwlb"),
    ("求是",      "/qstheory/magazine/qs"),
    ("求是·科教", "/qstheory/science"),
]


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()[:300]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=25).read()


def pick_title(it):
    for tag in ("title", "{http://www.w3.org/2005/Atom}title"):
        e = it.find(tag)
        if e is not None and e.text:
            return e.text.strip()
    return ""


def pick_link(it):
    for tag in ("link", "guid"):
        e = it.find(tag)
        if e is not None and e.text:
            return e.text.strip()
    e = it.find("{http://www.w3.org/2005/Atom}id")
    if e is not None and e.text:
        return e.text.strip()
    return ""


def pick_date(it):
    for tag in ("pubDate", "published", "{http://www.w3.org/2005/Atom}published"):
        e = it.find(tag)
        if e is not None and e.text:
            try:
                return parsedate_to_datetime(e.text.strip()).strftime("%Y-%m-%d")
            except Exception:
                return e.text.strip()[:10]
    return datetime.now().strftime("%Y-%m-%d")


old_ids = set()
if os.path.exists(STORE):
    with open(STORE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                old_ids.add(json.loads(line)["id"])
print(f"本地已有 {len(old_ids)} 条")

new_count = 0
seen = set()

for name, route in FEEDS:
    print(f"[{name}]")
    raw = None
    for host in HOSTS:
        try:
            raw = fetch(host + route)
            print(f"  使用 {host}")
            break
        except Exception as e:
            print(f"  失败 {type(e).__name__}")
    if raw is None:
        print("  跳过")
        continue

    root = ET.fromstring(raw)
    items = root.findall(".//item") or root.findall(
        ".//{http://www.w3.org/2005/Atom}entry")
    print(f"  取到 {len(items)} 条")

    with open(STORE, "a", encoding="utf-8") as f:
        for it in items:
            title = pick_title(it)
            link = pick_link(it)
            pid = link or (name + "|" + title)
            if not title or pid in old_ids or pid in seen:
                continue
            seen.add(pid)

            desc = it.find("description")
            if desc is None:
                desc = it.find("{http://www.w3.org/2005/Atom}summary")

            record = {
                "id": pid,
                "title": title,
                "date": pick_date(it),
                "summary": strip_html(desc.text if desc is not None else ""),
                "category": name,
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            new_count += 1
            print(f"  + {record['date']} {title[:45]}")

    time.sleep(2)

print(f"完成，新增 {new_count} 条")