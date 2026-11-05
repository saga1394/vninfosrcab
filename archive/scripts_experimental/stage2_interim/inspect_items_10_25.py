import sys
import sqlite3

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
for i in range(9, 25):
    r = rows[i]
    print(f"[{i+1:02d}] [{r[1]}] {r[2]} | {r[4]} | {r[3]}")
    print(f"     FP: {r[0][:12]} | URL: {r[5]}")
    if r[6]:
        snip = r[6].strip().replace('\n', ' ')
        print(f"     Snippet: {snip[:140]}...")
