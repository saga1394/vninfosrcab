import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

# MOPS t05st02:
# Payload for today's market announcements:
url = "https://mops.twse.com.tw/mops/web/ajax_t05st02"
payload = {
    "encodeColum": "Y",
    "step": "1",
    "firstin": "1",
    "off": "1",
    "TYPEK": "sii",
    "year": "113",
    "month": "11",
    "day": "02"
}
h = dict(headers)
h['Referer'] = 'https://mops.twse.com.tw/mops/web/t05st02'
r = client.post(url, data=payload, headers=h)
print("MOPS status:", r.status_code, "len:", len(r.content))
soup = BeautifulSoup(r.text, 'html.parser')
rows = soup.select('table tr')
print("MOPS table rows:", len(rows))
for tr in rows[:5]:
    tds = [td.get_text(strip=True) for td in tr.select('td, th')]
    if tds:
        print(" - MOPS:", tds[:5])
