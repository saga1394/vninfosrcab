# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

items = json.load(open('data/daily/nov_items_to_judge.json', encoding='utf-8'))
print(f"Total raw Nov items: {len(items)}")

# Let's inspect unique titles and check noise
seen = set()
unique_items = []
for it in items:
    t = it['title'].strip()
    if t not in seen:
        seen.add(t)
        unique_items.append(it)

print(f"Unique Nov items: {len(unique_items)}")
for i, it in enumerate(unique_items):
    print(f"{i+1:03d}. [{it['date']}] [{it['sid']}] {it['title']}")
