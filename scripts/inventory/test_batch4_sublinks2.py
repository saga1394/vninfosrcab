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

# 1. NetEase Finance
r = client.get("https://money.163.com")
soup = BeautifulSoup(r.text, 'html.parser')
print("NetEase links sample:")
for a in [a for a in soup.find_all('a', href=True) if len(a.get_text(strip=True)) > 12][:5]:
    print(" - NetEase:", a.get_text(strip=True)[:50], "->", a['href'])

# 2. Tencent News
r = client.get("https://news.qq.com")
soup = BeautifulSoup(r.text, 'html.parser')
print("\nTencent links sample:")
for a in [a for a in soup.find_all('a', href=True) if len(a.get_text(strip=True)) > 12][:5]:
    print(" - Tencent:", a.get_text(strip=True)[:50], "->", a['href'])

# 3. PR Newswire
r = client.get("https://www.prnasia.com")
soup = BeautifulSoup(r.text, 'html.parser')
print("\nPR Newswire links sample:")
for a in [a for a in soup.find_all('a', href=True) if len(a.get_text(strip=True)) > 15][:5]:
    print(" - PRN:", a.get_text(strip=True)[:50], "->", a['href'])

# 4. AIIB
r = client.get("https://www.aiib.org/en/projects/list/index.html")
soup = BeautifulSoup(r.text, 'html.parser')
print("\nAIIB links sample:")
for a in [a for a in soup.find_all('a', href=True) if '/projects/' in a['href']][:5]:
    print(" - AIIB:", a.get_text(strip=True)[:50], "->", a['href'])
