import sys
import httpx
from bs4 import BeautifulSoup
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers=headers)

# 1. MOF /api/news content
print("=== MOF /api/news ===")
r_mof = client.get("https://www.mof.gov.vn/api/news")
print(r_mof.text[:500])

# 2. EnterpriseSG sitemap or news
print("\n=== ESG robots.txt / sitemap ===")
r_esg_rob = client.get("https://www.enterprisesg.gov.sg/robots.txt")
print(r_esg_rob.text[:400])

# 3. VBPL HTML structure
print("\n=== VBPL HTML analysis ===")
r_vbpl = client.get("https://vbpl.vn/")
soup_vbpl = BeautifulSoup(r_vbpl.text, "html.parser")
# Check all 'a' tags with text length > 10
all_a = soup_vbpl.find_all("a")
print(f"VBPL total <a> tags: {len(all_a)}")
for a in all_a[:15]:
    txt = a.get_text(strip=True)
    if txt:
        print(f"  VBPL a: '{txt}' -> {a.get('href')}")
