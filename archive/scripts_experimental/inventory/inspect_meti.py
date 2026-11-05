import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.meti.gov.sg/newsroom/press-releases")
print("METI newsroom status:", r.status_code, "len:", len(r.text))
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    print("Title:", soup.find("title").get_text(strip=True) if soup.find("title") else "")
    for a in soup.find_all("a", href=True):
        t = a.get_text(strip=True)
        if len(t) > 20 and not "trusted" in t.lower():
            print("  Press release:", t[:80], "->", a["href"])
else:
    # check robots.txt
    r_rob = client.get("https://www.meti.gov.sg/robots.txt")
    print("METI robots.txt:", r_rob.text[:300])
