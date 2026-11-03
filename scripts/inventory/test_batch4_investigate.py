import sys
import httpx
from bs4 import BeautifulSoup
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

print("--- 1. Testing SZSE ---")
for u in ["http://www.szse.cn", "https://www.szse.cn", "https://www.szse.cn/disclosure/listed/notice/index.html"]:
    try:
        r = client.get(u)
        print(f"SZSE {u}: {r.status_code} len={len(r.content)}")
    except Exception as e:
        print(f"SZSE {u}: {type(e).__name__} - {e}")

print("\n--- 2. Testing SEC EDGAR with SEC-compliant User-Agent ---")
sec_headers = {
    'User-Agent': 'VnInvestmentResearch AdminContact@vnresearch.org',
    'Accept': 'application/json, text/html, */*',
}
try:
    r = client.get("https://efts.sec.gov/LATEST/search-index?q=Vietnam", headers=sec_headers)
    print(f"SEC EDGAR search API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        print("SEC hits total:", data.get('hits', {}).get('total', {}))
        hits = data.get('hits', {}).get('hits', [])[:3]
        for h in hits:
            src = h.get('_source', {})
            print(" - Hit:", src.get('display_names'), src.get('form'), src.get('file_date'))
except Exception as e:
    print(f"SEC EDGAR: {e}")

print("\n--- 3. Testing VITAS ---")
for u in ["http://vietnamtextile.org.vn", "https://vietnamtextile.org.vn", "http://vitas.org.vn", "https://vitas.org.vn"]:
    try:
        r = client.get(u)
        print(f"VITAS {u}: {r.status_code} len={len(r.content)} final={r.url}")
    except Exception as e:
        print(f"VITAS {u}: {type(e).__name__} - {e}")

print("\n--- 4. Testing MOPS (Taiwan) ---")
try:
    # MOPS web
    r = client.get("https://mops.twse.com.tw/mops/web/index")
    print(f"MOPS index: {r.status_code} len={len(r.content)} url={r.url}")
except Exception as e:
    print(f"MOPS error: {e}")

print("\n--- 5. Testing SBF & SMF (Singapore) ---")
for u in ["https://www.sbf.org.sg", "http://www.sbf.org.sg", "https://www.smfederation.org.sg", "http://www.smfederation.org.sg"]:
    try:
        r = client.get(u)
        print(f"SG Org {u}: {r.status_code} len={len(r.content)} url={r.url}")
    except Exception as e:
        print(f"SG Org {u}: {type(e).__name__} - {e}")

print("\n--- 6. Testing ADB ---")
try:
    r = client.get("https://www.adb.org/where-we-work/viet-nam/projects-results")
    print(f"ADB: {r.status_code} len={len(r.content)} server={r.headers.get('Server')}")
except Exception as e:
    print(f"ADB error: {e}")

print("\n--- 7. Testing CNINFO search API ---")
try:
    cninfo_api = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    payload = {
        "pageNum": 1,
        "pageSize": 5,
        "column": "szse",
        "tabName": "fulltext",
        "plateau": "",
        "stock": "",
        "searchkey": "越南",
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": "2024-01-01~2026-11-02"
    }
    r = client.post(cninfo_api, data=payload)
    print(f"CNINFO API: {r.status_code} len={len(r.content)}")
    if r.status_code == 200:
        data = r.json()
        annList = data.get("announcements", [])
        print(f"CNINFO announcements count: {len(annList)}, total: {data.get('totalAnnouncement')}")
        for ann in annList[:3]:
            print(f" - [{ann.get('secCode')}] {ann.get('secName')}: {ann.get('announcementTitle')} ({ann.get('announcementTime')})")
except Exception as e:
    print(f"CNINFO error: {e}")
