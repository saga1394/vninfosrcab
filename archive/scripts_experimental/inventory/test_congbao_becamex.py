import sys
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# 1. Congbao HTML
r = client.get("https://congbao.chinhphu.vn/")
soup = BeautifulSoup(r.text, "html.parser")
print("=== Congbao Homepage Extraction ===")
cb_items = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if ("/van-ban/" in h or "/cong-bao/" in h) and len(t) > 20 and not any(it["url"] == h for it in cb_items):
        full_h = "https://congbao.chinhphu.vn" + h if h.startswith("/") else h
        cb_items.append({"title": t, "url": full_h})
for it in cb_items[:5]:
    print(" ", it)

# 2. Becamex news page
r_bx = client.get("https://becamex.com.vn/feed/")
fp_bx = feedparser.parse(r_bx.text)
print(f"\nBecamex feed items count: {len(fp_bx.entries)}")

r_bx_page = client.get("https://becamex.com.vn/tin-tuc/")
print("Becamex /tin-tuc/ status:", r_bx_page.status_code)
if r_bx_page.status_code == 200:
    soup_bx = BeautifulSoup(r_bx_page.text, "html.parser")
    for a in soup_bx.find_all("a", href=True):
        t = a.get_text(strip=True)
        h = a["href"]
        if len(t) > 25 and not "tin tức" in t.lower() and not "giới thiệu" in t.lower():
            print("  Becamex page article:", t[:70], "->", h)
