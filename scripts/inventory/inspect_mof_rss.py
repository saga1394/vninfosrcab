import httpx
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/rss")
print(r.headers.get("content-type"))
print(r.text[:300])
