"""
Historical Intelligence Repository Ingestion Engine.
Adheres to 6152 Plan and AGENTS.md rules:
- Ingests 128 historical intelligence reports (2026-07-12 to 2026-11-03)
- Extracts 380+ projects (PRJ001~PRJ423), 600+ timeline events (EVTxxx), companies, and macro stats
- Populates SQLite database (data/stage2/projects.db)
- Exports structured archive to data/stage2/historical_repository.json
"""

import os
import re
import sys
import json
import glob
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECTS_DB_PATH = "data/stage2/projects.db"
HISTORICAL_DIR = "data/historical_reports/reports"
OUTPUT_JSON_PATH = "data/stage2/historical_repository.json"

PROVINCE_MAP = {
    # Vietnamese & Accents
    "hồ chí minh": "Hồ Chí Minh", "tp.hcm": "Hồ Chí Minh", "tphcm": "Hồ Chí Minh", "saigon": "Hồ Chí Minh", "胡志明": "Hồ Chí Minh",
    "bắc ninh": "Bắc Ninh", "bac ninh": "Bắc Ninh", "北宁": "Bắc Ninh",
    "hải phòng": "Hải Phòng", "hai phong": "Hải Phòng", "海防": "Hải Phòng",
    "quảng ninh": "Quảng Ninh", "quang ninh": "Quảng Ninh", "广宁": "Quảng Ninh",
    "thái nguyên": "Thái Nguyên", "thai nguyen": "Thái Nguyên", "太原": "Thái Nguyên",
    "tây ninh": "Tây Ninh", "tay ninh": "Tây Ninh", "西宁": "Tây Ninh",
    "hà nội": "Hà Nội", "ha noi": "Hà Nội", "河内": "Hà Nội",
    "đà nẵng": "Đà Nẵng", "da nang": "Đà Nẵng", "岘港": "Đà Nẵng",
    "nghệ an": "Nghệ An", "nghe an": "Nghệ An", "义安": "Nghệ An", "乂安": "Nghệ An",
    "đồng nai": "Đồng Nai", "dong nai": "Đồng Nai", "同奈": "Đồng Nai",
    "phú thọ": "Phú Thọ", "phu tho": "Phú Thọ", "富寿": "Phú Thọ",
    "ninh bình": "Ninh Bình", "ninh binh": "Ninh Bình", "宁平": "Ninh Bình",
    "hưng yên": "Hưng Yên", "hung yen": "Hưng Yên", "兴安": "Hưng Yên",
    "quảng nam": "Quảng Nam", "quang nam": "Quảng Nam", "广南": "Quảng Nam",
    "bình dương": "Bình Dương", "binh duong": "Bình Dương", "平阳": "Bình Dương",
    "bà rịa": "Bà Rịa - Vũng Tàu", "vũng tàu": "Bà Rịa - Vũng Tàu", "ba ria": "Bà Rịa - Vũng Tàu", "巴地头顿": "Bà Rịa - Vũng Tàu", "头顿": "Bà Rịa - Vũng Tàu",
    "bình phước": "Bình Phước", "binh phuoc": "Bình Phước", "平福": "Bình Phước",
    "long an": "Long An", "隆安": "Long An",
    "tiền giang": "Tiền Giang", "tien giang": "Tiền Giang", "前江": "Tiền Giang",
    "lâm đồng": "Lâm Đồng", "lam dong": "Lâm Đồng", "林同": "Lâm Đồng",
    "khánh hòa": "Khánh Hòa", "khanh hoa": "Khánh Hòa", "庆和": "Khánh Hòa",
    "quảng ngãi": "Quảng Ngãi", "quang ngai": "Quảng Ngãi", "广义": "Quảng Ngãi",
    "bình định": "Bình Định", "binh dinh": "Bình Định", "平定": "Bình Định",
    "gia lai": "Gia Lai", "嘉莱": "Gia Lai",
    "đắk lắk": "Đắk Lắk", "đắc lắc": "Đắk Lắk", "dak lak": "Đắk Lắk", "得乐": "Đắk Lắk", "多乐": "Đắk Lắk",
    "thừa thiên huế": "Thừa Thiên Huế", "huế": "Thừa Thiên Huế", "顺化": "Thừa Thiên Huế",
    "hà nam": "Hà Nam", "ha nam": "Hà Nam", "河南": "Hà Nam",
    "hải dương": "Hải Dương", "hai duong": "Hải Dương", "海阳": "Hải Dương",
    "vĩnh phúc": "Vĩnh Phúc", "vinh phuc": "Vĩnh Phúc", "永福": "Vĩnh Phúc",
    "thanh hóa": "Thanh Hóa", "thanh hoa": "Thanh Hóa", "清化": "Thanh Hóa",
    "hà tĩnh": "Hà Tĩnh", "ha tinh": "Hà Tĩnh", "河静": "Hà Tĩnh",
    "quảng trị": "Quảng Trị", "quang tri": "Quảng Trị", "广治": "Quảng Trị",
    "cần thơ": "Cần Thơ", "can tho": "Cần Thơ", "芹苴": "Cần Thơ",
    "kiên giang": "Kiên Giang", "kien giang": "Kiên Giang", "坚江": "Kiên Giang",
    "sóc trăng": "Sóc Trăng", "soc trang": "Sóc Trăng", "朔庄": "Sóc Trăng",
    "hòa bình": "Hòa Bình", "hoa binh": "Hòa Bình", "和平": "Hòa Bình",
    "sơn la": "Sơn La", "son la": "Sơn La", "山罗": "Sơn La",
    "lào cai": "Lào Cai", "lao cai": "Lào Cai", "老街": "Lào Cai",
    "yên bái": "Yên Bái", "yen bai": "Yên Bái", "安沛": "Yên Bái"
}

COUNTRY_MAP = {
    "中国": "中国大陆", "中资": "中国大陆", "china": "中国大陆",
    "中国台湾": "中国台湾", "台资": "中国台湾", "taiwan": "中国台湾",
    "中国香港": "中国香港", "港资": "中国香港", "hong kong": "中国香港",
    "日本": "日本", "日资": "日本", "japan": "日本",
    "韩国": "韩国", "韩资": "韩国", "korea": "韩国",
    "美国": "美国", "美资": "美国", "usa": "美国",
    "德国": "德国", "德资": "德国", "germany": "德国",
    "新加坡": "新加坡", "新资": "新加坡", "singapore": "新加坡",
    "泰国": "泰国", "泰资": "泰国", "thailand": "泰国",
    "马来西亚": "马来西亚", "malaysia": "马来西亚",
    "越南": "越南本土", "越资": "越南本土", "vietnam": "越南本土",
    "比利时": "比利时", "belgium": "比利时",
    "卢森堡": "卢森堡", "luxembourg": "卢森堡",
    "丹麦": "丹麦", "denmark": "丹麦",
    "澳大利亚": "澳大利亚", "australia": "澳大利亚"
}

def clean_province(text: str) -> Optional[str]:
    if not text:
        return None
    lower = text.lower()
    for k, v in PROVINCE_MAP.items():
        if k in lower:
            return v
    return None

def clean_country(text: str) -> str:
    if not text:
        return "未知/跨国"
    for k, v in COUNTRY_MAP.items():
        if k in text or k.lower() in text.lower():
            return v
    return text[:20]

def infer_stage(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["商运", "投产", "运营", "启用", "投用", "满产"]):
        return "OPERATING"
    if any(x in t for x in ["开工", "动工", "在建", "施工", "封顶", "奠基"]):
        return "CONSTRUCTING"
    if any(x in t for x in ["获批", "授证", "核准", "irc", "执照", "立项"]):
        return "IRC_APPROVED"
    if any(x in t for x in ["征地", "拆迁", "清表", "地块"]):
        return "SITE_CLEARANCE"
    if any(x in t for x in ["环评", "环境影响", "consult"]):
        return "EIA_CONSULTED"
    if any(x in t for x in ["排污", "许可证"]):
        return "PERMIT_APPLIED"
    if any(x in t for x in ["增资", "扩产", "加码", "并购", "收购", "注资", "注销", "退出", "分立"]):
        return "EXPANDING_EXIT"
    return "IRC_APPROVED"

def clean_title_str(t: str) -> str:
    t = re.sub(r'#{1,4}\s*', '', t)
    t = re.sub(r'^[🚩🔴🟡🟢💡\d\.\s\|]+', '', t)
    t = re.sub(r'[（\[\(].*?PRJ\d+.*?[）\]\)]', '', t)
    t = re.sub(r'[*_~`]', '', t)
    return t.strip()

def parse_all_reports() -> Dict[str, Any]:
    files = sorted(glob.glob(os.path.join(HISTORICAL_DIR, '*.*')))
    print(f"[PARSER] Scanning {len(files)} historical files in {HISTORICAL_DIR}...")
    
    projects: Dict[str, Dict[str, Any]] = {}
    events: List[Dict[str, Any]] = []
    macro_records: List[Dict[str, Any]] = []
    thematic_records: List[Dict[str, Any]] = []

    def get_or_create_project(pid: str) -> Dict[str, Any]:
        if pid not in projects:
            projects[pid] = {
                "project_id": pid,
                "project_name_cn": "",
                "project_name_vn": "",
                "investor_name": "",
                "parent_company": "",
                "origin_country": "",
                "province": "",
                "district_commune": "",
                "industrial_park": "",
                "sector": "",
                "scale_capacity": "",
                "current_stage": "IRC_APPROVED",
                "first_seen_date": "9999-99-99",
                "last_seen_date": "0000-00-00",
                "raw_titles": [],
                "raw_investors": [],
                "raw_provinces": [],
                "raw_amounts": [],
                "raw_sectors": [],
                "raw_stages": [],
                "event_ids": set(),
                "history_timeline": []
            }
        return projects[pid]

    for fpath in files:
        fname = os.path.basename(fpath)
        date_m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
        fdate = date_m.group(1) if date_m else "2026-10-01"
        
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()

        # Check for deep thematic packs
        if "datacenter" in fname:
            thematic_records.append({
                "theme_id": "THEME-DATACENTER",
                "theme_name": "越南数据中心外资准入与基础设施布局",
                "file_name": fname,
                "date": fdate,
                "summary": content[:500]
            })
        elif "VinFast" in fname or "半导体" in fname:
            thematic_records.append({
                "theme_id": "THEME-SEMICON-AUTO",
                "theme_name": "越南半导体与VinFast汽车供应链协同专题",
                "file_name": fname,
                "date": fdate,
                "summary": content[:500]
            })
        elif "JLL" in fname:
            thematic_records.append({
                "theme_id": "THEME-JLL-FDI",
                "theme_name": "JLL越南制造业FDI份额核实",
                "file_name": fname,
                "date": fdate,
                "summary": content[:500]
            })

        # Check for macro stats in file
        # Pattern A: Section 〇
        m_macro = re.search(r'##\s+〇[、\.\s\(].*?官方宏观数据(.*?)(?=\n\s*---\s*\n|\n##\s+[^〇]|\Z)', content, re.DOTALL)
        if m_macro:
            macro_block = m_macro.group(1)
            # Find totals in table: | **年内新增注册** | **548.5** |
            m_reg = re.search(r'年内新增注册.*?\|\s*\*?\*?([0-9\.]+)\*?\*?', macro_block)
            if not m_reg:
                m_reg = re.search(r'年内新增注册.*?([0-9\.]+)\s*(?:亿美元|亿)', macro_block)
            m_dis = re.search(r'实际到位.*?\|\s*\*?\*?([0-9\.]+)\*?\*?', macro_block)
            if not m_dis:
                m_dis = re.search(r'实际到位.*?([0-9\.]+)\s*(?:亿美元|亿)', macro_block)

            reg_val = float(m_reg.group(1)) if m_reg else None
            dis_val = float(m_dis.group(1)) if m_dis else None
            if reg_val or dis_val:
                macro_records.append({
                    "period_date": fdate,
                    "source_file": fname,
                    "registered_usd_bn": reg_val,
                    "disbursed_usd_bn": dis_val,
                    "summary": macro_block[:400].strip()
                })
        else:
            # Pattern B: July / early briefs with H1 or 前X个月
            m_h1 = re.search(r'H1\s+FDI.*?\$([0-9\.]+)亿.*?到位\$([0-9\.]+)亿', content)
            if m_h1:
                macro_records.append({
                    "period_date": fdate,
                    "source_file": fname,
                    "registered_usd_bn": float(m_h1.group(1)),
                    "disbursed_usd_bn": float(m_h1.group(2)),
                    "summary": m_h1.group(0)
                })

        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 1. Header with PRJ: e.g. ### 1. 台资电子｜光宝科技再注资 3.20 亿美元（PRJ117）
            if line.startswith('#') and 'PRJ' in line:
                pids = re.findall(r'PRJ\d+', line)
                if pids:
                    pid = pids[0]
                    p = get_or_create_project(pid)
                    if fdate < p["first_seen_date"]: p["first_seen_date"] = fdate
                    if fdate > p["last_seen_date"]: p["last_seen_date"] = fdate
                    
                    clean_t = clean_title_str(line)
                    if clean_t:
                        p["raw_titles"].append(clean_t)

                    # Gather block
                    sub_lines = []
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('#'):
                        sub_lines.append(lines[j])
                        j += 1
                    block_txt = '\n'.join(sub_lines)
                    
                    # Look for EVT in header or block
                    evts = re.findall(r'EVT\d+', line + ' ' + block_txt)
                    evt_id = evts[0] if evts else f"EVT-AUTO-{pid}-{fdate.replace('-', '')}"
                    p["event_ids"].add(evt_id)

                    # Extract details from bullet items
                    m_inv = re.search(r'\*?\*?(?:投资方|投资主体|投资者|业主|实体|公司)\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_inv: p["raw_investors"].append(m_inv.group(1).replace('*', '').strip())
                    
                    m_tgt = re.search(r'\*?\*?(?:标的|项目名称|标的资产|标的/项目)\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_tgt: p["raw_titles"].append(clean_title_str(m_tgt.group(1)))

                    m_amt = re.search(r'\*?\*?(?:金额[/\w]*|总投资|投资额|规模)[/\w]*\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_amt: p["raw_amounts"].append(m_amt.group(1).replace('*', '').strip())

                    m_loc = re.search(r'\*?\*?(?:选址|地点|厂址|位置|注册地|省份|落地)[/\w]*\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_loc: p["raw_provinces"].append(m_loc.group(1).replace('*', '').strip())

                    m_sec = re.search(r'\*?\*?(?:业务|行业|产能|方向|性质|产线)[/\w]*\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_sec: p["raw_sectors"].append(m_sec.group(1).replace('*', '').strip())

                    m_stg = re.search(r'\*?\*?(?:动作|状态|时点|进度|状态变更)[/\w]*\*?\*?[：:]\*?\*?\s*([^\n]+)', block_txt)
                    if m_stg: p["raw_stages"].append(m_stg.group(1).replace('*', '').strip())

                    # Add event
                    stg_val = infer_stage(clean_t + " " + block_txt)
                    p["current_stage"] = stg_val
                    evt_entry = {
                        "event_id": evt_id,
                        "project_id": pid,
                        "event_date": fdate,
                        "stage": stg_val,
                        "title": clean_t or "项目动态更新",
                        "snippet": block_txt[:600].strip(),
                        "source_file": fname
                    }
                    p["history_timeline"].append(evt_entry)
                    events.append(evt_entry)

                    i = j
                    continue

            # 2. Table row with PRJ: | PRJ018 | Fumakila同奈工厂(扩建) | 0.138 | 已开工 | ...
            if '|' in line and 'PRJ' in line:
                pids = re.findall(r'PRJ\d+', line)
                for pid in pids:
                    p = get_or_create_project(pid)
                    if fdate < p["first_seen_date"]: p["first_seen_date"] = fdate
                    if fdate > p["last_seen_date"]: p["last_seen_date"] = fdate

                    cells = [c.strip() for c in line.split('|') if c.strip()]
                    clean_cells = [c for c in cells if not re.search(r'PRJ\d+', c)]
                    
                    # Parse table cells
                    row_name = ""
                    for c in clean_cells:
                        if any(cur in c for cur in ['$', '亿', '万', 'USD', '越盾', 'tỷ']):
                            p["raw_amounts"].append(c)
                        elif any(st in c for st in ['获批', '开工', '投产', '签约', '扩建', '商运', '推进', '增资', '动工', '规划']):
                            p["raw_stages"].append(c)
                        elif any(p_kw in c.lower() for p_kw in PROVINCE_MAP.keys()):
                            p["raw_provinces"].append(c)
                        elif any(c_kw in c for c_kw in COUNTRY_MAP.keys()):
                            p["raw_investors"].append(c)
                        elif len(c) > 3 and not row_name and not any(x in c for x in ['新建', '更新', '历史', '条目', '编号', '代码']):
                            row_name = clean_title_str(c)
                    
                    if row_name:
                        p["raw_titles"].append(row_name)

                    evts = re.findall(r'EVT\d+', line)
                    evt_id = evts[0] if evts else f"EVT-TBL-{pid}-{fdate.replace('-', '')}"
                    p["event_ids"].add(evt_id)
                    stg_val = infer_stage(line)
                    evt_entry = {
                        "event_id": evt_id,
                        "project_id": pid,
                        "event_date": fdate,
                        "stage": stg_val,
                        "title": row_name or f"{pid} 进度更新",
                        "snippet": line[:300].strip(),
                        "source_file": fname
                    }
                    p["history_timeline"].append(evt_entry)
                    events.append(evt_entry)

            # 3. Bullet points: - **PRJ048（LSP龙山石化）**：追加5亿美元...
            if (line.startswith('-') or line.startswith('*') or line.startswith('>')) and 'PRJ' in line:
                pids = re.findall(r'PRJ\d+', line)
                for pid in pids:
                    p = get_or_create_project(pid)
                    if fdate < p["first_seen_date"]: p["first_seen_date"] = fdate
                    if fdate > p["last_seen_date"]: p["last_seen_date"] = fdate
                    
                    m_bname = re.search(r'PRJ\d+[（\(]?([^）\)\:：\*\n]+)', line)
                    if m_bname:
                        b_name = clean_title_str(m_bname.group(1))
                        if len(b_name) > 2:
                            p["raw_titles"].append(b_name)
                    
                    clean_l = clean_title_str(line)
                    evts = re.findall(r'EVT\d+', line)
                    evt_id = evts[0] if evts else f"EVT-BUL-{pid}-{fdate.replace('-', '')}"
                    p["event_ids"].add(evt_id)
                    stg_val = infer_stage(line)
                    evt_entry = {
                        "event_id": evt_id,
                        "project_id": pid,
                        "event_date": fdate,
                        "stage": stg_val,
                        "title": clean_l[:60],
                        "snippet": line[:300].strip(),
                        "source_file": fname
                    }
                    p["history_timeline"].append(evt_entry)
                    events.append(evt_entry)

            i += 1

    print(f"[PARSER] Raw extraction complete: {len(projects)} distinct projects, {len(events)} events.")

    # Consolidation and normalization
    for pid, p in projects.items():
        # Title selection: prefer longest meaningful Chinese/bilingual title
        valid_titles = [t for t in p["raw_titles"] if len(t) >= 4 and not t.isdigit()]
        if valid_titles:
            # pick best title
            best_t = max(valid_titles, key=lambda x: (len(x) < 45, len(x)))
            p["project_name_cn"] = best_t
        else:
            p["project_name_cn"] = f"项目 {pid}"

        # Investor
        valid_invs = [inv for inv in p["raw_investors"] if len(inv) >= 2]
        if valid_invs:
            p["investor_name"] = valid_invs[-1] # latest
        else:
            # try to extract company name from title
            m_comp = re.search(r'([A-Za-z0-9\u4e00-\u9fa5]+(?:集团|科技|工业|股份|有限|能源|石化|电子|控股|公司|电机|合金|特焊|重工|纸业|国际|投资|开发|商业))', p["project_name_cn"])
            if m_comp:
                p["investor_name"] = m_comp.group(1)
            else:
                p["investor_name"] = "待核验主体"

        # Country
        combined_text = " ".join(p["raw_investors"] + p["raw_titles"] + p["raw_sectors"])
        p["origin_country"] = clean_country(combined_text)

        # Province
        comb_prov = " ".join(p["raw_provinces"] + p["raw_titles"])
        found_prov = clean_province(comb_prov)
        if not found_prov and p["history_timeline"]:
            # check recent snippets
            recent_snips = " ".join([evt["snippet"] for evt in p["history_timeline"][-3:]])
            found_prov = clean_province(recent_snips)
        p["province"] = found_prov or "多省/全国"

        # Industrial Park
        comb_all_text = " ".join(p["raw_provinces"] + p["raw_titles"] + [evt["snippet"] for evt in p["history_timeline"][-2:]])
        m_ip = re.search(r'([A-ZÀ-Ỹa-z0-9\u4e00-\u9fa5\s]+(?:工业园|工业区|KCN|Khu công nghiệp|VSIP|Song Khoai|Đình Vũ|Deep C|Phú Mỹ|Yên Bình|Hiệp Phước|Nhơn Trạch))', comb_all_text)
        if m_ip:
            p["industrial_park"] = m_ip.group(1).replace('*', '').strip()[:35]

        # Scale / Amount
        if p["raw_amounts"]:
            p["scale_capacity"] = p["raw_amounts"][-1]
        else:
            p["scale_capacity"] = "投资额未公开/待补充"

        # Sector
        if p["raw_sectors"]:
            p["sector"] = p["raw_sectors"][-1]
        else:
            # infer sector from text
            comb_all = combined_text + " " + p["project_name_cn"]
            if any(x in comb_all for x in ["芯片", "半导体", "电子", "pcb", "led", "显示", "oled"]):
                p["sector"] = "电子与半导体"
            elif any(x in comb_all for x in ["光伏", "风电", "能源", "储能", "电力", "lng"]):
                p["sector"] = "新能源与清洁电力"
            elif any(x in comb_all for x in ["汽车", "零部件", "装备", "机械", "模具", "航空"]):
                p["sector"] = "高端装备与汽车制造"
            elif any(x in comb_all for x in ["物流", "仓储", "港口", "机场", "码头"]):
                p["sector"] = "物流基础设施与供应链"
            elif any(x in comb_all for x in ["化工", "橡胶", "钢铁", "新材料", "纸业", "造纸", "纺织"]):
                p["sector"] = "基础材料与先进制造"
            elif any(x in comb_all for x in ["数据中心", "算力", "云"]):
                p["sector"] = "数字经济与算力中心"
            else:
                p["sector"] = "综合实体产业"

        # Lifecycle stage
        if p["raw_stages"]:
            p["current_stage"] = infer_stage(" ".join(p["raw_stages"]))

        # Sort timeline by date
        p["history_timeline"].sort(key=lambda x: x["event_date"])

    return {
        "projects": projects,
        "events": events,
        "macro_records": macro_records,
        "thematic_records": thematic_records
    }

def save_to_database(parsed_data: Dict[str, Any]):
    projects = parsed_data["projects"]
    events = parsed_data["events"]
    macro_records = parsed_data["macro_records"]
    thematic_records = parsed_data["thematic_records"]

    print(f"[DB] Ingesting to {PROJECTS_DB_PATH}...")
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    c = conn.cursor()

    # Create / update tables
    c.execute("DROP TABLE IF EXISTS historical_macro_stats")
    c.execute("DROP TABLE IF EXISTS historical_thematic_packs")

    c.execute("""
    CREATE TABLE historical_macro_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_date TEXT,
        registered_usd_bn REAL,
        disbursed_usd_bn REAL,
        source_file TEXT,
        summary TEXT
    )
    """)

    c.execute("""
    CREATE TABLE historical_thematic_packs (
        theme_id TEXT PRIMARY KEY,
        theme_name TEXT,
        file_name TEXT,
        date TEXT,
        summary TEXT
    )
    """)

    # Deduplicate macro stats by (registered, disbursed)
    seen_macro = set()
    for m in macro_records:
        key = (m["registered_usd_bn"], m["disbursed_usd_bn"])
        if key in seen_macro:
            continue
        seen_macro.add(key)
        c.execute("""
        INSERT INTO historical_macro_stats (period_date, registered_usd_bn, disbursed_usd_bn, source_file, summary)
        VALUES (?, ?, ?, ?, ?)
        """, (m["period_date"], m["registered_usd_bn"], m["disbursed_usd_bn"], m["source_file"], m["summary"]))

    # Ingest thematic packs
    for t in thematic_records:
        c.execute("""
        INSERT OR REPLACE INTO historical_thematic_packs (theme_id, theme_name, file_name, date, summary)
        VALUES (?, ?, ?, ?, ?)
        """, (t["theme_id"], t["theme_name"], t["file_name"], t["date"], t["summary"]))

    # Ingest projects
    inserted_p = 0
    updated_p = 0
    for pid, p in projects.items():
        # Check if project exists
        existing = c.execute("SELECT project_id FROM projects WHERE project_id = ?", (pid,)).fetchone()
        if existing:
            c.execute("""
            UPDATE projects SET
                project_name_cn = CASE WHEN ? != '' AND ? NOT LIKE '项目 PRJ%' THEN ? ELSE project_name_cn END,
                investor_name = CASE WHEN ? != '待核验主体' THEN ? ELSE investor_name END,
                origin_country = CASE WHEN ? != '未知/跨国' THEN ? ELSE origin_country END,
                province = CASE WHEN ? != '多省/全国' THEN ? ELSE province END,
                industrial_park = COALESCE(NULLIF(?, ''), industrial_park),
                sector = CASE WHEN ? != '综合实体产业' THEN ? ELSE sector END,
                scale_capacity = CASE WHEN ? != '投资额未公开/待补充' THEN ? ELSE scale_capacity END,
                current_stage = ?,
                updated_at = ?
            WHERE project_id = ?
            """, (
                p["project_name_cn"], p["project_name_cn"], p["project_name_cn"],
                p["investor_name"], p["investor_name"],
                p["origin_country"], p["origin_country"],
                p["province"], p["province"],
                p["industrial_park"],
                p["sector"], p["sector"],
                p["scale_capacity"], p["scale_capacity"],
                p["current_stage"],
                p["last_seen_date"], pid
            ))
            updated_p += 1
        else:
            c.execute("""
            INSERT INTO projects (
                project_id, project_name, project_name_cn, investor_name, parent_company,
                origin_country, province, district_commune, industrial_park, sector,
                scale_capacity, current_stage, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, p["project_name_cn"], p["project_name_cn"], p["investor_name"],
                p["investor_name"], p["origin_country"], p["province"], "",
                p["industrial_park"], p["sector"], p["scale_capacity"], p["current_stage"],
                p["first_seen_date"], p["last_seen_date"]
            ))
            inserted_p += 1

        # Also register company if valid investor
        if p["investor_name"] and p["investor_name"] != "待核验主体":
            cid = f"COMP-{pid}"
            c.execute("""
            INSERT OR IGNORE INTO companies (company_id, company_name, origin_country, industry)
            VALUES (?, ?, ?, ?)
            """, (cid, p["investor_name"], p["origin_country"], p["sector"]))

        # Ingest timeline events
        for evt in p["history_timeline"]:
            fp_hash = hashlib.sha256(f"{pid}_{evt['event_date']}_{evt['event_id']}_{evt['title']}".encode('utf-8')).hexdigest()
            c.execute("""
            INSERT OR REPLACE INTO project_timeline (
                event_id, project_id, event_date, stage, title, snippet, source_id, source_name, raw_fingerprint, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evt["event_id"], pid, evt["event_date"], evt["stage"],
                evt["title"], evt["snippet"], "SRC-HISTORICAL-ARCHIVE",
                evt["source_file"], fp_hash, f"file:///{os.path.abspath(os.path.join(HISTORICAL_DIR, evt['source_file']))}"
            ))

    conn.commit()
    conn.close()

    print(f"[DB] Success: {inserted_p} new projects inserted, {updated_p} existing updated.")
    print(f"[DB] Inserted/updated timeline events into project_timeline.")
    print(f"[DB] Inserted {len(macro_records)} macro records and {len(thematic_records)} thematic packs.")

    # Export full JSON
    export_payload = {
        "metadata": {
            "title": "Vietnam Industrial & FDI Intelligence Historical Repository",
            "coverage_start": "2026-07-12",
            "coverage_end": "2026-11-03",
            "total_projects": len(projects),
            "total_timeline_events": len(events),
            "total_macro_snapshots": len(macro_records),
            "generated_at": "2026-11-03"
        },
        "projects": projects,
        "macro_stats": macro_records,
        "thematic_packs": thematic_records
    }
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as fp:
        json.dump(export_payload, fp, ensure_ascii=False, indent=2, default=str)
    print(f"[JSON] Exported comprehensive dossier to {OUTPUT_JSON_PATH}.")

def run():
    parsed_data = parse_all_reports()
    save_to_database(parsed_data)

if __name__ == "__main__":
    run()
