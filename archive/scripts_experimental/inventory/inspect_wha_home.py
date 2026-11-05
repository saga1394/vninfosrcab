import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.whavietnam.com/en/home")
soup = BeautifulSoup(r.text, "html.parser")
wha_entries = []
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "/updates/company-news/" in h or "/updates/csr-news/" in h:
        raw_text = a.get_text(" ", strip=True)
        # Look for date like 29 June 2026 or 04 June 2026
        m = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', raw_text)
        date = m.group(1) if m else ""
        title = raw_text.replace(date, "").strip() if date else raw_text
        if len(title) > 20 and not any(e["url"] == h for e in wha_entries):
            wha_entries.append({
                "title": title,
                "pubdate": date,
                "url": h,
                "snippet": f"WHA Vietnam update: {title}"
            })

print(f"Extracted {len(wha_entries)} WHA news items from homepage:")
for e in wha_entries[:4]:
    print(" ", e)
