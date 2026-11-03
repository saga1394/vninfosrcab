import sys
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'vi,en;q=0.9',
    },
    timeout=15.0
)

# 1. VOV RSS test with different UA
print("--- 1. VOV ---")
for ua in ["curl/7.88.1", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]:
    for ep in ["https://vov.vn/rss.vov", "https://vov.vn/rss/kinh-te.rss", "https://vov.vn/kinh-te"]:
        try:
            r = client.get(ep, headers={"User-Agent": ua})
            print(f"VOV {ep} with UA {ua[:10]}: HTTP {r.status_code}")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                arts = soup.select("article, .article-item, h3 a, h2 a")
                print(f"  Articles found: {len(arts)}")
                for a in arts[:3]:
                    print("   ", a.get_text(strip=True)[:60])
                break
        except Exception as e:
            print(f"VOV {ep} error:", e)

# 2. Báo Bắc Ninh domain search
print("\n--- 2. Báo Bắc Ninh ---")
# Test various domains for Bac Ninh media
for d in ["https://bacninh.gov.vn", "http://baobacninh.com.vn", "https://bacninhtv.vn", "http://bacninh.tintuc.vn", "https://baobacninh.vn"]:
    try:
        r = client.get(d, timeout=5.0)
        print(f"BBN {d}: HTTP {r.status_code}")
    except Exception as e:
        print(f"BBN {d} failed: {type(e).__name__}")

# 3. DealStreetAsia
print("\n--- 3. DealStreetAsia ---")
try:
    r = client.get("https://www.dealstreetasia.com")
    print(f"DSA home: HTTP {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select("h2.entry-title a, h3.entry-title a, .post-title a, article a")[:5]:
            print("  DSA:", item.get_text(strip=True), "->", item.get("href"))
except Exception as e:
    print("DSA error:", e)

# 4. The Star Malaysia
print("\n--- 4. The Star Malaysia ---")
try:
    r = client.get("https://www.thestar.com.my/business/business-news")
    print(f"The Star: HTTP {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select("h2.f18 a, h2 a, .story-title a")[:5]:
            print("  The Star:", item.get_text(strip=True), "->", item.get("href"))
except Exception as e:
    print("The Star error:", e)

# 5. Diễn đàn Doanh nghiệp
print("\n--- 5. Diễn đàn Doanh nghiệp ---")
try:
    r = client.get("https://diendandoanhnghiep.vn/kinh-te.html")
    print(f"DDDN: HTTP {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select("h3 a, h2 a, .title-news a")[:5]:
            t = item.get_text(strip=True)
            if t and len(t) > 10:
                print("  DDDN:", t[:60], "->", item.get("href"))
except Exception as e:
    print("DDDN error:", e)

# 6. TechNode Global feed with curl
print("\n--- 6. TechNode Global ---")
try:
    res = subprocess.run(
        ["curl.exe", "-s", "-L", "-k",
         "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
         "-H", "Accept: application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
         "https://technode.global/feed/"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    print("TechNode curl len:", len(res.stdout))
    fp = feedparser.parse(res.stdout)
    print("TechNode entries:", len(fp.entries))
    if fp.entries:
        print("  Sample:", fp.entries[0].title, "|", fp.entries[0].published)
except Exception as e:
    print("TechNode error:", e)

# 7. Local newspapers: Thái Nguyên, Đà Nẵng, Tây Ninh, Đồng Nai
print("\n--- 7. Local newspapers DOM ---")
locs = [
    ("Báo Thái Nguyên", "https://baothainguyen.vn/kinh-te/"),
    ("Báo Đà Nẵng", "https://baodanang.vn/channel/5404/"),
    ("Báo Tây Ninh", "https://baotayninh.vn/kinh-te-c10/"),
    ("Báo Đồng Nai", "https://baodongnai.com.vn/kinh-te/"),
]
for name, u in locs:
    try:
        r = client.get(u)
        print(f"{name} ({u}): HTTP {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        found = []
        for item in soup.select("h2 a, h3 a, .title a, article a, .box-category-item a"):
            t = item.get_text(strip=True)
            href = item.get("href", "")
            if t and len(t) > 15 and href not in [x[1] for x in found]:
                found.append((t, href))
        print(f"  Found {len(found)} articles:")
        for t, h in found[:3]:
            print(f"    - {t[:50]} -> {h}")
    except Exception as e:
        print(f"{name} error: {e}")
