import sys
import json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
data = json.load(open('data/inventory/batch_1_raw_results.json', encoding='utf-8'))
for s in data['sources']:
    print(f"{s['id']:<8} | {s['name'][:30]:<30} | {s['method_verified']:<35} | samples: {s['sample_count']} | HTTP: {s['status_code']}")
