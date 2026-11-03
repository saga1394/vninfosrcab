import sys
import httpx
import re
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

r = client.get("https://vbpl.vn/")
scripts = re.findall(r'<script>(self\.__next_f\.push\(.*?)\)</script>', r.text, re.DOTALL)
print(f"Found {len(scripts)} RSC script pushes in vbpl.vn")

for i, s in enumerate(scripts):
    if "Nghị định" in s or "Thông tư" in s or "Quyết định" in s or "Luật" in s:
        # Extract json strings inside self.__next_f.push([1,"..."])
        m = re.search(r'self\.__next_f\.push\(\[\d+,\s*"(.*)"\]\)', s, re.DOTALL)
        if m:
            raw_str = m.group(1).encode('utf-8').decode('unicode_escape', errors='replace')
            # Look for titles and dates
            items = re.findall(r'(\d+/[0-9A-ZĐ-]+).*?((?:Nghị định|Thông tư|Quyết định|Luật)[^"\\]+)', raw_str)
            print(f"Push {i} items found: {len(items)}")
            for code, title in items[:5]:
                print(f"  Doc: [{code}] {title[:80]}")
