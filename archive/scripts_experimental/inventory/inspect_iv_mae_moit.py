import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# 1. MOIT specific category
r = client.get("https://moit.gov.vn/tin-tuc/phat-trien-cong-nghiep")
print("MOIT phat-trien-cong-nghiep status:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        t = a.get_text(strip=True)
        if len(t) > 30:
            print("  MOIT industry item:", t[:80], "->", a["href"])

# 2. InvestVietnam news
r_iv = client.get("https://investvietnam.gov.vn/vi/tin-tuc-su-kien.html")
print("InvestVietnam tin-tuc-su-kien status:", r_iv.status_code)
if r_iv.status_code == 200:
    soup = BeautifulSoup(r_iv.text, "html.parser")
    for a in soup.find_all("a", href=True):
        t = a.get_text(strip=True)
        if len(t) > 25:
            print("  InvestVietnam item:", t[:80], "->", a["href"])

# 3. MAE news page
r_mae = client.get("https://mae.gov.vn/tin-tuc-su-kien.htm")
print("MAE tin-tuc-su-kien status:", r_mae.status_code)
if r_mae.status_code == 200:
    soup = BeautifulSoup(r_mae.text, "html.parser")
    for a in soup.find_all("a", href=True):
        t = a.get_text(strip=True)
        if len(t) > 30:
            print("  MAE item:", t[:80], "->", a["href"])
