import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
for chunk in ['assets/FinanceNewsViewVi-DOkXDNnl.js', 'assets/HomeDefaultViewVi-b_Iu7jgG.js', 'assets/NewsAndBannerBlock-BOyyrtKm.js']:
    r = client.get(f"https://www.mof.gov.vn/{chunk}")
    # find api strings or fetch/get
    apis = re.findall(r'["\'](/[^"\']+)["\']', r.text)
    print(f"=== {chunk} ===")
    for a in set(apis):
        if any(k in a.lower() for k in ["api", "article", "news", "post", "category", "tin-tuc", "data"]):
            print("  endpoint:", a)
