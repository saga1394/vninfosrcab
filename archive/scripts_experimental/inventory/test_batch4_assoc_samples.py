import sys
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

# 1. VEIA news
r = client.get("https://veia.org.vn/category/tin-tuc-su-kien/")
soup = BeautifulSoup(r.text, 'html.parser')
print(f"VEIA news ({r.status_code}):")
for p in soup.select('article, .post, .elementor-post'):
    a = p.find('a')
    if a and len(a.get_text(strip=True)) > 10:
        print("  -", a.get_text(strip=True)[:60], "->", a.get('href'))

# 2. Vilasia insights
r = client.get("https://vil.asia/insights/")
soup = BeautifulSoup(r.text, 'html.parser')
print(f"\nVilasia insights ({r.status_code}):")
for p in soup.select('article, .post, a.post-card, .elementor-post, div.post'):
    a = p if p.name == 'a' else p.find('a')
    if a and len(a.get_text(strip=True)) > 5:
        print("  -", a.get_text(strip=True)[:60], "->", a.get('href'))
if not soup.select('article, .post'):
    for a in soup.find_all('a', href=re.compile(r'/insights/|/news/')):
        if len(a.get_text(strip=True)) > 5 and a.get('href') != '/insights/':
            print("  - link:", a.get_text(strip=True)[:60], "->", a.get('href'))
