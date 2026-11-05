import httpx
import json
import re

r = httpx.get('https://www.aiib.org/en/projects/list/.content/all-projects-data.js', verify=False)
txt = r.text.strip()
txt = re.sub(r'^var\s+data\s*=\s*', '', txt).rstrip(';')
txt = re.sub(r',\s*\]', ']', txt)
data = json.loads(txt)
vn = [p for p in data if 'vietnam' in p.get('economy', '').lower() or 'viet nam' in p.get('economy', '').lower() or 'vietnam' in p.get('name', '').lower()]
print('AIIB Total projects:', len(data))
print('AIIB Vietnam projects:', len(vn))
for p in vn[:5]:
    print(f" - {p.get('name')} | {p.get('sector')} | {p.get('approved_funding')} | {p.get('date')} | {p.get('link', '')}")
