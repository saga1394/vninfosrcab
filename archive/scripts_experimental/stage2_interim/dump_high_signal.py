import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('data/daily/collector.db')
c = conn.cursor()

c.execute("""
    SELECT fingerprint, source_id, source_name, title, snippet, pub_date, province, url
    FROM raw_materials
    WHERE source_id IN (
        'src-A09', 'src-A10', 'src-DISC-01', 'src-DISC-03', 'src-DISC-05',
        'src-B04', 'src-B01', 'src-B02', 'src-B06', 'src-VN-FIN-06',
        'VN-LOC-04-TN-B', 'VN-LOC-12-NA-B', 'VN-LOC-05-HY-A'
    )
    ORDER BY source_id, pub_date DESC
""")
rows = c.fetchall()

print(f"Total high-signal rows: {len(rows)}\n")
for i, r in enumerate(rows):
    fp, sid, sname, title, snippet, pub_date, prov, url = r
    print(f"[{i+1}] [{sid}] ({sname})")
    print(f"    Title: {title}")
    if snippet:
        print(f"    Snippet: {snippet.strip()}")
    print(f"    Date: {pub_date} | Prov: {prov}")
    print(f"    URL: {url}")
    print(f"    Fingerprint: {fp}\n")
