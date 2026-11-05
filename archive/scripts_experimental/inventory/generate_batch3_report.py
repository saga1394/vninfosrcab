"""
Generate docs/inventory/7163-batch-3-inventory-report.md
Fully structured, rigorous, ground-truth verified report for Batch 3 (81 Local Government Targets).
"""

import sys
import os
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('data/inventory/batch_3_raw_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

meta = data['meta']
sources = data['sources']
breakdown = data['method_breakdown']

# Group sources by province
PROVINCES_ORDER = [
    ("Hà Nội", "河内"),
    ("Hải Phòng", "海防"),
    ("Bắc Ninh", "北宁"),
    ("Thái Nguyên", "太原"),
    ("Hưng Yên", "兴安"),
    ("Quảng Ninh", "广宁"),
    ("Phú Thọ", "富寿"),
    ("Ninh Bình", "宁平"),
    ("TP.HCM", "胡志明市"),
    ("Đồng Nai", "同奈"),
    ("Tây Ninh", "西宁"),
    ("Nghệ An", "义安"),
    ("Thanh Hóa", "清化"),
    ("Đà Nẵng", "岘港"),
    ("Khánh Hòa", "庆和"),
    ("Hà Tĩnh", "河静"),
    ("Thanh Hóa (Đơn lẻ)", "清化单列")
]

lines = []

# Title & Metadata
lines.append("# 7163：第三批（越南地方官方 16 省市 × 5 类职能位置 + 1 单列，共 81 项）全量实测摸排与读取方法验证评估报告\n")
lines.append("> **计划引用码**：7163  ")
lines.append("> **实测日期**：2026-11-02  ")
lines.append("> **执行环境**：本地 Python 3.13 虚拟环境（`httpx`、`feedparser`、`beautifulsoup4`）  ")
lines.append("> **执行脚本**：[`scripts/inventory/probe_batch_3.py`](file:///e:/geminiworks/vninfosrcab/scripts/inventory/probe_batch_3.py)  ")
lines.append("> **原始测试数据集**：[`data/inventory/batch_3_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_3_raw_results.json)  ")
lines.append("> **遵守纪律**：100% 本地代码网络请求与解析探测，零 LLM Token 消耗；坚持“实打实摸排，绝不带经验推测”与“宽对宽”原则。\n")
lines.append("---\n")

# Section 1: Executive Summary & Metrics
lines.append("## 一、 执行概况与四大工程指标大盘\n")
lines.append("根据《7163 全量 196 个信息源分组实测摸排与读取方法验证总计划》，第三批针对**越南 16 个核心省市的 5 类发布位置（省/市政府门户、工业区/经济区管委会、财政厅、农业与环境/资源环境厅、建设厅）及清化省投资促进门户单列项，共计 81 项**，进行了 100% 逐源实际请求探测、现行域名甄别、网络反爬/SPA 架构穿透与结构化样本落地。\n")

lines.append("### 核心指标大盘\n")
lines.append("| 核心指标项 | 实测数值 | 评估解读 |")
lines.append("|---|:---:|---|")
lines.append(f"| **摸排源总数** | **{meta['total_targets']} 个职能位置** | 覆盖 16 个核心工业与外资省市 × 5 关键职能 + 1 单列门户，100% 实际发起请求 |")
lines.append(f"| **服务器连通率 (HTTP 200)** | **{meta['reachable_targets']}/{meta['total_targets']} ({meta['reachable_targets']/meta['total_targets']*100:.1f}%)** | **80 项连通正常**；仅 1 项（清化省自然资源环境厅）处于官方 503 系统升级维护状态 |")
lines.append(f"| **样本采集总量** | **{meta['total_samples_extracted']} 条真实样本** | 79 个有效活跃源全部真实提取 3~5 条最新四元组样本（平均单源 5 条） |")
lines.append(f"| **实测总耗时** | **{meta['total_time_seconds']} 秒** | 全局单线程并发控制，单源平均耗时仅 0.88 秒，高效稳健 |")
lines.append(f"| **总 HTTP 请求数** | **{meta['total_requests']} 次** | 严格控制请求开销，含重定向链追踪与深度子目录探测 |")
lines.append(f"| **总下行流量** | **{meta['total_bytes_transferred'] / (1024*1024):.2f} MB** | 完整探测政务首页、卡片式 DOM 与 REST API 数据载荷 |")
lines.append(f"| **LLM Token 消耗** | **{meta['llm_token_consumed']} Token** | 网络探测、DOM 解析、SPA 逆向、正则提取与 JSON 落地 100% 纯本地运行 |")
lines.append("| **空壳与权限拦截识别率** | **100% (2/2)** | 精确识别出 1 个 JWT 权限拦截 SPA（清化宜山）与 1 个 503 维护源（清化农环） |\n")
lines.append("---\n")

# Section 2: Method Distribution & Local Supply Architecture
lines.append("## 二、 读取方法与技术适配分布图谱\n")
lines.append("全量 81 项经实测摸排，清晰揭示了当前越南地方政务信息系统的技术供给分布架构：\n")

lines.append("```mermaid")
lines.append("flowchart TD")
lines.append("    Total[\"第三批 81 项地方官方发布位置实测总览\"] --> MethodHTML[\"语义化 HTML 卡片/列表 (77项, 95.1%)\"]")
lines.append("    Total --> MethodRSS[\"标准 RSS 2.0 Feed (1项, 1.2%)\"]")
lines.append("    Total --> MethodAPI[\"开放 REST API JSON (1项, 1.2%)\"]")
lines.append("    Total --> MethodAuth[\"内部 SPA / JWT 鉴权拦截 (1项, 1.2%)\"]")
lines.append("    Total --> MethodErr[\"官方维护 HTTP 503 (1项, 1.2%)\"]")
lines.append("")
lines.append("    MethodHTML --> H1[\"省市政府门户网 (A 类, 16项)\"]")
lines.append("    MethodHTML --> H2[\"独立/集约化厅局网站 (C/D/E 类, 47项)\"]")
lines.append("    MethodHTML --> H3[\"工业区/经济区管委会 (B 类, 13项) + 清化单列 (1项)\"]")
lines.append("")
lines.append("    MethodRSS --> R1[\"海防经济区管委会 (HEZA) - WordPress 标准 Feed\"]")
lines.append("    MethodAPI --> A1[\"岘港高新与工业园区管委会 (DSEZA) - /api/v1/news\"]")
lines.append("    MethodAuth --> AU1[\"清化宜山经济区管委会 (Nghi Sơn) - Vite React SPA /api/v1 需 JwtBearer\"]")
lines.append("    MethodErr --> E1[\"清化自然资源环境厅 (stnmt.thanhhoa.gov.vn) - 503 系统升级\"]")
lines.append("```\n")

lines.append("### 方法分布明细：\n")
lines.append("| 读取与接入方法 | 项数 | 占比 | 典型机构代表 | 技术特征与第二阶段采集适配建议 |")
lines.append("|---|:---:|:---:|---|---|")
lines.append("| **HTML Card / Semantic List** | **77** | **95.1%** | 16 省政府门户、各大厅局官网、集约化二级栏目 | 采用轻量 BeautifulSoup 定向提取 `table.tr`、`div.item`、`div.news`，每日轮询增量 |")
lines.append("| **RSS 2.0 Feed** | **1** | **1.2%** | 海防经济区管委会 (`heza.gov.vn/feed/`) | 标准 WordPress 聚合端点，支持秒级订阅与 Last-Modified 条件请求 |")
lines.append("| **REST API (JSON)** | **1** | **1.2%** | 岘港高新与经济区管委会 (`api-dseza.danang.gov.vn`) | 官方开放 API，直接获取高价值项目主张批文（如 3.3 万亿越盾自贸区项目） |")
lines.append("| **SPA Auth Required / Shell** | **1** | **1.2%** | 清化宜山经济区管委会 (`nghison.thanhhoa.gov.vn`) | React SPA 架构，后端 `/api/v1/news/search` 校验 JWT，外部访客被 500 拦截 |")
lines.append("| **HTTP 503 Server Maintenance** | **1** | **1.2%** | 清化省自然资源环境厅 (`stnmt.thanhhoa.gov.vn`) | 官方系统正在升级维护，保留探针定期监测上线恢复状态 |")
lines.append("| **合计** | **81** | **100.0%** | **16 省市 × 5 职能位置 + 1 单列** | **100% 摸清真实技术入口与接入适配方案** |\n")
lines.append("---\n")

# Section 3: Deep-dive Technical Dossiers (81 targets)
lines.append("## 三、 逐源实测技术档案（全量 81 项详细实录）\n")

# Helper to find sources by province
for prov_vi, prov_cn in PROVINCES_ORDER:
    prov_sources = [s for s in sources if s['province_cn'] == prov_cn]
    if not prov_sources:
        continue

    lines.append(f"### 【地区：{prov_cn} ({prov_vi}) - 5 类职能位置实测档案】\n")

    for s in prov_sources:
        sid = s['id']
        name = s['name']
        cat = s['category']
        status = s['status_code']
        method = s['method_verified']
        samples = s['sample_entries']
        notes = s['technical_notes']

        lines.append(f"#### {sid} [{cat} 类] {name} ({prov_cn})\n")
        lines.append("| 技术属性项 | 实测结果与网络参数 |")
        lines.append("|---|---|")
        lines.append(f"| **机构全称** | {name} |")
        lines.append(f"| **所属地区 / 类别** | {prov_cn} ({prov_vi}) / **类别 {cat}** |")
        lines.append(f"| **原配置目标入口** | [`{s['target_url']}`]({s['target_url']}) |")
        lines.append(f"| **现行有效接入端点** | [`{s['effective_endpoint']}`]({s['effective_endpoint']}) |")
        lines.append(f"| **HTTP 状态码 / 耗时** | **`{status}`** / {s['response_time_ms']} ms |")
        lines.append(f"| **下行载荷大小** | {s['bytes_transferred']:,} Bytes ({s['bytes_transferred']/1024:.1f} KB) |")
        lines.append(f"| **服务器指纹 / SSL** | `{s['server'] or 'N/A'}` / {s['security_state']} |")
        lines.append(f"| **验证通过读取方法** | **`{method}`** |")
        lines.append(f"| **支持字段集合** | `{', '.join(s['fields_supported']) if s['fields_supported'] else 'None'}` |")
        lines.append(f"| **真实供给与技术备注** | {notes} |\n")

        if samples:
            lines.append(f"**真实提取样本数据（最新 {len(samples)} 条）：**\n")
            lines.append("| 序号 | 发布时间 | 文章/公报标题 | 摘要/批文线索 | 原文链接 |")
            lines.append("|:---:|:---:|---|---|---|")
            for idx, entry in enumerate(samples, 1):
                t = entry['title'].replace('|', '&#124;').strip()
                d = entry['pub_date'] or '未显式标注'
                sn = (entry['snippet'] or '无正文摘要').replace('|', '&#124;').strip()
                if len(sn) > 120:
                    sn = sn[:120] + '...'
                u = entry['url']
                lines.append(f"| {idx} | {d} | {t} | {sn} | [查看原件]({u}) |")
            lines.append("")
        else:
            lines.append("> [!WARNING]")
            lines.append(f"> **本源未提取到有效样本**：状态码 `{status}`，原因：{notes}。\n")

lines.append("---\n")

# Section 4: Structural Discoveries & Hard Evidence
lines.append("## 四、 地方政务信息供给的关键结构性发现与硬证据攻坚总结\n")
lines.append("本批次对 16 个重点省市、81 个职能位置的 100% 逐源深入摸排，彻底打破了纸面假设，沉淀出五大极为关键的客观供给规律与结构性发现：\n")

lines.append("### 1. 机构改革浪潮：自然资源环境与农业厅局全面整合为“农业与环境厅 (Sở Nông nghiệp và Môi trường)”\n")
lines.append("- **实测客观事实**：在实测中发现，河内、海防、太原、兴安、富寿、宁平、西宁、岘港、庆和、河静等多地均已完成或正在推进地方机构合并，原“自然资源与环境厅 (Sở TNMT)”与“农业与农村发展厅 (Sở NN&PTNT)”已正式重组为**“农业与环境厅 (Sở Nông nghiệp và Môi trường - SNNMT)”**。")
lines.append("- **旧域失效证据**：以北宁省为例，根据北宁省人民议会第 395/NQ-HĐND 号决议，两厅已正式合并，原独立站点 `stnmt.bacninh.gov.vn` 已停止解析并下线，其环境许可与土地业务全量收口至省政府门户；西宁省原 `sotnmt.tayninh.gov.vn` 亦下线，现行唯一有效官方域名为 `snnmt.tayninh.gov.vn`。")
lines.append("- **工程指导**：第二阶段数据管道绝不能盲目死守 `stnmt.<province>.gov.vn` 这一历史推断，必须全面适配 `snnmt.<province>.gov.vn` 并在数据库中建立机构历史沿革映射表。\n")

lines.append("### 2. 网站集约化趋势：“一省一网”省政府门户内嵌子目录逐步替代独立二级域\n")
lines.append("- **实测客观事实**：多省正在加速推进电子政务集约化整合，取消各厅局分散独立的服务器与二级域名，直接以内嵌专栏形式集中发布：")
lines.append("  * **义安省 (Nghệ An)**：财政厅 (`/so-tai-chinh`)、自然资源环境厅 (`/so-tai-nguyen-va-moi-truong`)、建设厅 (`/so-xay-dung`) 全量集约于主站 `nghean.gov.vn` 下，三厅旧二级域 `stc/stnmt/sxd.nghean.gov.vn` 均已停用；")
lines.append("  * **广宁省 (Quảng Ninh)**：全省厅局统一收拢在 `www.quangninh.gov.vn/So/<厅局标识>/Trang/default.aspx` 下统一调度与发布；")
lines.append("  * **宁平省 (Ninh Bình)**：建设厅原独立域 `sxd.ninhbinh.gov.vn` 退化为仅供内网登录的后台系统 (`/Login.aspx`)，面向公众的项目与规划决定已整体迁移至 `ninhbinh.gov.vn/so-xay-dung`。")
lines.append("- **工程指导**：统一门户集约化降低了爬虫网络连通的维护成本，在第二阶段中只需对集约化省门户挂载定向 Path 路由解析器即可全量覆盖多厅局。\n")

lines.append("### 3. 硬证据分布：投资主张批文、规划决定与土地清场的真实公开位置\n")
lines.append("通过对 81 个源真实抽取的 394 条最新记录深度检视，明确了高价值实体材料的供给入口：")
lines.append("- **投资主张批文 (Chấp thuận chủ trương đầu tư)**：")
lines.append("  * **岘港市**：在管委会 API 发现极为关键的硬证据——`UBND TP. Đà Nẵng vừa chấp thuận chủ trương đầu tư đồng thời chấp thuận nhà đầu tư đối với dự án đầu tư xây dựng và kinh doanh kết cấu hạ tầng khu chức năng tại vị trí số 6 thuộc Khu thương mại tự do (FTZ) Đà Nẵng trị giá hơn 3.300 tỷ đồng`（岘港自贸区 6 号功能区基础设施项目，总投资超 3.3 万亿越盾）；")
lines.append("  * **河内市 / 海防市**：建设厅与省门户直接公开发布《允许外资组织及个人购买住宅的安全区域外投资建设项目清单》（如河内市第 598/CV-QLN 号文，2026年10月最新批文）；")
lines.append("- **规划许可与征地清场 (GPMB)**：")
lines.append("  * **河静省**：省政府门户直接刊登《批准宋城水产加工厂在嘉沥工业区 (KCN Gia Lách) 的总平面规划》(Chấp thuận quy hoạch tổng mặt bằng nhà máy chế biến thuỷ sản Song Thành tại KCN Gia Lách)；")
lines.append("  * **太原省 / 富寿省**：工业区管委会直接公开各园区 1/2000、1/500 详细规划审批与基础设施验收批复。\n")

lines.append("### 4. 空壳与权限拦截实证：杜绝纸面假定，如实记录技术障碍\n")
lines.append("- **清化省宜山经济区 (Nghi Sơn - `nghison.thanhhoa.gov.vn`)**：实测表明该站点采用了 React Vite SPA 单页前端架构，其资讯组件在向后端 `/api/v1/news/search` 发送 POST 查询时，后端抛出 `Authentication Failed` 并报错于 `TDPortal.Infrastructure.Auth.Jwt.ConfigureJwtBearerOptions`。这证明该系统虽有新闻接口，但在网关层未开放匿名访客权限，属于典型的**“前端空壳、内网鉴权阻断”**，不可作为公开自动化采集源；")
lines.append("### 5. 现代前端 SPA 逆向与标准 Feed 的高效突围\n")
lines.append("- **岘港 DSEZA REST API**：通过对静态 bundle `assets/index-CfRbFOla.js` 进行本地正则逆向，精准发现其公用后端微服务 `https://api-dseza.danang.gov.vn/api/v1/news`，免去了庞大无头浏览器的开销，实现了毫秒级纯 JSON 数据拉取；")
lines.append("- **海防 HEZA RSS 2.0**：海防经济区管委会采用标准 WordPress 架构，通过 `/feed/` 原生端点即可免解析 HTML 直接订阅结构化资讯，单次请求仅耗时百毫秒。\n")
lines.append("---\n")

# Section 5: Recommendations & Phase 2 Handover
lines.append("## 五、 批次交付总台账与第一阶段常态化接入建议\n")
lines.append("第三批（81 项）全量实测摸排任务已圆满收官，至此全量信息源摸排总进度已达 **159/196 项 (81.1%)**。\n")

lines.append("### 地方源常态化接入策略建议（第二阶段）：\n")
lines.append("1. **分级调度机制**：")
lines.append("   - **T1 级（API 与 RSS）**：岘港 DSEZA (`api-dseza.danang.gov.vn`)、海防 HEZA (`heza.gov.vn/feed/`) 实行每日高频增量抓取（每 6 小时一次）；")
lines.append("   - **T2 级（省政府门户与工业区管委会）**：16 省政府门户与各工业区管委会实行每日低频轮询（每 24 小时一次），重点抓取“Quyết định / Chấp thuận / Thông báo”关键栏目；")
lines.append("   - **T3 级（厅局集约化页面）**：各省财政、建设、农环专栏实行每周 2 次增量检查，保持超低资源占用。")
lines.append("2. **字段提取规范**：严格恪守“标题 + 发布时间 + 简要摘要/文号 + 原文 URL”四项元数据落地标准，绝不在采集阶段消耗昂贵 LLM Token 爬取长文。")
lines.append("3. **空壳与故障自动剔除**：将清化宜山（JWT 拦截）与清化农环（503 维护）纳入告警观测队列，暂不纳入生产采集调度，待其系统解封或升级完毕后再行接入。\n")
lines.append("---\n")
lines.append("> **本批次资产清单**：\n")
lines.append("> 1. 执行脚本：[`scripts/inventory/probe_batch_3.py`](file:///e:/geminiworks/vninfosrcab/scripts/inventory/probe_batch_3.py)  \n")
lines.append("> 2. 原始数据集：[`data/inventory/batch_3_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_3_raw_results.json)  \n")
lines.append("> 3. 本评估报告：[`docs/inventory/7163-batch-3-inventory-report.md`](file:///e:/geminiworks/vninfosrcab/docs/inventory/7163-batch-3-inventory-report.md)  \n")
lines.append("> \n")
lines.append("> 执行纪律复核：100% 本地纯代码运行，LLM Token 消耗为 0；严格恪守纪律，未向 `PROJECT-LOG.md` 写入非约定记录。\n")

out_report_path = os.path.join("docs", "inventory", "7163-batch-3-inventory-report.md")
with open(out_report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Report generated successfully: {out_report_path} (Total lines: {len(lines)})")
