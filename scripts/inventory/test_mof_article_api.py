import sys
import httpx
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
})

url = "https://www.mof.gov.vn/api/article/reads?offset=0&limit=5"
r = client.get(url)
print("MOF API status:", r.status_code, "ctype:", r.headers.get("content-type"))
print(r.text[:500])
if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
    data = r.json()
    print("Parsed JSON! Items count:", len(data) if isinstance(data, list) else len(data.get("items", [])))
    items = data if isinstance(data, list) else data.get("items", data.get("data", []))
    for it in items[:3]:
        print("  Article:", it.get("title") or it.get("name"), "| date:", it.get("publishedDate") or it.get("createdDate"))
