# -*- coding: utf-8 -*-
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect("data/daily/collector.db")
cur = conn.cursor()

# 1. Backfill empty dates to fetched_at date
cur.execute("UPDATE raw_materials SET pub_date = substr(fetched_at, 1, 10) WHERE pub_date IS NULL OR pub_date = '';")
print(f"[*] Backfilled empty pub_dates to fetched_at: {cur.rowcount} rows")
conn.commit()

# 2. Total state
cur.execute("SELECT count(*), count(DISTINCT source_id), count(DISTINCT province), count(DISTINCT fetch_channel) FROM raw_materials;")
total, sources, provinces, channels = cur.fetchone()
print(f"[*] Total Rows: {total} | Distinct Sources: {sources} | Provinces: {provinces} | Channels: {channels}")

# 3. Check for any remaining empty pub_date
cur.execute("SELECT count(*) FROM raw_materials WHERE pub_date IS NULL OR pub_date = '';")
empty_dates = cur.fetchone()[0]
print(f"[*] Remaining empty pub_dates: {empty_dates}")

# 4. Show high-value samples across all 6 clusters
print("\n=== Verified Clean Samples Across Clusters ===")
targets = [
    ('src-DISC-01', 'CNINFO A股'),
    ('src-DISC-03', '深交所 SZSE'),
    ('src-DISC-05', '港交所 HKEX'),
    ('src-DISC-10', '美国 SEC EDGAR'),
    ('src-A07', '外资局 FIA'),
    ('src-A09', '环评 DSDTM'),
    ('src-A10', '排污许可 DSGiayPhep'),
    ('src-A08', '企业登记 Bố cáo'),
    ('src-B04', 'DEEP C 工业区'),
    ('VN-LOC-03-BN-A', '北宁省政府门户'),
    ('VN-LOC-03-BN-B', '北宁工业区管委会'),
    ('VN-LOC-02-HP-A', '海防市政府门户'),
    ('src-ASSOC-01', '纺织服装协会 VITAS'),
    ('src-ASSOC-03', '物流协会 VLA'),
    ('src-VN-FIN-06', 'The Investor 英文旗舰')
]

for sid, label in targets:
    cur.execute("SELECT source_name, title, pub_date, url FROM raw_materials WHERE source_id = ? ORDER BY pub_date DESC LIMIT 1;", (sid,))
    row = cur.fetchone()
    if row:
        print(f"[{sid}] {label} ({row[0]}) | Date: {row[2]}")
        print(f"    Title: {row[1]}")
        print(f"    URL:   {row[3]}")

conn.close()
