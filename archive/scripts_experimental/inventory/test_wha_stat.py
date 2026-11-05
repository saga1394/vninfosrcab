import httpx
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.whavietnam.com/en/home")
print(r.status_code, len(r.text))
if len(r.text) < 10000:
    print(r.text)
