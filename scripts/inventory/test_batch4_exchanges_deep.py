import sys
import httpx
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, text/html, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

print("=== 1. SSE (上交所) Announcements Search ===")
try:
    # SSE announcement search endpoint:
    # http://query.sse.com.cn/security/stock/queryCompanyBulletin.do
    # Let's test without keyword or with keyword and correct parameters
    url = "http://query.sse.com.cn/security/stock/queryCompanyBulletin.do"
    params = {
        "isPagination": "true",
        "pageHelp.pageSize": "5",
        "pageHelp.pageNo": "1",
        "pageHelp.beginPage": "1",
        "pageHelp.cacheSize": "1",
        "pageHelp.endPage": "5",
        "_": str(int(time.time() * 1000))
    }
    h = dict(headers)
    h['Referer'] = 'http://www.sse.com.cn/disclosure/listedinfo/announcement/'
    r = client.get(url, params=params, headers=h)
    print("SSE latest announcements status:", r.status_code, "len:", len(r.content))
    if r.status_code == 200:
        data = r.json()
        print("SSE total latest:", data.get('pageHelp', {}).get('total'))
        for item in data.get('pageHelp', {}).get('data', [])[:3]:
            print(f" - [{item.get('SECURITY_CODE')}] {item.get('SECURITY_NAME')}: {item.get('BULLETIN_TITLE')} ({item.get('BULLETIN_DATE')})")
except Exception as e:
    print("SSE error:", e)

print("\n=== 2. BSE (北交所) Announcements Query ===")
try:
    url = "https://www.bse.cn/disclosureInfoController/infoResult.do"
    # let's test BSE disclosure list
    payload = {
        "disclosureType": "5",
        "page": "0",
        "pageSize": "5",
        "sortType": "desc"
    }
    h = dict(headers)
    h['Referer'] = 'https://www.bse.cn/disclosure/announcement.html'
    r = client.post(url, data=payload, headers=h)
    print("BSE status:", r.status_code, "len:", len(r.content))
    if r.status_code == 200:
        txt = r.text.strip()
        if txt.startswith("null(") and txt.endswith(")"):
            txt = txt[5:-1]
        data = json.loads(txt)
        if isinstance(data, list) and len(data) > 0 and 'data' in data[0]:
            items = data[0]['data'].get('content', [])
            print("BSE announcements count:", len(items))
            for item in items[:3]:
                print(f" - [{item.get('companyCode')}] {item.get('companyName')}: {item.get('disclosureTitle')} ({item.get('publishDate')})")
        else:
            print("BSE data structure:", type(data))
except Exception as e:
    print("BSE error:", e)

print("\n=== 3. TDnet (JPX) Daily Disclosures ===")
try:
    # Today is 20261102 (or let's check recent dates like 20261030)
    for dt_str in ["20261102", "20261030", "20261029"]:
        url = f"https://www.release.tdnet.info/inbs/I_list_001_{dt_str}.html"
        r = client.get(url)
        print(f"TDnet {dt_str}: status {r.status_code}, len {len(r.content)}")
        if r.status_code == 200 and len(r.content) > 1000:
            soup = BeautifulSoup(r.content, 'html.parser', from_encoding='shift_jis')
            rows = soup.select('table#main-list-table tr') or soup.select('table tr')
            valid_rows = []
            for tr in rows:
                tds = [td.get_text(strip=True) for td in tr.select('td')]
                if len(tds) >= 4 and any(c.isdigit() for c in tds[1] if len(tds)>1):
                    valid_rows.append(tds)
            print(f"TDnet valid disclosure rows for {dt_str}: {len(valid_rows)}")
            for v in valid_rows[:3]:
                print(" - TDnet item:", v[:4])
            if valid_rows:
                break
except Exception as e:
    print("TDnet error:", e)

print("\n=== 4. SGX Announcements Detailed ===")
try:
    url = "https://api.sgx.com/securities/v1.1/announcements?pagestart=0&pagesize=5"
    h = dict(headers)
    h['Referer'] = 'https://www.sgx.com/securities/company-announcements'
    r = client.get(url, headers=h)
    print("SGX API status:", r.status_code, "len:", len(r.content))
    if r.status_code == 200:
        data = r.json()
        print("SGX keys:", list(data.keys()))
        data_field = data.get('data')
        print("SGX 'data' type:", type(data_field))
        if isinstance(data_field, list):
            for item in data_field[:3]:
                print(f" - {item.get('company_name')}: {item.get('title')} ({item.get('submission_date')})")
        elif isinstance(data_field, dict):
            print("SGX data dict keys:", list(data_field.keys()))
            items = data_field.get('announcements', []) or data_field.get('items', [])
            print("SGX announcements list:", len(items))
            for item in items[:3]:
                print(f" - {item.get('company_name')}: {item.get('title')} ({item.get('submission_date')})")
except Exception as e:
    print("SGX error:", e)

print("\n=== 5. DART (Korea) Daily Disclosures ===")
try:
    # DART today's disclosure list
    # URL: https://dart.fss.or.kr/dsac001/search.ax
    url = "https://dart.fss.or.kr/dsac001/search.ax"
    params = {
        "currentPage": "1",
        "maxResults": "15",
        "maxLinks": "10",
        "sort": "date",
        "series": "desc"
    }
    r = client.post(url, data=params)
    print("DART search.ax status:", r.status_code, "len:", len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.select('table tbody tr') or soup.select('tr')
    print("DART rows found:", len(rows))
    for tr in rows[:4]:
        tds = [td.get_text(strip=True) for td in tr.select('td')]
        if tds:
            print(" - DART item:", tds[:4])
except Exception as e:
    print("DART error:", e)
