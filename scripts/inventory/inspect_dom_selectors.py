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

# 1. Bac Ninh TV / Báo Bắc Ninh
print("=== 1. Bac Ninh TV (bacninhtv.vn) ===")
r = client.get("https://bacninhtv.vn/kinh-te")
if r.status_code != 200:
    r = client.get("https://bacninhtv.vn")
print("status:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25 and ("kinh-te" in h or "tin-tuc" in h or ".html" in h):
        print("  BBN:", t[:60], "->", h)

# 2. Báo Đà Nẵng
print("\n=== 2. Báo Đà Nẵng (baodanang.vn) ===")
r = client.get("https://baodanang.vn/kinhte/")
if r.status_code != 200:
    r = client.get("https://baodanang.vn")
print("status:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25 and ("vn" in h or "/" in h) and not "javascript" in h:
        print("  BDN:", t[:60], "->", h)

# 3. Báo Tây Ninh
print("\n=== 3. Báo Tây Ninh (baotayninh.vn) ===")
r = client.get("https://baotayninh.vn/kinh-te/")
if r.status_code != 200:
    r = client.get("https://baotayninh.vn")
print("status:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25:
        print("  BTN:", t[:60], "->", h)

# 4. Báo Đồng Nai
print("\n=== 4. Báo Đồng Nai (baodongnai.com.vn) ===")
r = client.get("https://baodongnai.com.vn")
print("status:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25:
        print("  BDN:", t[:60], "->", h)

# 5. DealStreetAsia
print("\n=== 5. DealStreetAsia ===")
r = client.get("https://www.dealstreetasia.com")
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 30 and "dealstreetasia.com/stories" in h:
        print("  DSA:", t[:70], "->", h)

# 6. The Star Malaysia
print("\n=== 6. The Star Malaysia ===")
r = client.get("https://www.thestar.com.my/business")
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("a"):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 25 and "business" in h:
        print("  The Star:", t[:60], "->", h)
