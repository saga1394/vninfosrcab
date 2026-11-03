"""
Directional Backward-Trace Query Engine for Vietnam FDI & Industrial Intelligence.
Adheres to 6152 Plan and AGENTS.md rules:
- Enables instant reverse-lookup of any project, company, province, or sector in the historical archive.
- Fetches full historical timeline, previous capex rounds, location details, and evidence links.
- Supports both CLI invocation and programmatic import in daily pipelines.

Usage:
    python scripts/stage2/query_history.py "光宝"
    python scripts/stage2/query_history.py PRJ117
    python scripts/stage2/query_history.py --province "北宁"
    python scripts/stage2/query_history.py --sector "半导体"
    python scripts/stage2/query_history.py --macro
"""

import sys
import os
import sqlite3
import argparse
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECTS_DB_PATH = "data/stage2/projects.db"

STAGE_NAMES = {
    "IRC_APPROVED": "获批立项 (IRC Approved)",
    "SITE_CLEARANCE": "征地拆迁 (Site Clearance)",
    "EIA_CONSULTED": "环评公示 (EIA Consulted)",
    "PERMIT_APPLIED": "排污许可 (Permit Applied)",
    "CONSTRUCTING": "开工建设 (Constructing)",
    "OPERATING": "试产商运 (Operating / Commissioned)",
    "EXPANDING_EXIT": "增资扩产/并购退出 (Expanding / Exit / M&A)"
}

ZH_TO_VN_PROVINCES = {
    "北宁": "Bắc Ninh", "海防": "Hải Phòng", "广宁": "Quảng Ninh",
    "太原": "Thái Nguyên", "河内": "Hà Nội", "胡志明": "Hồ Chí Minh",
    "西宁": "Tây Ninh", "岘港": "Đà Nẵng", "同奈": "Đồng Nai",
    "义安": "Nghệ An", "乂安": "Nghệ An", "富寿": "Phú Thọ",
    "宁平": "Ninh Bình", "兴安": "Hưng Yên", "广南": "Quảng Nam",
    "平阳": "Bình Dương", "巴地头顿": "Bà Rịa - Vũng Tàu", "头顿": "Bà Rịa - Vũng Tàu",
    "平福": "Bình Phước", "隆安": "Long An", "前江": "Tiền Giang",
    "林同": "Lâm Đồng", "庆和": "Khánh Hòa", "广义": "Quảng Ngãi",
    "平定": "Bình Định", "嘉莱": "Gia Lai", "多乐": "Đắk Lắk", "得乐": "Đắk Lắk",
    "顺化": "Thừa Thiên Huế", "河南": "Hà Nam", "海阳": "Hải Dương",
    "永福": "Vĩnh Phúc", "清化": "Thanh Hóa", "河静": "Hà Tĩnh",
    "广治": "Quảng Trị", "芹苴": "Cần Thơ", "坚江": "Kiên Giang",
    "朔庄": "Sóc Trăng", "和平": "Hòa Bình", "山罗": "Sơn La",
    "老街": "Lào Cai", "安沛": "Yên Bái"
}

def query_project(query: str, province: str = None, sector: str = None, limit: int = 10):
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sql = """
    SELECT p.*
    FROM projects p
    WHERE 1=1
    """
    params = []

    if query:
        q_upper = query.strip().upper()
        if q_upper.startswith("PRJ"):
            sql += " AND p.project_id = ?"
            params.append(q_upper)
        else:
            # check if query is a province
            q_vn_prov = ZH_TO_VN_PROVINCES.get(query.strip())
            sql += """ AND (
                p.project_id LIKE ? OR
                p.project_name_cn LIKE ? OR
                p.investor_name LIKE ? OR
                p.parent_company LIKE ? OR
                p.sector LIKE ? OR
                p.province LIKE ?
            """
            pattern = f"%{query.strip()}%"
            params.extend([pattern, pattern, pattern, pattern, pattern, pattern])
            if q_vn_prov:
                sql += " OR p.province LIKE ?"
                params.append(f"%{q_vn_prov}%")
            sql += ")"

    if province:
        prov_clean = ZH_TO_VN_PROVINCES.get(province.strip(), province.strip())
        sql += " AND (p.province LIKE ? OR p.province LIKE ?)"
        params.extend([f"%{prov_clean}%", f"%{province.strip()}%"])

    if sector:
        sql += " AND (p.sector LIKE ? OR p.project_name_cn LIKE ?)"
        params.extend([f"%{sector.strip()}%", f"%{sector.strip()}%"])

    sql += " ORDER BY p.project_id ASC LIMIT ?"
    params.append(limit)

    rows = c.execute(sql, params).fetchall()

    if not rows:
        print(f"\n[QUERY] 未检索到匹配条件的项目 (查询词: '{query}', 省份: '{province}', 赛道: '{sector}')")
        conn.close()
        return []

    print("\n" + "=" * 80)
    print(f"  🔍 定向反向回溯结果：共命中 {len(rows)} 个历史实体项目")
    print("=" * 80)

    results = []
    for r in rows:
        pid = r["project_id"]
        # Fetch timeline
        t_sql = """
        SELECT event_id, event_date, stage, title, snippet, source_name, url
        FROM project_timeline
        WHERE project_id = ?
        ORDER BY event_date ASC, event_id ASC
        """
        timeline = c.execute(t_sql, (pid,)).fetchall()

        stage_cn = STAGE_NAMES.get(r["current_stage"], r["current_stage"])
        print(f"\n📌 【{pid}】{r['project_name_cn']}")
        print(f"   🏢 投资主体：{r['investor_name'] or '未知'} （来源国别：{r['origin_country'] or '未知'}）")
        print(f"   📍 落地省份：{r['province'] or '未知'} ｜ 园区/地点：{r['industrial_park'] or '未指明'}")
        print(f"   💼 产业赛道：{r['sector'] or '综合制造业'} ｜ 投资规模：{r['scale_capacity'] or '未公开'}")
        print(f"   ⚡ 当前生命周期阶段：{stage_cn}")
        print(f"   📅 记录时间跨度：{r['created_at']} 至 {r['updated_at']} （累计 {len(timeline)} 次重大事件/更新）")

        if timeline:
            print("   📜 历史时间线演进（自早至晚）：")
            for t in timeline:
                stg_label = STAGE_NAMES.get(t["stage"], t["stage"])
                snip = (t["snippet"] or "").replace("\n", " ").strip()
                if len(snip) > 120:
                    snip = snip[:120] + "..."
                print(f"      • [{t['event_date']}] [{stg_label}] {t['title']}")
                if snip and snip != t["title"]:
                    print(f"        摘要: {snip}")
                if t["source_name"]:
                    print(f"        出处: {t['source_name']}")

        print("-" * 80)
        results.append(dict(r))

    conn.close()
    return results

def show_macro_timeline():
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    rows = c.execute("""
    SELECT period_date, registered_usd_bn, disbursed_usd_bn, source_file, summary
    FROM historical_macro_stats
    WHERE registered_usd_bn IS NOT NULL OR disbursed_usd_bn IS NOT NULL
    ORDER BY period_date ASC
    """).fetchall()

    print("\n" + "=" * 80)
    print("  📊 越南官方 FDI 宏观时间序列基石 (FIA / NSO 一手发布)")
    print("=" * 80)
    print(f"{'期次/发布日':<14} | {'年内新增注册(亿美元)':<20} | {'实际到位资金(亿美元)':<20} | {'一手出处文件'}")
    print("-" * 80)
    for r in rows:
        reg = f"${r['registered_usd_bn']:.1f} 亿" if r['registered_usd_bn'] else "未拆分"
        dis = f"${r['disbursed_usd_bn']:.1f} 亿" if r['disbursed_usd_bn'] else "未拆分"
        print(f"{r['period_date']:<14} | {reg:<22} | {dis:<22} | {r['source_file']}")
    print("-" * 80)
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Vietnam FDI History Reverse-Lookup Query Tool")
    parser.add_argument("query", nargs="?", default="", help="Company name, project name, or PRJ ID (e.g., '光宝', 'PRJ117')")
    parser.add_argument("--province", "-p", help="Filter by province (e.g., '北宁', '广宁')")
    parser.add_argument("--sector", "-s", help="Filter by sector (e.g., '半导体', '新能源', '汽车')")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Maximum number of results to display")
    parser.add_argument("--macro", "-m", action="store_true", help="Display official macroeconomic FDI time series")

    args = parser.parse_args()

    if args.macro:
        show_macro_timeline()
        return

    if not args.query and not args.province and not args.sector:
        print("\n使用方法:")
        print("  python scripts/stage2/query_history.py <企业或项目名称/PRJ编号>")
        print("  python scripts/stage2/query_history.py --province <省份>")
        print("  python scripts/stage2/query_history.py --sector <赛道>")
        print("  python scripts/stage2/query_history.py --macro  (查看宏观FDI时间线)")
        print("\n示例:")
        print("  python scripts/stage2/query_history.py 光宝")
        print("  python scripts/stage2/query_history.py PRJ266")
        print("  python scripts/stage2/query_history.py --province 北宁")
        return

    query_project(args.query, args.province, args.sector, args.limit)

if __name__ == "__main__":
    main()
