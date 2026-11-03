import sys
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# 1. VSIP (RSS)
print("=== 1. VSIP (feed) ===")
r = client.get("https://www.vsip.com.vn/feed/")
fp = feedparser.parse(r.text)
for e in fp.entries[:3]:
    print("  VSIP:", e.title, "|", e.published, "|", e.link)

# 2. Amata (feed)
print("\n=== 2. Amata (feed) ===")
r = client.get("https://amatavn.com/feed/")
fp = feedparser.parse(r.text)
for e in fp.entries[:3]:
    print("  Amata:", e.title, "|", e.published, "|", e.link)

# 3. Becamex (feed)
print("\n=== 3. Becamex (feed) ===")
r = client.get("https://becamex.com.vn/feed/")
fp = feedparser.parse(r.text)
for e in fp.entries[:3]:
    print("  Becamex:", e.title, "|", e.published, "|", e.link)

# 4. DEEP C (HTML)
print("\n=== 4. DEEP C ===")
r = client.get("https://deepc.vn/vi/thong-tin-chuyen-nganh/tin-tuc-su-kien/")
soup = BeautifulSoup(r.text, "html.parser")
cards = soup.find_all("div", class_=lambda c: c and any(k in str(c) for k in ["blog-item", "card", "post-item", "item"]))
print("Deep C items count:", len(cards))
# fallback to links
dc_links = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if "/blog/" in h and len(t) > 20:
        dc_links.append((t, h))
for t, h in dc_links[:3]:
    print("  DEEP C:", t, "->", h)

# 5. Long Hau (HTML)
print("\n=== 5. Long Hau ===")
r = client.get("https://longhau.com.vn/truyen-thong/tin-tuc-su-kien")
soup = BeautifulSoup(r.text, "html.parser")
lh_links = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if ("/tin-tuc-su-kien/" in h or "/thong-tin-thi-truong/" in h) and len(t) > 20:
        lh_links.append((t, h))
for t, h in lh_links[:3]:
    print("  Long Hau:", t, "->", h)

# 6. BW Industrial (feed)
print("\n=== 6. BW Industrial (feed) ===")
r = client.get("https://bwindustrial.com/feed/")
fp = feedparser.parse(r.text)
for e in fp.entries[:3]:
    print("  BW Industrial:", e.title, "|", e.published, "|", e.link)

# 7. WHA Vietnam (HTML)
print("\n=== 7. WHA Vietnam ===")
r = client.get("https://www.whavietnam.com/en/updates/company-news")
soup = BeautifulSoup(r.text, "html.parser")
wha_links = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if "/updates/company-news/" in h and len(t) > 20:
        wha_links.append((t, h))
for t, h in wha_links[:3]:
    print("  WHA:", t, "->", h)
