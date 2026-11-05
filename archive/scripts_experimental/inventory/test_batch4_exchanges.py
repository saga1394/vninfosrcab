import sys
import httpx
from bs4 import BeautifulSoup
import json
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

print("--- 1. SSE (上交所) Announcements Query ---")
try:
    sse_url = "http://query.sse.com.cn/security/stock/queryCompanyBulletin.do"
    sse_params = {
        "isPagination": "true",
        "pageHelp.pageSize": "5",
        "pageHelp.pageNo": "1",
        "pageHelp.beginPage": "1",
        "pageHelp.cacheSize": "1",
        "pageHelp.endPage": "5",
        "keyWord": "越南",
        "_": str(int(time.time() * 1000))
    }
    sse_headers = dict(headers)
    sse_headers['Referer'] = 'http://www.sse.com.cn/disclosure/listedinfo/announcement/'
    r = client.get(sse_url, params=sse_params, headers=sse_headers)
    print(f"SSE API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        print("SSE total:", data.get('pageHelp', {}).get('total'))
        for item in data.get('pageHelp', {}).get('data', [])[:3]:
            print(f" - [{item.get('SECURITY_CODE')}] {item.get('SECURITY_NAME')}: {item.get('BULLETIN_TITLE')} ({item.get('BULLETIN_DATE')})")
except Exception as e:
    print(f"SSE error: {e}")

print("\n--- 2. SZSE (深交所) Announcements Query ---")
try:
    szse_url = "https://www.szse.cn/api/disc/announcement/annList"
    szse_payload = {
        "seDate": ["", ""],
        "searchKey": ["越南"],
        "channelCode": ["listedNotice_disc"],
        "pageSize": 5,
        "pageNum": 1
    }
    szse_headers = dict(headers)
    szse_headers['Referer'] = 'https://www.szse.cn/disclosure/listed/notice/index.html'
    szse_headers['Content-Type'] = 'application/json'
    r = client.post(szse_url, json=szse_payload, headers=szse_headers)
    print(f"SZSE API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        print("SZSE announce count:", len(data.get('data', [])))
        for item in data.get('data', [])[:3]:
            print(f" - [{item.get('secCode')}] {item.get('secName')}: {item.get('title')} ({item.get('publishTime')})")
except Exception as e:
    print(f"SZSE error: {e}")

print("\n--- 3. BSE (北交所) Announcements Query ---")
try:
    bse_url = "https://www.bse.cn/disclosureInfoController/infoResult.do"
    bse_params = {
        "disclosureType": "5",
        "page": "0",
        "pageSize": "5",
        "keyword": "越南",
        "sortType": "desc"
    }
    bse_headers = dict(headers)
    bse_headers['Referer'] = 'https://www.bse.cn/disclosure/announcement.html'
    r = client.post(bse_url, data=bse_params, headers=bse_headers)
    print(f"BSE API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        print("BSE response snippet:", r.text[:200])
except Exception as e:
    print(f"BSE error: {e}")

print("\n--- 4. HKEXnews (港交所披露易) ---")
try:
    hkex_url = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"
    hkex_headers = dict(headers)
    hkex_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    r = client.get(hkex_url, headers=hkex_headers)
    print(f"HKEXnews title search page: {r.status_code} len={len(r.content)}")
    # Also check latest announcements endpoint
    hkex_latest = "https://www1.hkexnews.hk/search/prefix.do?lang=ZH&type=A"
    r2 = client.get(hkex_latest, headers=hkex_headers)
    print(f"HKEXnews prefix.do: {r2.status_code} len={len(r2.content)}")
except Exception as e:
    print(f"HKEXnews error: {e}")

print("\n--- 5. MOPS (台湾) ---")
try:
    mops_url = "https://mops.twse.com.tw/mops/web/ajax_t05st02"
    mops_payload = {
        "encodeColum": "Y",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "TYPEK": "sii",
        "year": "113",
        "month": "11"
    }
    mops_headers = dict(headers)
    mops_headers['Referer'] = 'https://mops.twse.com.tw/mops/web/t05st02'
    r = client.post(mops_url, data=mops_payload, headers=mops_headers)
    print(f"MOPS ajax_t05st02: {r.status_code} len={len(r.content)}")
    if len(r.content) < 500:
        print("MOPS text:", r.text[:300])
except Exception as e:
    print(f"MOPS error: {e}")

print("\n--- 6. SGX (新加坡交易所) ---")
try:
    sgx_api = "https://api.sgx.com/securities/v1.1/announcements?pagestart=0&pagesize=5"
    sgx_headers = dict(headers)
    sgx_headers['Referer'] = 'https://www.sgx.com/securities/company-announcements'
    r = client.get(sgx_api, headers=sgx_headers)
    print(f"SGX API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        print("SGX announcements:", len(data.get('data', [])))
        for item in data.get('data', [])[:3]:
            print(f" - {item.get('company_name')}: {item.get('title')} ({item.get('submission_date')})")
except Exception as e:
    print(f"SGX error: {e}")

print("\n--- 7. DART (韩国) ---")
try:
    dart_url = "https://dart.fss.or.kr/dsac001/main.do"
    r = client.get(dart_url)
    print(f"DART main: {r.status_code} len={len(r.content)}")
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.select('table.tblList tbody tr') or soup.select('table tr')
    print(f"DART table rows: {len(rows)}")
    for tr in rows[:3]:
        tds = [td.get_text(strip=True) for td in tr.select('td')]
        if tds:
            print(" - DART row:", tds[:3])
except Exception as e:
    print(f"DART error: {e}")

print("\n--- 8. JPX / TDnet (日本) ---")
try:
    tdnet_url = "https://www.release.tdnet.info/inbs/I_main_00.html"
    r = client.get(tdnet_url)
    print(f"TDnet main: {r.status_code} len={len(r.content)}")
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='shift_jis')
    rows = soup.select('tr')
    print(f"TDnet rows count: {len(rows)}")
    sample_items = []
    for tr in rows:
        tds = [td.get_text(strip=True) for td in tr.select('td')]
        if len(tds) >= 4 and any(tds[0].endswith(':') or '/' in tds[0] for _ in [1]):
            sample_items.append(tds)
    print(f"TDnet parsed items: {len(sample_items)}")
    for s in sample_items[:3]:
        print(" - TDnet:", s[:4])
except Exception as e:
    print(f"TDnet error: {e}")

print("\n--- 9. NSE & BSE (印度) ---")
try:
    nse_url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    nse_headers = dict(headers)
    nse_headers['Referer'] = 'https://www.nseindia.com/'
    # NSE often requires landing page cookie first
    client.get("https://www.nseindia.com/", headers=headers)
    r = client.get(nse_url, headers=nse_headers)
    print(f"NSE API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        print("NSE records:", len(data))
except Exception as e:
    print(f"NSE error: {e}")

try:
    bse_url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?strCat=-1&strPrevDate=&strScrip=&strSearch=P&strToDate=&strType=C"
    bse_headers = dict(headers)
    bse_headers['Referer'] = 'https://www.bseindia.com/'
    r = client.get(bse_url, headers=bse_headers)
    print(f"BSE API: {r.status_code} len={len(r.content)}")
except Exception as e:
    print(f"BSE error: {e}")
