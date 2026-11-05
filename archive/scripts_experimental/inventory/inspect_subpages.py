import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers=headers)

# 1. MOF content analysis
r_mof = client.get("https://www.mof.gov.vn/")
print("=== MOF HTML ===")
print(r_mof.text[:1000])

# 2. Deep C news links from homepage
r_deepc = client.get("https://deepc.vn/vi/")
soup_deepc = BeautifulSoup(r_deepc.text, "html.parser")
print("\n=== DEEP C Links ===")
for a in soup_deepc.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["tin", "news", "su-kien", "media", "bai-viet"]):
        print("DeepC link:", a.get_text(strip=True), "->", href)

# 3. Long Hau links from homepage
r_longhau = client.get("https://longhau.com.vn/")
soup_longhau = BeautifulSoup(r_longhau.text, "html.parser")
print("\n=== LONG HAU Links ===")
for a in soup_longhau.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["tin", "news", "su-kien", "media", "khuyen-mai"]):
        print("LongHau link:", a.get_text(strip=True), "->", href)

# 4. WHA links from homepage
r_wha = client.get("https://www.whavietnam.com/en/home")
soup_wha = BeautifulSoup(r_wha.text, "html.parser")
print("\n=== WHA Links ===")
for a in soup_wha.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["news", "media", "press", "investor", "event"]):
        print("WHA link:", a.get_text(strip=True), "->", href)

# 5. EnterpriseSG links from homepage
r_esg = client.get("https://www.enterprisesg.gov.sg/")
soup_esg = BeautifulSoup(r_esg.text, "html.parser")
print("\n=== EnterpriseSG Links ===")
for a in soup_esg.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["media", "news", "release", "press"]):
        print("ESG link:", a.get_text(strip=True), "->", href)

# 6. VBPL links
r_vbpl = client.get("https://vbpl.vn/")
soup_vbpl = BeautifulSoup(r_vbpl.text, "html.parser")
print("\n=== VBPL Links ===")
for a in soup_vbpl.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["vanban", "van-ban", "moi-ban-hanh", "tim-kiem", "Pages"]):
        print("VBPL link:", a.get_text(strip=True)[:60], "->", href)
