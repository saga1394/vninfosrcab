import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=10.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

def find_links(portal_url, province_name):
    print(f"\n================ Finding links on {province_name} ({portal_url}) ================")
    try:
        r = client.get(portal_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a', href=True)
        keywords = ['tai nguyen', 'moi truong', 'tnmt', 'tai chinh', 'xay dung', 'khu kinh te', 'kkt', 'kcn', 'khu cong nghiep', 'nghi son', 'vung ang', 'van phong']
        found = []
        for a in links:
            href = a['href'].strip()
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords) or any(kw in href.lower() for kw in ['tnmt', 'stc', 'sxd', 'kcn', 'kkt', 'so-tai', 'so-xay']):
                found.append((a.get_text(strip=True), href))
        # Deduplicate
        seen = set()
        for text, href in found:
            key = (text, href)
            if key not in seen and text:
                seen.add(key)
                print(f"  * {text} -> {href}")
    except Exception as e:
        print(f"Error fetching {portal_url}: {e}")

portals = [
    ("https://bacninh.gov.vn", "Bắc Ninh"),
    ("https://quangninh.gov.vn", "Quảng Ninh"),
    ("https://tayninh.gov.vn", "Tây Ninh"),
    ("https://thanhhoa.gov.vn", "Thanh Hóa"),
    ("https://danang.gov.vn", "Đà Nẵng"),
    ("https://khanhhoa.gov.vn", "Khánh Hòa"),
    ("https://hatinh.gov.vn", "Hà Tĩnh")
]

for url, name in portals:
    find_links(url, name)
