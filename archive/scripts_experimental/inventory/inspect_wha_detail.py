import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.whavietnam.com/en/updates/company-news")
print("Status:", r.status_code, "len:", len(r.text))
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if len(t) > 20 and not "explore" in t.lower():
        print("  WHA a:", t[:80], "->", h)
