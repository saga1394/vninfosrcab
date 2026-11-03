import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.whavietnam.com/en/home")
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.find_all("a", href=True):
    h = a["href"]
    if "487" in h or "486" in h:
        print("FOUND:", repr(h), repr(a.get_text(strip=True)))
