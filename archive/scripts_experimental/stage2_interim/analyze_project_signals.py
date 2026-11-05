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
    ORDER BY source_id, pub_date DESC
""")
rows = c.fetchall()

print(f"Total rows: {len(rows)}")

# Project signal keywords in Vietnamese, Chinese, English
project_keywords = [
    r'dự án', r'nhà máy', r'khu công nghiệp', r'kcn', r'kkt', r'công ty', r'đầu tư', r'đtm', r'giấy phép',
    r'xây dựng', r'khánh thành', r'khởi công', r'mở rộng', r'quy hoạch', r'chấp thuận', r'điện mặt trời',
    r'cụm công nghiệp', r'nhà xưởng', r'sản xuất',
    # Chinese
    r'越南', r'子公司', r'增资', r'投资', r'项目', r'工厂', r'产能', r'中标', r'担保', r'设立',
    # English
    r'project', r'plant', r'factory', r'investment', r'investor', r'industrial park', r'facility', r'expand'
]

combined_kw = re.compile('|'.join(project_keywords), re.IGNORECASE)

candidates = []
for r in rows:
    fp, sid, sname, cat, title, snippet, pub_date, prov, url = r
    text = f"{title} {snippet or ''}"
    if combined_kw.search(text):
        candidates.append(r)

print(f"Records matching project signals: {len(candidates)} / {len(rows)}")

print("\n--- Breakdown by Source ID ---")
by_source = {}
for r in candidates:
    sid = r[1]
    by_source[sid] = by_source.get(sid, 0) + 1

for sid, cnt in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
    print(f"  {sid}: {cnt}")

print("\n--- High-Value Project Extraction Preview ---")
for i, r in enumerate(candidates):
    fp, sid, sname, cat, title, snippet, pub_date, prov, url = r
    print(f"[{i+1}] [{sid}] ({prov}) {title}")
    if snippet and len(snippet.strip()) > 0 and snippet.strip() != title.strip():
        print(f"    Snippet: {snippet[:140]}...")
    print(f"    Date: {pub_date} | URL: {url}\n")
