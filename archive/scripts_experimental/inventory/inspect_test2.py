import sys
import subprocess
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(
    verify=False,
    follow_redirects=True,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'vi,en;q=0.9',
    },
    timeout=15.0
)

# 1. The Economic Times
print("--- 1. The Economic Times ---")
for url in [
    "https://economictimes.indiatimes.com",
    "http://economictimes.indiatimes.com",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://m.economictimes.com"
]:
    try:
        r = client.get(url, timeout=5.0)
        print(f"ET {url}: HTTP {r.status_code}")
    except Exception as e:
        print(f"ET {url}: {type(e).__name__}: {e}")

# Try curl on ET
res = subprocess.run(["curl.exe", "-s", "-i", "-k", "--connect-timeout", "5", "https://economictimes.indiatimes.com"], capture_output=True, text=True, errors="replace")
print("ET curl lines:", res.stdout.splitlines()[:2])

# 2. Báo Đà Nẵng
print("\n--- 2. Báo Đà Nẵng ---")
r = client.get("https://baodanang.vn/kinhte/")
print("baodanang /kinhte/:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".media a, .item a, .news-item a, article a, h2 a, h3 a, h4 a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if t and len(t) > 15:
        print("  BDN article:", t[:50], "->", h)

# 3. Báo Thái Nguyên
print("\n--- 3. Báo Thái Nguyên ---")
r = client.get("https://baothainguyen.vn/kinh-te/")
print("baothainguyen /kinh-te/:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".zone--content a, .story a, .item a, article a, h2 a, h3 a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if t and len(t) > 20 and not "chuyen-muc" in h:
        print("  BTN article:", t[:50], "->", h)

# 4. Báo Bắc Ninh
print("\n--- 4. Báo Bắc Ninh ---")
# Check bacninh.gov.vn news
r = client.get("https://bacninh.gov.vn/tin-tuc-su-kien")
print("bacninh.gov.vn news:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.select("a"):
        t = a.get_text(strip=True)
        h = a.get("href", "")
        if t and len(t) > 25 and ("kinh-te" in h or "tin-tuc" in h or "chi-tiet" in h):
            print("  BBN Portal:", t[:50], "->", h)

# Check bacninhtv.vn news
r = client.get("https://bacninhtv.vn")
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".item a, .news a, article a, h2 a, h3 a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if t and len(t) > 20:
        print("  BBN TV:", t[:50], "->", h)

# 5. Financial News Korea (fnnews.com)
print("\n--- 5. Financial News Korea ---")
r = client.get("https://www.fnnews.com/section/002001000")
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".tit a, .art_title a, dt a, .thumb_txt a"):
    t = a.get_text(strip=True)
    h = a.get("href", "")
    if t and len(t) > 10:
        print("  FN:", t[:50], "->", h)

# 6. Manila Bulletin
print("\n--- 6. Manila Bulletin ---")
for ep in ["https://mb.com.ph", "https://mb.com.ph/category/business", "https://mb.com.ph/feed/"]:
    res = subprocess.run(["curl.exe", "-s", "-i", "-k", "--connect-timeout", "5", ep], capture_output=True, text=True, errors="replace")
    print("MB curl:", ep, "->", res.stdout.splitlines()[:2])
