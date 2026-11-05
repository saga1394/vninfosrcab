import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

r = httpx.get('https://www.worldbank.org/ext/en/country/vietnam', verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a', href=True):
    t = a.get_text(strip=True)
    if len(t) > 5:
        print(f"WB link: {t[:60]} -> {a['href']}")
