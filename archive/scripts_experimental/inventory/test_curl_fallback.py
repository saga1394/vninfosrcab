import subprocess
import json
from bs4 import BeautifulSoup

def fetch_thamvan(url):
    res = subprocess.run(["curl.exe", "-s", "-k", "--connect-timeout", "10", url], capture_output=True, text=True, encoding="utf-8")
    return res.stdout

html = fetch_thamvan("https://thamvan.mae.gov.vn/Home/DSDTM")
print("HTML length:", len(html))
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table")
if table:
    rows = table.find_all("tr")
    print("Found table with rows:", len(rows))
    for r in rows[1:4]:
        cols = [td.get_text(strip=True) for td in r.find_all("td")]
        print("ROW:", cols[:3])
