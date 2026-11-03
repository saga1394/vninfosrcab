import httpx
from bs4 import BeautifulSoup
import feedparser

client = httpx.Client(verify=False, follow_redirects=True, timeout=15)

# Check SMF
print("--- SMF ---")
try:
    r = client.get("https://smfederation.org.sg/feed/")
    print("SMF feed status:", r.status_code, len(r.content))
except Exception as e:
    print("SMF error:", type(e).__name__, e)

# Check VCCI
print("\n--- VCCI ---")
try:
    r = client.get("https://vcci.com.vn/tin-tuc")
    print("VCCI status:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=True) if '/tin-tuc/' in a['href'] and len(a.get_text(strip=True)) > 15]
    print("VCCI /tin-tuc/ links:", len(links))
    for a in links[:3]:
        print(" - VCCI link:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("VCCI error:", e)

# Check EtNet
print("\n--- EtNet ---")
try:
    r = client.get("https://www.etnet.com.hk/www/tc/news/categorized_news.php")
    print("EtNet status:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [a for a in soup.find_all('a', href=True) if 'newsid=' in a['href'] and len(a.get_text(strip=True)) > 5]
    print("EtNet links:", len(links))
    for a in links[:3]:
        print(" - EtNet link:", a.get_text(strip=True)[:50], "->", a['href'])
except Exception as e:
    print("EtNet error:", e)

# Check Sogou Weixin
print("\n--- Sogou Weixin ---")
try:
    r = client.get("https://weixin.sogou.com/weixin?type=2&query=%E8%B6%8A%E5%8D%97+%E6%8A%95%E8%B5%84")
    print("Weixin status:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.select('.news-list li a')
    print("Weixin .news-list li a:", len(links))
    for a in links[:3]:
        print(" - Weixin link:", a.get_text(strip=True)[:50], "->", a.get('href'))
except Exception as e:
    print("Weixin error:", e)
