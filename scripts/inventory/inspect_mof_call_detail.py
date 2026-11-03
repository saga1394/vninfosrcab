import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/HomeDefaultViewVi-b_Iu7jgG.js")
pos = r.text.find("pinNews")
if pos != -1:
    print(r.text[max(0, pos-150):min(len(r.text), pos+300)])
