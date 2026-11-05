import sys
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en;q=0.9,zh-CN;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

def inspect_links(name, url, pattern=None, limit=5):
    print(f"\n--- {name} ({url}) ---")
    try:
        r = client.get(url)
        print(f"Status: {r.status_code}, Length: {len(r.content)}")
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a', href=True)
        seen = set()
        count = 0
        for a in links:
            href = a['href']
            text = a.get_text(strip=True)
            if not text or len(text) < 10 or text in seen:
                continue
            if pattern and not re.search(pattern, href, re.I):
                continue
            full_url = urljoin(str(r.url), href)
            print(f"  [{count+1}] {text[:60]} -> {full_url}")
            seen.add(text)
            count += 1
            if count >= limit:
                break
    except Exception as e:
        print("  Error:", e)

inspect_links("VEIA", "https://veia.org.vn")
inspect_links("VITAS", "http://www.vietnamtextile.org.vn")
inspect_links("Vilasia", "https://vil.asia")
inspect_links("World Bank VN", "https://www.worldbank.org/en/country/vietnam")
inspect_links("PR Newswire", "https://www.prnasia.com")
inspect_links("Media OutReach", "https://www.media-outreach.com")
inspect_links("Elmet IR", "https://investors.theelmetgroup.com")
inspect_links("Vietnam.vn", "https://www.vietnam.vn/zh-CN/")
