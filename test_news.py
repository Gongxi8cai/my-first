import urllib.request
import xml.etree.ElementTree as ET
import socket

# 官方文档列的公共实例（含一个国内的）
HOSTS = [
    "https://rsshub.app",
    "https://rss.spriple.org",
    "https://rsshub.rssforever.com",
    "https://hub.slarker.me",
    "https://rsshub.pseudoyu.com",
    "https://rsshub.rss.tips",
    "https://rss.owo.nz",
    "https://rsshub.email-once.com",
]

ROUTE = "/cctv/tv/lm/xwlb"   # 先用新闻联播这一条测，最快看出谁通
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

socket.setdefaulttimeout(15)
works = []

for host in HOSTS:
    url = host + ROUTE
    print(f"\n--- {host} ---")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        })
        raw = urllib.request.urlopen(req, timeout=15).read()
        root = ET.fromstring(raw)
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry")
        print(f"  ✅ 成功，{len(items)} 条")
        for it in items[:2]:
            t = it.find("title")
            if t is None:
                t = it.find("{http://www.w3.org/2005/Atom}title")
            if t is not None and t.text:
                print(f"     · {t.text.strip()[:55]}")
        works.append(host)
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")

print("\n" + "=" * 45)
if works:
    print("可用的服务器：")
    for w in works:
        print("  " + w)
else:
    print("全部失败，需要换方案")