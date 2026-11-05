import sys
import httpx
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json'
})

url = "https://www.mof.gov.vn/api/article/reads?offset=0&limit=5"
r = client.post(url, json={})
print("MOF POST status:", r.status_code, "ctype:", r.headers.get("content-type"))
print(r.text[:500])
if r.status_code == 200:
    try:
        data = r.json()
        print("Success! JSON data:", list(data.keys()) if isinstance(data, dict) else len(data))
    except Exception as e:
        print("Not json:", e)
