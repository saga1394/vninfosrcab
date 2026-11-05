import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
# Find imports or chunk names
chunks = set(re.findall(r'assets/[a-zA-Z0-9_-]+\.js', r.text))
print("MOF chunks:", chunks)

# Find any strings containing "tin" or "news" or "article" or "bai-viet"
keywords = re.findall(r'["\']([^"\']*(?:tintuc|tin-tuc|news|article)[^"\']*)["\']', r.text, re.IGNORECASE)
print("Keywords in MOF JS:", set(keywords)[:10])
