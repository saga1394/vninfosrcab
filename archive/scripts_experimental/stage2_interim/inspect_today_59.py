# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/daily/2026-11-04_extracted_59.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for i in range(20, 31):
    r = items[i]
    print(f"[{i+1:02d}] {r['source_id']} | Prov: {r.get('province')} | Date: {r.get('pub_date')} | FP: {r['fingerprint'][:8]}")
    print(f"     Title: {r['title']}")
    print(f"     URL: {r['url']}")
    print(f"     Snippet: {r['snippet'][:220]}")
    print()
