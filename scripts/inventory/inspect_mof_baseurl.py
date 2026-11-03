import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
# find where baseURL or api is defined
matches = re.findall(r'(?:baseURL|baseUrl|api)[^,;]{1,60}', r.text)
print("BaseURL / API matches:")
for m in matches[:15]:
    print(" ", m)
