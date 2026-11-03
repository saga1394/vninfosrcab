import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
# Find context around VITE_SERVER_URL
pos = r.text.find("VITE_SERVER_URL")
if pos != -1:
    print(r.text[max(0, pos-150):min(len(r.text), pos+250)])
