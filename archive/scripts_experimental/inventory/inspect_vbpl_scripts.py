import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

r = client.get("https://vbpl.vn/")
soup = BeautifulSoup(r.text, "html.parser")
scripts = soup.find_all("script")
for i, s in enumerate(scripts):
    txt = s.get_text()
    if any(k in txt for k in ["Nghị định", "Thông tư", "Quyết định", "Luật", "doc", "vanban"]):
        print(f"Script #{i} length={len(txt)}: {txt[:200]}...")
