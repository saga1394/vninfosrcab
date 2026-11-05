import sys
import httpx
from bs4 import BeautifulSoup
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

# Test titleSearchServlet.do or search
try:
    url = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
    params = {
        "sortDir": "0",
        "sortByOptions": "DateTime",
        "category": "0",
        "market": "SEHK",
        "documentType": "-1",
        "t1code": "-2",
        "t2Gcode": "-2",
        "t2code": "-2",
        "title": "越南",
        "lang": "zh"
    }
    r = client.get(url, params=params)
    print("HKEX titleSearchServlet status:", r.status_code, "len:", len(r.content))
    if r.status_code == 200:
        data = r.json()
        print("HKEX results count:", data.get('totalRecords'))
        records = data.get('result', [])
        for rec in records[:3]:
            print(" - HKEX:", rec.get('stockCode'), rec.get('stockName'), rec.get('title'), rec.get('date'))
except Exception as e:
    print("HKEX servlet error:", e)
