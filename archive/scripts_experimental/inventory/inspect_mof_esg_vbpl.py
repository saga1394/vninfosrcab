import sys
import re
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers=headers)

# 1. MOF: Search API endpoints in JS file
print("--- Checking MOF JS ---")
r_js = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
apis = set(re.findall(r'["\'](/api/[^"\']+|\bhttps?://[^"\']+/api/[^"\']+)["\']', r_js.text))
print("Found API endpoints in MOF JS:", len(apis))
for a in list(apis)[:10]:
    print("  MOF API:", a)

# Also check common MOF endpoints
for ep in ["/api/news", "/api/v1/news", "/webcenter/portal/btcvn", "/portal/page/portal/mof_vn"]:
    try:
        r = client.get(f"https://www.mof.gov.vn{ep}")
        print(f"MOF {ep} -> {r.status_code}, len={len(r.text)}")
    except Exception as e:
        print(f"MOF {ep} -> {e}")

# 2. EnterpriseSG Media Centre
print("\n--- Checking EnterpriseSG Media Centre ---")
r_esg = client.get("https://www.enterprisesg.gov.sg/resources/media-centre")
soup_esg = BeautifulSoup(r_esg.text, "html.parser")
print("ESG Media Centre Title:", soup_esg.find("title").get_text(strip=True) if soup_esg.find("title") else "")
esg_items = []
for a in soup_esg.find_all("a", href=True):
    t = a.get_text(strip=True)
    if len(t) > 20:
        esg_items.append((t, a["href"]))
print(f"Found {len(esg_items)} ESG links:")
for t, h in esg_items[:5]:
    print("  -", t[:80], "->", h)

# 3. VBPL
print("\n--- Checking VBPL ---")
r_vbpl = client.get("https://vbpl.vn/")
soup_vbpl = BeautifulSoup(r_vbpl.text, "html.parser")
# Check forms, tables, lists
print("VBPL title:", soup_vbpl.find("title").get_text(strip=True) if soup_vbpl.find("title") else "")
for tag in soup_vbpl.find_all(["li", "div", "tr"], class_=lambda c: c and any(k in str(c).lower() for k in ["item", "doc", "van-ban", "news"])):
    a = tag.find("a")
    if a and len(a.get_text(strip=True)) > 15:
        print("  VBPL item:", a.get_text(strip=True)[:80], "->", a.get("href"))
