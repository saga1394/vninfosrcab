import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r = client.get("https://www.mof.gov.vn/assets/index-DnZFZR59.js")
# find all occurrences of .get( or .post(
matches = re.findall(r'\.(?:get|post)\([`"\']([^`"\']+)[`"\']', r.text)
print("All .get/.post calls in index:", set(matches))
