import sys
import sqlite3
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('e:/geminiworks/vninfosrcab/data/daily/collector.db')
c = conn.cursor()
c.execute("""
    SELECT fingerprint, source_id, source_name, title, pub_date, url, snippet 
    FROM raw_materials 
    WHERE fetched_at LIKE '2026-11-03%' 
    ORDER BY pub_date DESC
""")
rows = c.fetchall()
print(f"Total records fetched today (2026-11-03): {len(rows)}")
for i, r in enumerate(rows, 1):
    print(f"[{i:02d}] [{r[1]}] {r[2]} | {r[4]} | {r[3]}")
    print(f"     FP: {r[0][:12]} | URL: {r[5]}")
    if r[6]:
        snip = r[6].strip().replace('\n', ' ')
        print(f"     Snippet: {snip[:130]}...")
