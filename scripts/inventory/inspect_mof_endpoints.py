import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
matches = set(re.findall(r'["\'](?:api/|/api/)[^"\']+["\']', r.text))
print("Found API endpoints in MOF index:", len(matches))
for m in sorted(matches):
    print(" ", m)
