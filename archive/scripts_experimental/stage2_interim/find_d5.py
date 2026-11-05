import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('e:/geminiworks/vninfosrcab/data/daily/collector.db')
c = conn.cursor()
c.execute("""
    SELECT fingerprint, source_id, source_name, title, pub_date, url
    FROM raw_materials
    WHERE title LIKE '%Sembcorp%' OR title LIKE '%Xuan Thien%'
""")
for r in c.fetchall():
    print(r)
