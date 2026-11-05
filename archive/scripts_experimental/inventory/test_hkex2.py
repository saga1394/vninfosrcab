import httpx
import json

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0)
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
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh',
}
r = client.get(url, params=params, headers=headers)
data = r.json()
print("HKEX type:", type(data))
if isinstance(data, str):
    data = json.loads(data)
    print("HKEX inner type:", type(data))
    if isinstance(data, dict):
        print("HKEX keys:", list(data.keys()))
        result = data.get('result', [])
        print("HKEX result count:", len(result))
        for item in result[:3]:
            print(" -", item.get('STOCK_CODE'), item.get('STOCK_NAME'), item.get('TITLE'), item.get('DATE_TIME'))
