import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.enterprisesg.gov.sg/sitemap.xml")
print("ESG sitemap status:", r.status_code, "len:", len(r.text))
soup = BeautifulSoup(r.text, "xml")
urls = soup.find_all("url")
print(f"Found {len(urls)} URLs in ESG sitemap.")
media_urls = [u for u in urls if any(k in (u.find("loc").text if u.find("loc") else "").lower() for k in ["media", "news", "release", "press", "vietnam"])]
print(f"Found {len(media_urls)} media/news URLs. First 5:")
for u in media_urls[:5]:
    loc = u.find("loc").text if u.find("loc") else ""
    lastmod = u.find("lastmod").text if u.find("lastmod") else ""
    print(f"  loc: {loc} | lastmod: {lastmod}")
