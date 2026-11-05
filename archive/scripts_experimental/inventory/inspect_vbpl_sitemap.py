import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://vbpl.vn/sitemap.xml")
print(r.text)
