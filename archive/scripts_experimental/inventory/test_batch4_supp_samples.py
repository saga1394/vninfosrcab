import sys
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

print("--- 1. Testing Sina Finance ---")
try:
    r = client.get("https://finance.sina.com.cn")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'sina\.com\.cn.*(?:\.shtml|/doc-)')) if len(a.get_text(strip=True)) > 12]
    print(f"Sina Finance links: {len(links)}")
    for a in links[:3]:
        print(" - Sina:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("Sina error:", e)

print("\n--- 2. Testing NetEase Finance ---")
try:
    r = client.get("https://money.163.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'money\.163\.com/\d+')) if len(a.get_text(strip=True)) > 12]
    print(f"NetEase Finance links: {len(links)}")
    for a in links[:3]:
        print(" - NetEase:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("NetEase error:", e)

print("\n--- 3. Testing Sohu Finance ---")
try:
    r = client.get("https://business.sohu.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'sohu\.com/a/\d+')) if len(a.get_text(strip=True)) > 12]
    print(f"Sohu Finance links: {len(links)}")
    for a in links[:3]:
        print(" - Sohu:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("Sohu error:", e)

print("\n--- 4. Testing Tencent News ---")
try:
    r = client.get("https://news.qq.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'news\.qq\.com/rain/a/')) if len(a.get_text(strip=True)) > 10]
    print(f"Tencent News links: {len(links)}")
    for a in links[:3]:
        print(" - Tencent:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("Tencent error:", e)

print("\n--- 5. Testing EtNet 经济通 ---")
try:
    r = client.get("https://www.etnet.com.hk/www/tc/news/categorized_news.php")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'news_detail\.php\?newsid=')) if len(a.get_text(strip=True)) > 8]
    print(f"EtNet links: {len(links)}")
    for a in links[:3]:
        print(" - EtNet:", a.get_text(strip=True)[:50], "->", urljoin("https://www.etnet.com.hk/www/tc/news/", a['href']))
except Exception as e:
    print("EtNet error:", e)

print("\n--- 6. Testing PR Newswire ---")
try:
    r = client.get("https://www.prnasia.com/releases/apac/")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'/story/')) if len(a.get_text(strip=True)) > 12]
    print(f"PR Newswire links: {len(links)}")
    for a in links[:3]:
        print(" - PRN:", a.get_text(strip=True)[:50], "->", urljoin("https://www.prnasia.com", a['href']))
except Exception as e:
    print("PR Newswire error:", e)

print("\n--- 7. Testing Media OutReach ---")
try:
    r = client.get("https://www.media-outreach.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'/release/|/news/|/article/')) if len(a.get_text(strip=True)) > 12]
    print(f"Media OutReach links: {len(links)}")
    for a in links[:3]:
        print(" - MOR:", a.get_text(strip=True)[:50], "->", urljoin("https://www.media-outreach.com", a['href']))
except Exception as e:
    print("Media OutReach error:", e)

print("\n--- 8. Testing AIIB Projects List ---")
try:
    r = client.get("https://www.aiib.org/en/projects/list/index.html")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=re.compile(r'/projects/details/')) if len(a.get_text(strip=True)) > 5]
    print(f"AIIB project links: {len(links)}")
    for a in links[:3]:
        print(" - AIIB:", a.get_text(strip=True)[:50], "->", urljoin("https://www.aiib.org", a['href']))
except Exception as e:
    print("AIIB error:", e)
