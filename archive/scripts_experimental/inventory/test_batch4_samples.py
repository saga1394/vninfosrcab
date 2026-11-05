import sys
import httpx
from bs4 import BeautifulSoup
import json
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

print("=== 1. VITAS News Extraction ===")
try:
    r = client.get("http://www.vietnamtextile.org.vn/tin-tuc-su-kien_p1_1-1_2-1.html")
    print("VITAS news page:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select('.list_news .item_news') or soup.select('.news_item') or soup.select('div.item')
    print("VITAS items found:", len(items))
    if not items:
        # Search all a with href containing tin-tuc
        links = soup.find_all('a', href=re.compile(r'/tin-tuc/|\.html'))
        print("VITAS links with html:", len(links))
        for a in links[:5]:
            t = a.get_text(strip=True)
            if len(t) > 10:
                print(" -", t, "-->", a.get('href'))
except Exception as e:
    print("VITAS error:", e)

print("\n=== 2. VEIA (veia.org.vn) Extraction ===")
try:
    r = client.get("https://veia.org.vn/tin-tuc-su-kien/")
    print("VEIA news page:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.select('article') or soup.select('.post') or soup.select('div.item')
    print("VEIA posts found:", len(posts))
    for p in posts[:3]:
        a = p.find('a')
        t = a.get_text(strip=True) if a else ""
        href = a.get('href') if a else ""
        date = p.find(class_=re.compile(r'date|time'))
        d_str = date.get_text(strip=True) if date else ""
        print(" - VEIA post:", t[:60], "|", d_str, "|", href)
except Exception as e:
    print("VEIA error:", e)

print("\n=== 3. VLA (vla.com.vn) Extraction ===")
try:
    r = client.get("https://vla.com.vn/category/tin-tuc/")
    print("VLA news page:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.select('article') or soup.select('.post') or soup.select('div.item')
    print("VLA posts found:", len(posts))
    for p in posts[:3]:
        a = p.find('a')
        t = a.get_text(strip=True) if a else ""
        href = a.get('href') if a else ""
        print(" - VLA post:", t[:60], "-->", href)
except Exception as e:
    print("VLA error:", e)

print("\n=== 4. VCCI (vcci.com.vn) Extraction ===")
try:
    r = client.get("https://vcci.com.vn/tin-tuc")
    print("VCCI news page:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.select('.news-item') or soup.select('article') or soup.select('.item') or soup.select('div.col-md-4')
    print("VCCI items found:", len(posts))
    for p in posts[:3]:
        a = p.find('a')
        t = a.get_text(strip=True) if a else ""
        href = a.get('href') if a else ""
        print(" - VCCI:", t[:60], "-->", href)
except Exception as e:
    print("VCCI error:", e)

print("\n=== 5. Vilasia (vil.asia) Extraction ===")
try:
    r = client.get("https://vil.asia/an-pham/")
    print("Vilasia publications:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.select('article') or soup.select('.post') or soup.select('.blog-item')
    print("Vilasia posts:", len(posts))
    for p in posts[:3]:
        a = p.find('a')
        t = a.get_text(strip=True) if a else ""
        print(" - Vilasia:", t[:60], "-->", a.get('href') if a else "")
except Exception as e:
    print("Vilasia error:", e)

print("\n=== 6. World Bank Vietnam Extraction ===")
try:
    r = client.get("https://www.worldbank.org/en/country/vietnam/overview")
    print("World Bank VN overview:", r.status_code, len(r.content))
    # Check news endpoint or press release
    r_news = client.get("https://www.worldbank.org/en/country/vietnam/publication/all")
    print("World Bank VN publications:", r_news.status_code, len(r_news.content))
except Exception as e:
    print("World Bank error:", e)

print("\n=== 7. AIIB Projects Extraction ===")
try:
    r = client.get("https://www.aiib.org/en/projects/list/index.html")
    print("AIIB projects page:", r.status_code, len(r.content))
    # Check if there is an AIIB projects API
    r_api = client.get("https://www.aiib.org/en/projects/list/_jcr_content/root/responsivegrid/projectlist.projectlist.json")
    print("AIIB projects API:", r_api.status_code, len(r_api.content))
    if r_api.status_code == 200:
        data = r_api.json()
        print("AIIB project keys/count:", type(data))
except Exception as e:
    print("AIIB error:", e)

print("\n=== 8. PR Newswire APAC (prnasia.com) ===")
try:
    r = client.get("https://www.prnasia.com/rss/all.xml")
    print("PR Newswire RSS:", r.status_code, len(r.content))
    if r.status_code == 200:
        import feedparser
        fp = feedparser.parse(r.content)
        print("PR Newswire RSS entries:", len(fp.entries))
        for ent in fp.entries[:3]:
            print(" - PRN:", ent.title, "|", ent.published, "|", ent.link)
except Exception as e:
    print("PR Newswire error:", e)

print("\n=== 9. Media OutReach ===")
try:
    r = client.get("https://www.media-outreach.com/newsroom/")
    print("Media OutReach newsroom:", r.status_code, len(r.content))
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select('.press-release-item') or soup.select('article') or soup.select('.news-item') or soup.select('div.col-12')
    print("Media OutReach items:", len(items))
    for item in items[:3]:
        a = item.find('a')
        if a and len(a.get_text(strip=True)) > 10:
            print(" - MOR:", a.get_text(strip=True)[:60], "-->", a.get('href'))
except Exception as e:
    print("Media OutReach error:", e)
