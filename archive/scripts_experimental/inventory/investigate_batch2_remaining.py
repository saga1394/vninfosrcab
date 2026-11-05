"""
Investigate the remaining 19 sources of Batch 2 to find working feeds, sitemaps, or HTML DOM selectors.
"""

import sys
import time
import subprocess
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(
    verify=False,
    follow_redirects=True,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    },
    timeout=12.0
)

def test_curl(url):
    try:
        res = subprocess.run(
            ["curl.exe", "-s", "-i", "-k", "-L", "--connect-timeout", "10",
             "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
             url],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        first_line = res.stdout.splitlines()[0] if res.stdout else "EMPTY"
        return first_line, res.stdout[:5000]
    except Exception as e:
        return f"ERROR: {e}", ""

print("=== 1. VOV (vov.vn) ===")
# Try curl on vov.vn
status, out = test_curl("https://vov.vn")
print("vov.vn curl:", status)
status_rss, out_rss = test_curl("https://vov.vn/rss.vov")
print("vov.vn/rss.vov curl:", status_rss)
try:
    r = client.get("https://vov.vn", headers={"User-Agent": "curl/7.88.1"})
    print("vov.vn UA curl:", r.status_code)
except Exception as e:
    print("vov.vn error:", e)

print("\n=== 2. Báo Đầu tư (baodautu.vn) ===")
# Inspect HTML DOM for baodautu.vn
r = client.get("https://baodautu.vn/dau-tu-c4/")
print("baodautu.vn/dau-tu-c4/:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select(".story, .timeline, article, .box-category-item, a.title")
    print("baodautu article count:", len(articles))
    for a in soup.select("a.title")[:5]:
        print("  Title:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 3. CafeLand (cafeland.vn) ===")
r = client.get("https://cafeland.vn/tin-tuc/")
print("cafeland tin-tuc:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".box-category-item a, .news-title a, h3 a, h2 a")[:5]:
    if a.get_text(strip=True):
        print("  CafeLand:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 4. Diễn đàn Doanh nghiệp (diendandoanhnghiep.vn) ===")
r = client.get("https://diendandoanhnghiep.vn/kinh-te.html")
print("diendandoanhnghiep:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for h in soup.select("h3.title-news a, .story a, h2 a, h3 a")[:5]:
    if h.get_text(strip=True):
        print("  DDDN:", h.get_text(strip=True), "->", h.get("href"))

print("\n=== 5. Báo Hải Phòng (baohaiphong.vn) ===")
r = client.get("https://baohaiphong.vn/kinh-te/")
print("baohaiphong:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for h in soup.select(".story h2 a, .story h3 a, article a, h3 a")[:5]:
    if h.get_text(strip=True):
        print("  BHP:", h.get_text(strip=True), "->", h.get("href"))

print("\n=== 6. Báo Bắc Ninh (baobacninh.com.vn vs baobacninh.vn) ===")
try:
    r = client.get("https://baobacninh.com.vn")
    print("baobacninh.com.vn:", r.status_code)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.select("a.title, .story a, h3 a, h2 a")[:5]:
        if a.get_text(strip=True):
            print("  BBN:", a.get_text(strip=True), "->", a.get("href"))
except Exception as e:
    print("baobacninh.com.vn error:", e)

print("\n=== 7. Báo Hưng Yên (baohungyen.vn) ===")
r = client.get("https://baohungyen.vn/kinh-te/")
print("baohungyen:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("h2 a, h3 a, .title a, article a")[:5]:
    if a.get_text(strip=True):
        print("  BHY:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 8. Báo Thái Nguyên (baothainguyen.vn/rss) ===")
r = client.get("https://baothainguyen.vn/rss")
print("baothainguyen/rss:", r.status_code)
fp = feedparser.parse(r.content)
print("entries:", len(fp.entries))
if fp.entries:
    print("  BTN sample:", fp.entries[0].title, fp.entries[0].published)

print("\n=== 9. Báo Đà Nẵng (baodanang.vn) ===")
r = client.get("https://baodanang.vn/channel/5404/")
print("baodanang channel 5404:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("h2 a, h3 a, .title a, .media-heading a")[:5]:
    if a.get_text(strip=True):
        print("  BDN:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 10. Báo Tây Ninh (baotayninh.vn) ===")
r = client.get("https://baotayninh.vn/kinh-te-c10/")
print("baotayninh:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("h2 a, h3 a, .title a, article a")[:5]:
    if a.get_text(strip=True):
        print("  BTN:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 11. Báo Đồng Nai (baodongnai.com.vn) ===")
r = client.get("https://baodongnai.com.vn/kinh-te/")
print("baodongnai:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("h2 a, h3 a, .title a, article a")[:5]:
    if a.get_text(strip=True):
        print("  BDN:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 12. DealStreetAsia (dealstreetasia.com) ===")
r = client.get("https://www.dealstreetasia.com/section/indochina/")
print("dealstreetasia indochina:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".post-title a, h2 a, h3 a")[:5]:
    if a.get_text(strip=True):
        print("  DSA:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 13. The Business Times (businesstimes.com.sg) ===")
r = client.get("https://www.businesstimes.com.sg/international/asean")
print("businesstimes:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".card-title a, h2 a, h3 a, .media-body a")[:5]:
    if a.get_text(strip=True):
        print("  BT:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 14. Financial News Korea (fnnews.com) ===")
status, out = test_curl("https://www.fnnews.com")
print("fnnews curl:", status)
r = client.get("https://www.fnnews.com/section/002001000")
print("fnnews section:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select(".tit a, .art_title a, dt a, h2 a, h3 a")[:5]:
    if a.get_text(strip=True):
        print("  FN:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 15. The Economic Times ===")
status, out = test_curl("https://economictimes.indiatimes.com")
print("economictimes curl:", status)

print("\n=== 16. TechNode Global ===")
status, out = test_curl("https://technode.global/feed/")
print("technode curl:", status)

print("\n=== 17. Manila Bulletin ===")
status, out = test_curl("https://mb.com.ph")
print("mb.com.ph curl:", status)

print("\n=== 18. The Star Malaysia ===")
r = client.get("https://www.thestar.com.my/business/business-news")
print("the star business:", r.status_code)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.select("h2 a, h3 a, .story-title a")[:5]:
    if a.get_text(strip=True):
        print("  The Star:", a.get_text(strip=True), "->", a.get("href"))

print("\n=== 19. Reuters ===")
status, out = test_curl("https://www.reuters.com")
print("reuters curl:", status)
