import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})

# 1. InvestVietnam homepage news items
r_iv = client.get("https://investvietnam.gov.vn/")
soup_iv = BeautifulSoup(r_iv.text, "html.parser")
print("=== InvestVietnam homepage ===")
for a in soup_iv.find_all("a", href=True):
    t = a.get_text(strip=True)
    h = a["href"]
    if len(t) > 20 and not any(k in t.lower() for k in ["trang chủ", "giới thiệu", "liên hệ"]):
        print("  IV link:", t[:70], "->", h)

# 2. MAE homepage items
r_mae = client.get("https://mae.gov.vn/")
soup_mae = BeautifulSoup(r_mae.text, "html.parser")
print("\n=== MAE homepage ===")
for a in soup_mae.find_all("a", href=True):
    t = a.get_text(strip=True)
    h = a["href"]
    if len(t) > 30 and h.endswith(".htm") and not any(k in h for k in ["lien-ket", "van-ban-phap-luat"]):
        print("  MAE link:", t[:70], "->", h)
