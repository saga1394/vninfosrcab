import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
with open('data/inventory/batch_3_raw_results.json', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total Sources: {len(d['sources'])}")
print("\n=== Sources with Status != 200 or Samples < 3 ===")
for s in d['sources']:
    if s['status_code'] != 200 or s['sample_count'] < 3:
        print(f"[{s['id']}] {s['province_cn']} ({s['category']}): {s['name']}")
        print(f"  URL: {s['target_url']}")
        print(f"  Status: {s['status_code']} | Method: {s['method_verified']} | Samples: {s['sample_count']}")
        print(f"  Notes: {s['technical_notes']}")
        print()

print("\n=== Sample of 5 Valid Sources and Their First 2 Records ===")
count = 0
for s in d['sources']:
    if s['sample_count'] >= 3:
        count += 1
        print(f"[{s['id']}] {s['province_cn']} ({s['category']}) - {s['name']}:")
        for idx, entry in enumerate(s['sample_entries'][:2], 1):
            print(f"   ({idx}) Title: {entry['title']}")
            print(f"       Date: {entry['pub_date']} | URL: {entry['url']}")
        if count >= 5:
            break
