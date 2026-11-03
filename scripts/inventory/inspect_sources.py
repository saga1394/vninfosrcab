import sys
import json
import re
import subprocess
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers=headers)

def fetch_url(url):
    try:
        r = client.get(url)
        return r.status_code, r.text, r.headers.get("content-type", "")
    except Exception as e:
        # fallback to curl if Windows SSL issue
        try:
            res = subprocess.run(["curl.exe", "-s", "-k", "-L", "--connect-timeout", "15", url], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.stdout:
                return 200, res.stdout, "text/html"
            return None, str(e), ""
        except Exception as e2:
            return None, f"{e} / curl: {e2}", ""

# Test specific sources that need structural understanding
test_targets = [
    # 2. MOF
    ("mof", "https://www.mof.gov.vn/"),
    # 3. MOIT
    ("moit", "https://moit.gov.vn/tin-tuc"),
    # 4. MOC
    ("moc", "https://moc.gov.vn/vn/Pages/Trangchu.aspx"),
    # 7. InvestVietnam
    ("investvietnam", "https://investvietnam.gov.vn/"),
    # 11. MAE
    ("mae", "https://mae.gov.vn/"),
    # 12. Congbao
    ("congbao", "https://congbao.chinhphu.vn/"),
    # 13. VBPL
    ("vbpl", "https://vbpl.vn/"),
    # 14. MTI
    ("mti_sg", "https://www.meti.gov.sg/"),
    # 15. EnterpriseSG
    ("enterprisesg", "https://www.enterprisesg.gov.sg/media-centre/media-releases"),
    # 16. ACRA
    ("acra_bizfile", "https://www.acra.gov.sg/news-events/news-announcements"),
    # 17. VSIP
    ("vsip", "https://www.vsip.com.vn/"),
    # 18. Amata
    ("amata", "https://amatavn.com/"),
    # 19. Becamex
    ("becamex", "https://becamex.com.vn/"),
    # 20. DEEP C
    ("deepc", "https://deepc.vn/vi/tin-tuc"),
    # 21. Long Hau
    ("longhau", "https://longhau.com.vn/tin-tuc/"),
    # 22. BW Industrial
    ("bwindustrial", "https://bwindustrial.com/news/"),
    # 23. WHA
    ("wha", "https://www.whavietnam.com/en/news-promotions/media-release"),
]

for sid, url in test_targets:
    code, text, ctype = fetch_url(url)
    print(f"\n=== [{sid}] {url} -> {code} ({len(text)} bytes) ===")
    if not code or code != 200:
        print(f"Error / Non-200: {text[:200]}")
        continue
    soup = BeautifulSoup(text, "html.parser")
    title_tag = soup.find("title")
    print(f"Page Title: {title_tag.get_text(strip=True) if title_tag else 'No Title'}")
    
    # Check for rss link
    rss_link = soup.find("link", type=lambda t: t and ("rss" in t or "atom" in t))
    if rss_link:
        print(f"RSS Link found: {rss_link.get('href')}")
    
    # Sample some article links or news items
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(strip=True)
        if len(txt) > 25 and not any(skip in txt.lower() for skip in ["xem thêm", "đọc tiếp", "chi tiết", "xem chi tiết"]):
            links.append((txt[:80], href))
    print(f"Found {len(links)} long-text links. First 3:")
    for t, h in links[:3]:
        print(f"  - {t} -> {h}")
