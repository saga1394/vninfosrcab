import sqlite3
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = sqlite3.connect('data/daily/collector.db')
c = conn.cursor()

c.execute("""
    SELECT fingerprint, source_id, source_name, category, title, snippet, pub_date, province, url
    FROM raw_materials
""")
rows = c.fetchall()

# Let's inspect all items from:
# 1. src-A09 (EIA)
# 2. src-A10 (Discharge permits)
# 3. src-DISC-* (Disclosures: SSE, SZSE, HKEX, TWSE)
# 4. src-B04 (DEEP C), src-B01 (VSIP), src-B02 (Viglacera), src-B06 (KBC)
# 5. src-VN-FIN-06 (The Investor / FDI)
# 6. src-VN-FIN-04 (Vietstock / VIR)
# 7. VN-LOC-* (Provincial Portals & IZAs)
# 8. src-TW-MED-01, src-JP-MED-01

focus_sources = [
    'src-A09', 'src-A10', 'src-DISC-01', 'src-DISC-03', 'src-DISC-05', 'src-DISC-10',
    'src-B04', 'src-B01', 'src-B02', 'src-B06', 'src-VN-FIN-06', 'src-VN-FIN-04',
    'src-TW-MED-01', 'src-JP-MED-01', 'src-IND-PROP-01', 'src-A07'
]

print("=== DEEP INSPECTION OF PRIMARY INDUSTRIAL & DISCLOSURE SOURCES ===")
for r in rows:
    fp, sid, sname, cat, title, snippet, pub_date, prov, url = r
    if sid in focus_sources or sid.startswith('VN-LOC-'):
        print(f"[{sid}] | Prov: {prov} | Date: {pub_date}")
        print(f"  Title: {title}")
        if snippet:
            print(f"  Snippet: {snippet.strip()[:180]}")
        print(f"  URL: {url}\n")
