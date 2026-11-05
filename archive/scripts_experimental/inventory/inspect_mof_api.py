import sys
import httpx
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
})

endpoints = [
    "https://www.mof.gov.vn/api/financeNews",
    "https://www.mof.gov.vn/api/pinNews",
    "https://www.mof.gov.vn/api/slideNews",
    "https://www.mof.gov.vn/api/newsBlock1",
]

for ep in endpoints:
    r = client.get(ep)
    print(f"{ep} -> status {r.status_code}, ctype: {r.headers.get('content-type')}")
    if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
        data = r.json()
        print("  JSON keys:", list(data.keys()) if isinstance(data, dict) else f"list of {len(data)}")
        if isinstance(data, dict):
            # check items
            for k in ["data", "items", "content", "result"]:
                if k in data and isinstance(data[k], list):
                    print(f"  First item in '{k}':", data[k][0] if data[k] else "empty")
                    break
