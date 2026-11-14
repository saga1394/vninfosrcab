import json
import sqlite3

vault_path = 'V2/data/runs/2026-11-14_candidate_vault.json'
with open(vault_path, 'r', encoding='utf-8') as f:
    vault = json.load(f)

# Also check triage kept
triage_path = 'V2/data/runs/2026-11-14_triage_kept.json'
with open(triage_path, 'r', encoding='utf-8') as f:
    triage = json.load(f)

# Also check projects.db
conn = sqlite3.connect('V2/data/projects.db')
c = conn.cursor()

keywords = {
    '1. 中策橡胶/ZCV/富美II/IDICO': ['zhongce', 'zcv', 'phú mỹ ii', 'phu my ii', 'ch策', 'cao su', 'idico'],
    '2. 南定一号/Taekwang/ACWA': ['nam định', 'nam dinh', 'taekwang', 'acwa', 'bot nam', 'ninh bình', 'ninh binh'],
    '3. VSIP岘港自贸区/Asco': ['asco', 'thương mại tự do', 'thuong mai tu do', 'ftz', 'kita', 'đà nẵng', 'da nang'],
    '4. 名幸电子 Meiko': ['meiko', 'phú thọ', 'phu tho', 'bố trại', 'bo trai', 'hoa binh', 'hòa bình'],
    '5. 新澳股份': ['xinao', 'tân úc', 'thành thành công', 'thanh thanh cong', '603889', 'new australian', 'len'],
    '6. 谅山边境/Fanya': ['lạng sơn', 'lang son', 'fanya', 'hữu lũng', 'huu lung', '1855'],
    '7. 参数补齐/光宝/龙山LNG/SBI': ['lite-on', 'liteon', 'long sơn', 'long son', 'sbi', 'prj117', 'prj131', 'prj473']
}

print(f"Total vault items: {len(vault)}")
print(f"Total triage kept items: {len(triage)}")

for cat, kw_list in keywords.items():
    print(f"\n==================================================")
    print(f"=== Category: {cat} ===")
    
    # 1. Search in vault
    matched_vault = []
    for cid, item in vault.items():
        text = (item.get('title', '') + ' ' + item.get('evidence_snippet', '') + ' ' + item.get('direct_url', '')).lower()
        if any(kw in text for kw in kw_list):
            matched_vault.append(item)
    print(f"  [Vault Matched]: {len(matched_vault)}")
    for m in matched_vault[:5]:
        print(f"    - [{m.get('candidate_id')} / {m.get('source_id')}] {m.get('title')}")
        print(f"      URL: {m.get('direct_url')}")

    # 2. Search in triage kept
    matched_triage = []
    for item in triage:
        text = (item.get('title', '') + ' ' + item.get('evidence_snippet', '') + ' ' + item.get('direct_url', '')).lower()
        if any(kw in text for kw in kw_list):
            matched_triage.append(item)
    print(f"  [Triage Kept Matched]: {len(matched_triage)}")
    for m in matched_triage[:5]:
        print(f"    - [{m.get('candidate_id')} / {m.get('source_id')}] {m.get('title')}")

    # 3. Search in projects.db
    # Check tables in projects.db
    query = "SELECT project_id, name_zh, name_vn, status, total_investment_usd FROM projects WHERE " + " OR ".join(["LOWER(name_zh) LIKE ? OR LOWER(name_vn) LIKE ? OR LOWER(investor_name) LIKE ?"] * len(kw_list))
    params = []
    for kw in kw_list:
        params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
    try:
        c.execute(query, params)
        rows = c.fetchall()
        print(f"  [projects.db Matched]: {len(rows)}")
        for r in rows[:5]:
            print(f"    - DB Project: {r}")
    except Exception as e:
        print(f"    - DB Query Error: {e}")
