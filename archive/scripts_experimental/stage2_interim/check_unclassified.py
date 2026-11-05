import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('e:/geminiworks/vninfosrcab/data/stage2/projects.db')
c = conn.cursor()
c.execute("SELECT raw_fingerprint FROM dimensional_signals")
existing_fps = set(r[0] for r in c.fetchall())
conn.close()

conn_raw = sqlite3.connect('e:/geminiworks/vninfosrcab/data/daily/collector.db')
c_raw = conn_raw.cursor()
c_raw.execute("""
    SELECT fingerprint, source_id, source_name, title, pub_date, url, snippet 
    FROM raw_materials 
    ORDER BY pub_date DESC, fetched_at DESC
""")
rows = c_raw.fetchall()

print(f"Total in collector.db: {len(rows)}")
unclassified = [r for r in rows if r[0] not in existing_fps]
print(f"Unclassified count: {len(unclassified)}")

# Group unclassified by source_id
by_source = {}
for r in unclassified:
    by_source.setdefault(r[1], []).append(r)

print("\nUnclassified by source:")
for sid, rlist in sorted(by_source.items()):
    print(f"  {sid:18s} ({rlist[0][2][:25]}): {len(rlist)} records")
