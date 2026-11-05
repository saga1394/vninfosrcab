import sys
import httpx
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
# Let's inspect page chunk
r = client.get("https://vbpl.vn/_next/static/chunks/app/%5Blocale%5D/page-e1d9a6f406fcd305.js")
apis = set(re.findall(r'["\'](/api/[^"\']+|\bhttps?://[^"\']+)["\']', r.text))
print("APIs in page chunk:", len(apis))
for a in apis:
    if "api" in a or "van-ban" in a or "document" in a:
        print("  API/path:", a)

# Let's also check robots.txt and sitemap
r_rob = client.get("https://vbpl.vn/robots.txt")
print("VBPL robots.txt:\n", r_rob.text[:300])

r_site = client.get("https://vbpl.vn/sitemap.xml")
print("VBPL sitemap status:", r_site.status_code, "len:", len(r_site.text))
