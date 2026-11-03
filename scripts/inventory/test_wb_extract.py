import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

r = httpx.get('https://www.worldbank.org/en/country/vietnam', verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=True)
wb_items = []
for a in links:
    h = a['href']
    t = a.get_text(strip=True)
    if ('news/press-release' in h or 'publication' in h) and len(t) > 15:
        if not any(t == item['title'] for item in wb_items):
            wb_items.append({"title": t, "url": h})

print("World Bank Vietnam items found:", len(wb_items))
for item in wb_items[:5]:
    print(f" - {item['title']} | {item['url']}")
