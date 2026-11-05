import sys
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

# 1. Báo Đà Nẵng (baodanang.vn)
print("=== Báo Đà Nẵng ===")
r = client.get("https://baodanang.vn")
soup = BeautifulSoup(r.text, "html.parser")
articles_bdn = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 20 and ("baodanang.vn" in h or h.startswith("/")) and not any(k in h for k in ["#", "javascript", "category", "video"]):
        articles_bdn.append((t, h if h.startswith("http") else "https://baodanang.vn" + h))
print(f"BDN articles found: {len(articles_bdn)}")
for t, h in articles_bdn[:5]:
    print("  BDN:", t[:60], "->", h)

# 2. Diễn đàn Doanh nghiệp (diendandoanhnghiep.vn)
print("\n=== Diễn đàn Doanh nghiệp ===")
r = client.get("https://diendandoanhnghiep.vn/kinh-te.html")
soup = BeautifulSoup(r.text, "html.parser")
articles_dddn = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25 and h.endswith(".html") and not any(k in h for k in ["kinh-te.html", "index.html", "rss"]):
        articles_dddn.append((t, h if h.startswith("http") else "https://diendandoanhnghiep.vn" + h))
print(f"DDDN articles found: {len(articles_dddn)}")
for t, h in articles_dddn[:5]:
    print("  DDDN:", t[:60], "->", h)

# 3. Financial News Korea (fnnews.com)
print("\n=== Financial News Korea ===")
r = client.get("https://www.fnnews.com")
soup = BeautifulSoup(r.text, "html.parser")
articles_fn = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 15 and "news/" in h:
        articles_fn.append((t, h if h.startswith("http") else "https://www.fnnews.com" + h))
print(f"FN articles found: {len(articles_fn)}")
for t, h in articles_fn[:5]:
    print("  FN:", t[:60], "->", h)

# 4. VOV (vov.vn)
print("\n=== VOV (vov.vn) ===")
# Let's check vov.vn/kinh-te
r = client.get("https://vov.vn/kinh-te", headers={"User-Agent": "curl/7.88.1"})
soup = BeautifulSoup(r.text, "html.parser")
articles_vov = []
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25 and "-post" in h:
        articles_vov.append((t, h if h.startswith("http") else "https://vov.vn" + h))
print(f"VOV articles found: {len(articles_vov)}")
for t, h in articles_vov[:5]:
    print("  VOV:", t[:60], "->", h)
