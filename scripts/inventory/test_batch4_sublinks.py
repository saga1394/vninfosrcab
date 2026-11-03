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

# VEIA:
r = client.get("https://veia.org.vn")
soup = BeautifulSoup(r.text, 'html.parser')
print("VEIA menu links:")
for a in soup.select('nav a, header a, .menu a'):
    href = a.get('href')
    text = a.get_text(strip=True)
    if text and href and href != '#':
        print(f"  VEIA: {text} -> {href}")

# VITAS:
r = client.get("http://www.vietnamtextile.org.vn/default_p1_1-1_2-1.html")
soup = BeautifulSoup(r.text, 'html.parser')
print("\nVITAS menu links:")
for a in soup.select('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if any(k in href.lower() for k in ['tin-tuc', 'news', 'su-kien', 'hoat-dong']) and len(text) > 5:
        print(f"  VITAS: {text} -> {href}")

# Vilasia:
r = client.get("https://vil.asia")
soup = BeautifulSoup(r.text, 'html.parser')
print("\nVilasia menu links:")
for a in soup.select('nav a, header a, footer a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if text:
        print(f"  Vilasia: {text} -> {href}")
