import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)
r = client.get("https://dart.fss.or.kr/", headers=headers)
print("DART home status:", r.status_code, "len:", len(r.content))
soup = BeautifulSoup(r.text, 'html.parser')
# Find today's disclosures on homepage
tables = soup.select('table')
print("DART tables:", len(tables))
for t in tables:
    for tr in t.select('tr')[:5]:
        tds = [td.get_text(strip=True) for td in tr.select('th, td')]
        if tds:
            print(" - DART row:", tds[:4])
