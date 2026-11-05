import sys
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

sys.stdout.reconfigure(encoding='utf-8')
client = httpx.Client(verify=False, follow_redirects=True, timeout=8.0)

for label, u in [('DSEZA', 'https://dseza.danang.gov.vn'), ('NghiSon', 'https://nghison.thanhhoa.gov.vn/vi/portal/pages/default.aspx')]:
    r = client.get(u)
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
    print(f"=== {label} scripts ===")
    for s in scripts:
        full_s = urljoin(u, s)
        print(" ", full_s)
        # Fetch script to look for api endpoints
        try:
            js = client.get(full_s).text
            apis = re.findall(r'(/api/[a-zA-Z0-9_\-/]+)', js)
            if apis:
                print(f"    APIs found: {set(apis[:8])}")
        except:
            pass
