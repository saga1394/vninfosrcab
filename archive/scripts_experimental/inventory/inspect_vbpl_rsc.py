import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

r = client.get("https://vbpl.vn/")
scripts = re.findall(r'<script>(self\.__next_f\.push\(.*?<\/script>)', r.text, re.DOTALL)
print(f"Found {len(scripts)} RSC script pushes in vbpl.vn")
for s in scripts:
    # search for document titles or law numbers
    matches = re.findall(r'(Nghị định|Thông tư|Quyết định|Luật)[^"]+', s)
    if matches:
        print("  Found legal docs:", matches[:5])
