# -*- coding: utf-8 -*-
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('data/daily/collector.db')
cur = conn.cursor()

keywords = [
    'bán dẫn', 'semiconductor', 'chip', 'vi mạch',
    'dữ liệu', 'data center', 'datacenter',
    'rác', 'waste', 'sinh khối', 'biomass',
    'pin', 'battery', 'lưu trữ', 'bess',
    'vinfast', 'vingroup', 'ô tô', 'xe điện', 'ev',
    'kho', 'logistics', 'kho lạnh', 'nhà xưởng',
    'điện mặt trời', 'điện gió', 'lng', 'dppa', 'giá điện',
    'robot', 'tự động hóa', 'cơ khí', 'khuôn mẫu'
]

conditions = " OR ".join(["title LIKE ? OR snippet LIKE ?" for _ in keywords])
params = []
for kw in keywords:
    params.extend([f"%{kw}%", f"%{kw}%"])

sql = f"SELECT source_id, source_name, title, pub_date, url, snippet FROM raw_materials WHERE {conditions}"
cur.execute(sql, params)
rows = cur.fetchall()

print(f"Total keyword matches: {len(rows)}")

# Filter for Vietnam relevance:
# Check if it mentions Vietnam places or Vietnamese entities or Vietnam market
vn_markers = [
    'việt nam', 'vietnam', 'hà nội', 'hồ chí minh', 'hcm', 'bắc ninh', 'hải phòng',
    'thái nguyên', 'đồng nai', 'bình dương', 'quảng ninh', 'hải dương', 'nghệ an',
    'thanh hóa', 'đà nẵng', 'khánh hòa', 'ninh thuận', 'cà ná', 'long thành',
    'khu công nghiệp', 'kcn', 'vinfast', 'vingroup', 'evn', 'thaco', 'fpt', 'viettel',
    'bộ ', 'ubnd', 'ban quản lý', 'chính phủ', 'thủ tướng'
]

vn_local = []
non_vn = []
for r in rows:
    text = (r[2] + " " + r[5]).lower()
    if any(m in text for m in vn_markers):
        vn_local.append(r)
    else:
        non_vn.append(r)

print(f"Vietnam-specific items: {len(vn_local)}")
print(f"Non-Vietnam/Global items: {len(non_vn)}")

print("\n--- SAMPLE VIETNAM-LOCAL MATCHES ---")
for r in vn_local[:25]:
    print(f"[{r[0]}] {r[2]} | {r[3]}")
