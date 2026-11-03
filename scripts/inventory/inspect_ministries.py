import sys
import httpx
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# 1. MOIT (Industry and Trade)
print("=== MOIT News ===")
r_moit = client.get("https://moit.gov.vn/tin-tuc")
soup_moit = BeautifulSoup(r_moit.text, "html.parser")
articles = soup_moit.find_all("div", class_=lambda c: c and any(k in str(c) for k in ["item", "news", "article"]))
print(f"MOIT articles count: {len(articles)}")
found = 0
for a in soup_moit.find_all("a", href=True):
    href = a["href"]
    t = a.get_text(strip=True)
    if "/tin-tuc/" in href and len(t) > 25 and href.count("/") >= 3:
        print(f"  MOIT: {t[:80]} -> {href}")
        found += 1
        if found >= 5:
            break

# 2. MOC (Construction)
print("\n=== MOC News ===")
r_moc = client.get("https://moc.gov.vn/vn/Pages/Trangchu.aspx")
soup_moc = BeautifulSoup(r_moc.text, "html.parser")
found = 0
for a in soup_moc.find_all("a", href=True):
    href = a["href"]
    t = a.get_text(strip=True)
    if ("/tin-tuc/" in href or "Pages/ChiTiet" in href or "/chuyen-muc/" in href) and len(t) > 25:
        print(f"  MOC: {t[:80]} -> {href}")
        found += 1
        if found >= 5:
            break

# 3. MAE (Agriculture & Environment)
print("\n=== MAE News ===")
r_mae = client.get("https://mae.gov.vn/")
soup_mae = BeautifulSoup(r_mae.text, "html.parser")
found = 0
for a in soup_mae.find_all("a", href=True):
    href = a["href"]
    t = a.get_text(strip=True)
    if (".htm" in href or "tin-tuc" in href) and len(t) > 30 and not "van-ban" in href:
        print(f"  MAE: {t[:80]} -> {href}")
        found += 1
        if found >= 5:
            break
