# -*- coding: utf-8 -*-
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('data/daily/collector.db')
cur = conn.cursor()

keywords = ['bán dẫn', 'semiconductor', 'chip', 'data center', 'điện rác', 'pin', 'vinfast', 'xe điện', 'ô tô', 'logistics', 'dppa', 'robot']

matches = []
cur.execute("SELECT source_id, source_name, title, pub_date, url, snippet FROM raw_materials")
for r in cur.fetchall():
    sid, sname, title, pdate, url, snip = r
    text = (title + " " + snip).lower()
    
    # Check if keyword matches
    matched_kws = [kw for kw in keywords if kw in text]
    if not matched_kws:
        continue
        
    # Check if Vietnam local relevance
    vn_markers = [
        'việt nam', 'vietnam', 'hà nội', 'hồ chí minh', 'hcm', 'bắc ninh', 'hải phòng',
        'thái nguyên', 'đồng nai', 'bình dương', 'quảng ninh', 'hải dương', 'nghệ an',
        'thanh hóa', 'đà nẵng', 'khánh hòa', 'ninh thuận', 'cà ná', 'long thành',
        'vinfast', 'transerco', 'evn', 'thaco', 'fpt', 'viettel'
    ]
    if any(vm in text for vm in vn_markers):
        matches.append((r, matched_kws))

print(f"Total Vietnam-relevant sector matches: {len(matches)}")
for (r, kws) in matches:
    print(f"[{','.join(kws)}] [{r[0]}] {r[2]} ({r[3]})")
