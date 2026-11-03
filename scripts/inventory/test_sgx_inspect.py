import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)
r = client.get("https://www.sgx.com/securities/company-announcements")
print("SGX page status:", r.status_code, "len:", len(r.content))
soup = BeautifulSoup(r.text, 'html.parser')
scripts = [s['src'] for s in soup.find_all('script', href=False) if s.get('src')]
print("SGX scripts count:", len(scripts))
# check if there are api links in inline scripts
matches = set(re.findall(r'api\.sgx\.com[a-zA-Z0-9_/\.\-\?=&]+|/securities/[a-zA-Z0-9_/\.\-\?=&]+', r.text))
print("SGX api matches:", len(matches))
for m in list(matches)[:10]:
    print(" - SGX match:", m)
