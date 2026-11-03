import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://vbpl.vn/sitemap/1.xml")
print("Sitemap 1 status:", r.status_code, "len:", len(r.text))
soup = BeautifulSoup(r.text, "xml")
urls = soup.find_all("url")
print(f"Found {len(urls)} URLs in sitemap 1. First 5:")
for u in urls[:5]:
    loc = u.find("loc").text if u.find("loc") else ""
    lastmod = u.find("lastmod").text if u.find("lastmod") else ""
    print(f"  loc: {loc} | lastmod: {lastmod}")
