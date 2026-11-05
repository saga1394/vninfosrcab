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

unclassified = [r for r in rows if r[0] not in existing_fps]

print(f"--- Top Unclassified Provincial & Key Regulatory Records ---")
for r in unclassified:
    sid = r[1]
    title = r[3]
    if any(k in sid for k in ["LOC", "src-A", "src-B", "DISC", "ASSOC", "src-IND"]) or "The Investor" in r[2]:
        print(f"[{sid:16s}] {r[4]} | {title}")
        print(f"    FP: {r[0][:12]} | URL: {r[5]}")
