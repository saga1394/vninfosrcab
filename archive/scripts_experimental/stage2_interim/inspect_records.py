import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('data/daily/collector.db')
c = conn.cursor()

c.execute("SELECT count(*) FROM raw_materials")
print(f"Total raw materials: {c.fetchone()[0]}")

c.execute("""
    SELECT source_id, source_name, category, title, snippet, pub_date, province, dimension_hints, url, fingerprint
    FROM raw_materials 
    ORDER BY fetched_at ASC
""")
records = c.fetchall()

source_counts = {}
for r in records:
    sid = r[0]
    source_counts[sid] = source_counts.get(sid, 0) + 1

print(f"\nSources distribution ({len(source_counts)} sources):")
for sid, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {sid}: {count}")

print("\n=== Project-Relevant Candidates Sample (First 25) ===")
count = 0
for i, r in enumerate(records):
    title = r[3]
    snippet = r[4] or ""
    # Filter or look at potential project-related mentions
    print(f"[{i+1}] [{r[0]}] {r[1]} | Date: {r[5]} | Prov: {r[6]}")
    print(f"    Title: {title}")
    if snippet:
        print(f"    Snippet: {snippet[:120]}...")
    print(f"    URL: {r[8]}\n")
