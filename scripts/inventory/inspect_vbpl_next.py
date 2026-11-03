import httpx
from bs4 import BeautifulSoup
import re
import json

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

r = client.get("https://vbpl.vn/")
soup = BeautifulSoup(r.text, "html.parser")
next_data = soup.find("script", id="__NEXT_DATA__")
if next_data:
    print("Found __NEXT_DATA__! Length:", len(next_data.text))
    try:
        data = json.loads(next_data.text)
        print("Keys:", list(data.keys()))
        print("Page props keys:", list(data.get("props", {}).get("pageProps", {}).keys()))
    except Exception as e:
        print("JSON parse error:", e)
else:
    print("No __NEXT_DATA__ tag found. Checking scripts:")
    for s in soup.find_all("script"):
        src = s.get("src", "")
        if src:
            print("  Script:", src)
