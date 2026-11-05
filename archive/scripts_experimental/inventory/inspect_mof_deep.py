import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# Let's inspect the bundle js of MOF to see what API it calls
r_js = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
# Find strings like axios or fetch or baseUrl or api
matches = set(re.findall(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_.-]+)*', r_js.text))
print("URLs in MOF JS:")
for m in matches:
    if "mof.gov.vn" in m or "api" in m:
        print(" ", m)

# Also check if mof has rss
r_rss = client.get("https://www.mof.gov.vn/rss")
print("MOF /rss status:", r_rss.status_code)
