import sys
import subprocess
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0)

# 1. Vietnam News
print("=== 1. Vietnam News ===")
r = client.get("https://vietnamnews.vn/rss/economy.rss")
print("status:", r.status_code, "len:", len(r.content))
fp = feedparser.parse(r.content)
print("entries:", len(fp.entries))
if fp.entries:
    for e in fp.entries[:3]:
        print(" ", e.title, e.link)

# 2. Báo Đầu tư
print("\n=== 2. Báo Đầu tư ===")
r = client.get("https://baodautu.vn/dau-tu-c4/")
print("status:", r.status_code, "len:", len(r.text))
soup = BeautifulSoup(r.text, "html.parser")
articles = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 20 and "-d" in h and h.endswith(".html") and not any(k in h for k in ["#", "javascript", "category"]):
        if h not in [x[1] for x in articles]:
            articles.append((t, h if h.startswith("http") else "https://baodautu.vn" + h))
print("baodautu articles found:", len(articles))
for t, h in articles[:5]:
    print(" ", t[:60], "->", h)

# 3. Báo Tây Ninh
print("\n=== 3. Báo Tây Ninh ===")
r = client.get("https://baotayninh.vn")
soup = BeautifulSoup(r.text, "html.parser")
articles_btn = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 20 and h.endswith(".html") and "-" in h:
        if h not in [x[1] for x in articles_btn]:
            articles_btn.append((t, h if h.startswith("http") else "https://baotayninh.vn" + h))
print("baotayninh articles found:", len(articles_btn))
for t, h in articles_btn[:5]:
    print(" ", t[:60], "->", h)

# 4. TechNode Global
print("\n=== 4. TechNode Global ===")
res = subprocess.run(
    ["curl.exe", "-s", "-k", "-L",
     "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
     "https://technode.global/feed/"],
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print("curl len:", len(res.stdout))
fp = feedparser.parse(res.stdout)
print("entries:", len(fp.entries))
if fp.entries:
    for e in fp.entries[:3]:
        print(" ", e.title, e.link)

# 5. Korea Times
print("\n=== 5. Korea Times ===")
for ep in ["https://www.koreatimes.co.kr/www/rss/rss.xml", "https://feed.koreatimes.co.kr/k/allnews.xml", "https://www.koreatimes.co.kr/www/rss/biz.xml"]:
    try:
        r = client.get(ep)
        fp = feedparser.parse(r.content)
        print(ep, "->", len(fp.entries))
    except Exception as e:
        print(ep, "->", e)
