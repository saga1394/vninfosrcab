import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

r = httpx.get('https://www.worldbank.org/en/country/vietnam', verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=True)
for a in links:
    if 'worldbank.org' in a['href'] or a['href'].startswith('/'):
        t = a.get_text(strip=True)
        if any(w in a['href'].lower() for w in ['press-release', 'news', 'publication', 'overview', 'brief']):
            print(f"WB link: {t[:50]} -> {a['href']}")
