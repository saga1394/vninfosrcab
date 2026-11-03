"""
Generates the Master Historical Intelligence Repository Document:
docs/stage2/HISTORICAL-INTELLIGENCE-REPOSITORY.md
Adheres to 6152 Plan and AGENTS.md rules.
"""

import sqlite3
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECTS_DB_PATH = "data/stage2/projects.db"
DOC_OUTPUT_PATH = "docs/stage2/HISTORICAL-INTELLIGENCE-REPOSITORY.md"

def generate():
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_projects = c.execute("SELECT count(*) FROM projects").fetchone()[0]
    total_events = c.execute("SELECT count(*) FROM project_timeline").fetchone()[0]
    total_companies = c.execute("SELECT count(*) FROM companies").fetchone()[0]
    total_macro = c.execute("SELECT count(*) FROM historical_macro_stats").fetchone()[0]
    total_themes = c.execute("SELECT count(*) FROM historical_thematic_packs").fetchone()[0]

    # Sector distribution
    sector_counts = c.execute("""
    SELECT sector, count(*) as cnt
    FROM projects
    GROUP BY sector
    ORDER BY cnt DESC
    """).fetchall()

    # Country distribution
    country_counts = c.execute("""
    SELECT origin_country, count(*) as cnt
    FROM projects
    WHERE origin_country != '未知/跨国'
    GROUP BY origin_country
    ORDER BY cnt DESC
    LIMIT 10
    """).fetchall()

    # Province distribution
    province_counts = c.execute("""
    SELECT province, count(*) as cnt
    FROM projects
    WHERE province != '多省/全国'
    GROUP BY province
    ORDER BY cnt DESC
    LIMIT 12
    """).fetchall()

    # Macro timeline rows
    macro_rows = c.execute("""
    SELECT period_date, registered_usd_bn, disbursed_usd_bn, source_file
    FROM historical_macro_stats
    WHERE registered_usd_bn IS NOT NULL OR disbursed_usd_bn IS NOT NULL
    ORDER BY period_date ASC
    """).fetchall()

    # Key flagship projects
    flagship_pids = [
        "PRJ117", "PRJ266", "PRJ013", "PRJ016", "PRJ020", "PRJ036",
        "PRJ118", "PRJ128", "PRJ170", "PRJ268", "PRJ281", "PRJ370",
        "PRJ418", "PRJ419", "PRJ423", "PRJ-VN-2026-ASCO-AEROSPACE",
        "PRJ-VN-2026-XUAN-THIEN-COMPLEX", "PRJ-VN-2026-SEMBCORP-WIND"
    ]
    flagship_projects = []
    for pid in flagship_pids:
        p = c.execute("SELECT * FROM projects WHERE project_id = ?", (pid,)).fetchone()
        if p:
            evt_cnt = c.execute("SELECT count(*) FROM project_timeline WHERE project_id = ?", (pid,)).fetchone()[0]
            flagship_projects.append((p, evt_cnt))

    conn.close()

    lines = []
    lines.append("# 越南实体与 FDI 情报历史信息库总台账（2026-07-12 至 2026-11-03）")
    lines.append("\n> **资产建档引用码**：6152（基于计划 `6152-2026-11-03-historical-intelligence-repository-construction.md`）")
    lines.append(f"> **全库资产总览**：累计收录实体项目 **{total_projects} 项**（涵盖 PRJ001~PRJ423 及重大综合体）｜历史时间线事件 **{total_events} 条**（EVT001~EVT642）｜核心企业主体 **{total_companies} 家**｜宏观官方数据锚点 **{total_macro} 期**｜深度专题包 **{total_themes} 组**")
    lines.append("> **定位原则（严格遵循 AGENTS.md）**：**时效收敛与定向反向回溯**。历史往期情报全面沉淀于本底座，杜绝历史旧账侵占近 48~72 小时日常早报大盘；日常巡检捕获新动向或需核实前瞻因果时，调用工具链秒级定向回溯穿透。")
    lines.append("\n---\n")

    lines.append("## 一、历史信息库全景概貌\n")
    lines.append("### 1.1 资产结构总揽\n")
    lines.append("| 资产类别 | 收录数量 | 覆盖周期 | 核心价值与证据效力 |")
    lines.append("|---|---|---|---|")
    lines.append(f"| **实体投资项目 (projects)** | **{total_projects} 个** | 2026-07 至 2026-11 | 覆盖跨国巨头、中资出海、台资算力、日韩重工与越南本土旗舰 |")
    lines.append(f"| **时间线事件 (project_timeline)** | **{total_events} 条** | 2026-07 至 2026-11 | 完整记录立项获批、开工、封顶、试产、增资扩产、合资并购全流程 |")
    lines.append(f"| **官方宏观时间序列 (historical_macro_stats)** | **{total_macro} 条** | H1 / 前7月 / 前8月 / 前9月 / 前10月 | 财政部外国投资局 (FIA) 与统计局 (NSO) 官方审批与到位资金锚点 |")
    lines.append(f"| **深度专题档案包 (thematic_packs)** | **{total_themes} 组** | 2026-08 至 2026-10 | 数据中心准入开放、半导体与VinFast链条、JLL制造业核实等 |")
    lines.append(f"| **企业实体名录 (companies)** | **{total_companies} 家** | 全周期 | 穿透上市代码、母公司国别与核心主营业务 |")

    lines.append("\n### 1.2 产业赛道分布矩阵\n")
    lines.append("| 产业赛道 | 项目数量 | 占比 | 代表性企业与重大项目 |")
    lines.append("|---|---|---|---|")
    for s in sector_counts:
        ratio = f"{s['cnt'] / total_projects * 100:.1f}%"
        lines.append(f"| **{s['sector']}** | **{s['cnt']}** | {ratio} | 涵盖该领域代表性外资与在建项目 |")

    lines.append("\n### 1.3 核心省份与来源国分布\n")
    lines.append("#### 核心枢纽省份分布（Top 12）\n")
    lines.append("| 省份 | 收录项目数 | 产业带特征与主攻方向 |")
    lines.append("|---|---|---|")
    for p in province_counts:
        lines.append(f"| **{p['province']}** | **{p['cnt']}** | 北部电子半导体/中部清洁能源/南部石化物流核心承载区 |")

    lines.append("\n#### 核心投资来源国别分布（Top 10）\n")
    lines.append("| 投资来源国别 | 项目数 | 投资偏好与典型产业 |")
    lines.append("|---|---|---|")
    for c_item in country_counts:
        lines.append(f"| **{c_item['origin_country']}** | **{c_item['cnt']}** | 供应链出海、高精制造、清洁能源或重化工 |")

    lines.append("\n---\n")

    lines.append("## 二、越南官方宏观 FDI 连续时间序列基石\n")
    lines.append("> 数据源自财政部外国投资局（FIA）与财政部统计局（NSO）一手公报与官方 XLSX 表格：\n")
    lines.append("| 节点/发布日 | 年内新增注册额 (亿美元) | 实际到位资金 (亿美元) | 关键看点与口径衔接 | 出处报告 |")
    lines.append("|---|---|---|---|---|")
    for m in macro_rows:
        reg_str = f"**${m['registered_usd_bn']:.1f} 亿**" if m['registered_usd_bn'] else "分项统计中"
        dis_str = f"**${m['disbursed_usd_bn']:.1f} 亿**" if m['disbursed_usd_bn'] else "分项统计中"
        lines.append(f"| {m['period_date']} | {reg_str} | {dis_str} | 官方核定时间序列锚点 | [`{m['source_file']}`](file:///e:/geminiworks/vninfosrcab/data/historical_reports/reports/{m['source_file']}) |")

    lines.append("\n---\n")

    lines.append("## 三、重点战略赛道与标杆旗舰项目名录（精选 18 项）\n")
    lines.append("| 编号 | 项目中文名称 | 投资主体 / 母公司 | 来源国别 | 落地省份 | 规模/金额 | 当前生命周期阶段 | 历史事件数 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for p, evts in flagship_projects:
        pid = p["project_id"]
        pname = p["project_name_cn"][:24]
        inv = (p["investor_name"] or "未披露")[:20]
        cntry = p["origin_country"] or "跨国"
        prov = p["province"] or "全国"
        scale = (p["scale_capacity"] or "未公开")[:15]
        stg = p["current_stage"]
        lines.append(f"| **{pid}** | **{pname}** | {inv} | {cntry} | {prov} | {scale} | `{stg}` | **{evts} 次更新** |")

    lines.append("\n---\n")

    lines.append("## 四、定向反向回溯工具使用指引（Backward-Trace Engine）\n")
    lines.append("历史信息库沉淀后，日常巡检和研究分析**无需翻阅海量历史旧闻**。遇到任何企业、项目、省份或赛道线索时，通过本地 Python 引擎秒级调用：\n")
    lines.append("### 4.1 常用查询命令\n")
    lines.append("```bash")
    lines.append("# 1. 按企业或项目名称检索（支持中英文/简写/代码）")
    lines.append('python scripts/stage2/query_history.py "光宝"')
    lines.append('python scripts/stage2/query_history.py "SCG"')
    lines.append('python scripts/stage2/query_history.py "Pacifico"')
    lines.append('python scripts/stage2/query_history.py "五新智能"')
    lines.append('python scripts/stage2/query_history.py "博威"')
    lines.append("")
    lines.append("# 2. 按项目编号精准检索（秒级输出全周期时间线演进）")
    lines.append("python scripts/stage2/query_history.py PRJ117")
    lines.append("python scripts/stage2/query_history.py PRJ266")
    lines.append("")
    lines.append("# 3. 按核心省份筛选项目组合")
    lines.append('python scripts/stage2/query_history.py --province "北宁" -n 10')
    lines.append('python scripts/stage2/query_history.py --province "广宁"')
    lines.append('python scripts/stage2/query_history.py --province "海防"')
    lines.append("")
    lines.append("# 4. 按产业赛道筛选")
    lines.append('python scripts/stage2/query_history.py --sector "半导体"')
    lines.append('python scripts/stage2/query_history.py "数据中心"')
    lines.append("")
    lines.append("# 5. 查看越南国家级 FDI 宏观时间序列基石")
    lines.append("python scripts/stage2/query_history.py --macro")
    lines.append("```")

    lines.append("\n### 4.2 程序化调用接口（供 Stage 2 及日常巡检脚本集成）\n")
    lines.append("```python")
    lines.append("from scripts.stage2.query_history import query_project")
    lines.append("")
    lines.append("# 当日巡检命中 '光宝科技' 时，自动提取历史背景以辅助大模型判断")
    lines.append('history_records = query_project("光宝科技", limit=1)')
    lines.append("if history_records:")
    lines.append("    print('发现历史项目背景：', history_records[0]['project_name_cn'])")
    lines.append("```")

    lines.append("\n---\n")

    lines.append("## 五、历史深度专题档案包清单\n")
    lines.append("| 专题代号 | 专题名称 | 档案来源文件 | 核心内容提要 |")
    lines.append("|---|---|---|---|")
    lines.append("| `THEME-DATACENTER` | 越南数据中心外资准入与基础设施布局 | [`2026-08-31-datacenter-topic-pack.md`](file:///e:/geminiworks/vninfosrcab/data/historical_reports/reports/2026-08-31-datacenter-topic-pack.md) | 法规对外资全资开放、电信三巨头 (Viettel/VNPT/FPT) 算力基建、海外资本 STT/GDS/BW/EdgeConneX 竞合格局 |")
    lines.append("| `THEME-SEMICON-AUTO` | 越南半导体与VinFast汽车供应链协同专题 | [`2026-10-06-半导体与VinFast链条-三条快讯原文.md`](file:///e:/geminiworks/vninfosrcab/data/historical_reports/reports/2026-10-06-半导体与VinFast链条-三条快讯原文.md) | 北宁安平半导体封装基板、VinFast纯电生态与配套车规级芯片国产化 |")
    lines.append("| `THEME-JLL-FDI` | JLL越南制造业FDI份额真实性核实 | [`2026-10-02-核查-JLL制造业FDI份额.md`](file:///e:/geminiworks/vninfosrcab/data/historical_reports/reports/2026-10-02-核查-JLL制造业FDI份额.md) | JLL 机构研报数据与官方 FIA 数据口径的差异对账与交叉印证 |")
    lines.append("| `THEME-BOYING-HRSG` | 博盈特焊越南基地发展时间线 | [`2026-10-24-博盈特焊越南基地-新闻与影像时间线.md`](file:///e:/geminiworks/vninfosrcab/data/historical_reports/reports/2026-10-24-博盈特焊越南基地-新闻与影像时间线.md) | 中资特种装备出海标杆：8条产线达产、HRSG余热锅炉国际订单交付 |")

    lines.append("\n---\n*本台账由 `scripts/stage2/generate_historical_repository_doc.py` 自动化编译生成，数据源自 `data/stage2/projects.db`。*")

    os.makedirs(os.path.dirname(DOC_OUTPUT_PATH), exist_ok=True)
    with open(DOC_OUTPUT_PATH, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(lines))

    print(f"[DOC] Generated Master Historical Repository document at {DOC_OUTPUT_PATH}.")

if __name__ == "__main__":
    generate()
