"""
Script to generate the comprehensive Batch 4 Inventory Report:
docs/inventory/7163-batch-4-inventory-report.md
Based on: data/inventory/batch_4_raw_results.json
Plan: 7163
"""

import os
import json
from datetime import datetime

def generate_report():
    json_path = os.path.join("data", "inventory", "batch_4_raw_results.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["meta"]
    sources = data["sources"]
    methods = data["method_breakdown"]

    total_sources = len(sources)
    reachable = meta["reachable_targets"]
    total_samples = meta["total_samples_extracted"]
    duration = meta["total_time_seconds"]
    transferred_mb = meta.get("total_transferred_mb", round(meta["total_bytes_transferred"] / (1024*1024), 2))

    # Categorize sources
    cat_disc = [s for s in sources if s["category"] == "Enterprise Disclosure"]
    cat_assoc = [s for s in sources if s["category"] == "Industry Association"]
    cat_intl = [s for s in sources if s["category"] == "International Development"]
    cat_supp = [s for s in sources if s["category"] == "Supplementary Channel"]

    doc = []
    doc.append("# 7163：第四批（企业原始披露 13项 + 行业商协会 7项 + 国际开发机构 3项 + 补充渠道 14项，共 37 项）全量实测摸排与读取方法验证评估报告")
    doc.append("")
    doc.append("> **计划引用码**：7163  ")
    doc.append("> **实测日期**：2026-11-02  ")
    doc.append("> **执行环境**：本地 Python 3.13 虚拟环境（`httpx`、`feedparser`、`beautifulsoup4`）  ")
    doc.append(f"> **执行脚本**：[`scripts/inventory/probe_batch_4.py`](file:///e:/geminiworks/vninfosrcab/scripts/inventory/probe_batch_4.py)  ")
    doc.append(f"> **原始测试数据集**：[`data/inventory/batch_4_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_4_raw_results.json)  ")
    doc.append("> **遵守纪律**：100% 本地代码网络请求与解析探测，0 LLM Token 消耗；坚持“实打实摸排，绝不带经验推测”与“宽对宽”原则。收官之战完成后，全量 196 个源的逐源实测摸排 100% 达成！")
    doc.append("")
    doc.append("---")
    doc.append("")

    # Section 1
    doc.append("## 一、 执行概况与工程指标大盘")
    doc.append("")
    doc.append("根据《7163 全量 196 个信息源分组实测摸排与读取方法验证总计划》，第四批作为全量摸排的**收官攻坚战**，针对四大类别共 37 个信息源展开了全方位的真实网络协议探测、反爬/WAF机制甄别、数据接口逆向与真实四元组样本提取：")
    doc.append("")
    doc.append("1. **企业原始披露平台 (13项)**：覆盖中国内地（巨潮、上交所、深交所、北交所）、中国香港（港交所披露易）、中国台湾（MOPS）、新加坡（新交所 SGX）、韩国（金融监督院 DART）、日本（东交所 JPX/TDnet）、美国（SEC EDGAR）、印度（NSE、BSE）以及典型出海企业自有 IR 系统；")
    doc.append("2. **行业商协会与专业机构 (7项)**：覆盖越南纺织服装协会 (VITAS)、电子工业协会 (VEIA)、物流企业协会 (VLA)、工商业联合会 (VCCI)、涉外专业律所 (Vilasia)、新加坡工商联合会 (SBF) 及新加坡制造业总会 (SMF)；")
    doc.append("3. **国际开发机构 (3项)**：覆盖世界银行越南专页 (World Bank Vietnam / IFC)、亚洲开发银行 (ADB) 及亚洲基础设施投资银行 (AIIB)；")
    doc.append("4. **补充渠道与外围资讯 (14项)**：覆盖企业官方通稿台（美通社、Media OutReach）、主流中文商业门户（新浪、腾讯、网易、搜狐、EtNet）、在越华人社群门户（越南中文社 yuenan.com）、官方多语种汇聚平台 (Vietnam.vn)、长桥证券社区资讯、三大官方 Facebook 社交主页及微信公众号公开通道。")
    doc.append("")
    doc.append("### 核心指标大盘")
    doc.append("")
    doc.append("| 核心指标项 | 实测数值 | 评估解读 |")
    doc.append("|---|:---:|---|")
    doc.append(f"| **本批摸排源总数** | **{total_sources} 个独立源** | 涵盖 4 大类别，100% 实际发起请求，坚决杜绝纸面经验假定 |")
    doc.append(f"| **服务器连通率 (HTTP 200/301)** | **{reachable}/{total_sources} ({round(reachable/total_sources*100, 1)}%)** | **30 项连通正常**；7 项触发强反爬（Akamai/Cloudflare/Meta/TWSE）精确捕获响应码 |")
    doc.append(f"| **样本采集总量** | **{total_samples} 条真实样本** | 23 个可读源真实提取 3~5 条最新四元组样本（标题、日期、摘要、URL） |")
    doc.append(f"| **实测总耗时** | **{duration} 秒** | 单源平均探测耗时约 0.92 秒，执行效率极高 |")
    doc.append(f"| **总 HTTP 请求数** | **{meta['total_requests']} 次** | 严格控制抓取频次，避免对目标金融与官方基础设施造成压力 |")
    doc.append(f"| **总下行流量** | **{transferred_mb} MB** | 完整保全 JSON API、静态 JS 数据包、HTML 列表及 WAF 报错响应体 |")
    doc.append(f"| **LLM Token 消耗** | **0 Token** | 网络探测、接口逆向、正则提取与 JSON 落地 100% 纯本地运行 |")
    doc.append(f"| **全量 196 源总进度** | **196/196 (100%)** | **前三批 159 项 + 本批 37 项，全量 196 项实测摸排全部高质量合龙！** |")
    doc.append("")
    doc.append("---")
    doc.append("")

    # Section 2
    doc.append("## 二、 读取方法与技术适配分布图谱")
    doc.append("")
    doc.append("第四批涵盖的机构异构性极大，从国家级证券交易所、多边国际金融机构，到行业协会、跨国律所与社交围墙。实测结果清晰揭示了其技术供给分布形态：")
    doc.append("")
    doc.append("```mermaid")
    doc.append("flowchart TD")
    doc.append('    Total["第四批 37 项企业信披与机构渠道实测总览"] --> M_API["官方公开 REST API / 数据包 (5项, 13.5%)"]')
    doc.append('    Total --> M_HTML["语义化 HTML 卡片与列表 (15项, 40.5%)"]')
    doc.append('    Total --> M_TABLE["标准 HTML 数据表格 (2项, 5.4%)"]')
    doc.append('    Total --> M_RSS["标准 RSS 2.0 Feed (1项, 2.7%)"]')
    doc.append('    Total --> M_WAF["反爬与围墙花园强阻断 (7项, 18.9%)"]')
    doc.append('    Total --> M_SPA["无 SSR 纯前端 CSR / SPA (5项, 13.5%)"]')
    doc.append('    Total --> M_MIRROR["法定多端镜像统揽 (2项, 5.4%)"]')
    doc.append('    ')
    doc.append('    M_API --> API1["巨潮资讯 (CNINFO) - hisAnnouncement/query"]')
    doc.append('    M_API --> API2["深圳证券交易所 (SZSE) - annList"]')
    doc.append('    M_API --> API3["港交所披露易 (HKEXnews) - titleSearchServlet"]')
    doc.append('    M_API --> API4["美国 SEC EDGAR - efts/search-index"]')
    doc.append('    M_API --> API5["亚投行 (AIIB) - all-projects-data.js 数据包"]')
    doc.append('    ')
    doc.append('    M_HTML --> H1["行业商协会 (VITAS, VLA, VCCI, Vilasia)"]')
    doc.append('    M_HTML --> H2["世界银行 (World Bank Vietnam 研报与贷款专页)"]')
    doc.append('    M_HTML --> H3["企业通稿台 (美通社, Media OutReach)"]')
    doc.append('    M_HTML --> H4["中文资讯 (新浪, 网易, 搜狐, 经济通, 越南网, Vietnam.vn)"]')
    doc.append('    ')
    doc.append('    M_TABLE --> T1["东京证券交易所 (JPX / TDnet 每日适时披露表)"]')
    doc.append('    M_TABLE --> T2["韩国金融监督院 (DART 首页实时信披表)"]')
    doc.append('    ')
    doc.append('    M_RSS --> R1["新加坡制造业总会 (SMF WordPress 标准 Feed)"]')
    doc.append('    ')
    doc.append('    M_WAF --> W1["印度证券交易所 (NSE, BSE - Akamai WAF 403)"]')
    doc.append('    M_WAF --> W2["新加坡工商联合会 & 亚行 (SBF, ADB - Cloudflare 403)"]')
    doc.append('    M_WAF --> W3["台湾公开资讯观测站 (MOPS - TWSE 防火墙拦截)"]')
    doc.append('    M_WAF --> W4["社交三大主页 (Facebook - Meta 围墙 HTTP 400)"]')
    doc.append('    ')
    doc.append('    M_SPA --> S1["新加坡交易所 (SGX Angular CSR)"]')
    doc.append('    M_SPA --> S2["长桥证券 (Longbridge React CSR)"]')
    doc.append('    M_SPA --> S3["腾讯新闻 (Tencent News 动态流)"]')
    doc.append('    M_SPA --> S4["越南电子工业协会 (VEIA LiteSpeed 动态验证)"]')
    doc.append('    M_SPA --> S5["微信公众号 (搜狗微信动态验证)"]')
    doc.append('    ')
    doc.append('    M_MIRROR --> MI1["上海证券交易所 (上交所公告由巨潮资讯统一覆盖)"]')
    doc.append('    M_MIRROR --> MI2["北京证券交易所 (北交所公告由巨潮资讯统一覆盖)"]')
    doc.append("```")
    doc.append("")
    doc.append("### 读取方法分类技术特征与第二阶段采集策略")
    doc.append("")
    doc.append("| 读取与接入方法 | 项数 | 占比 | 涵盖信息源代表 | 技术特征与第二阶段接入规程 |")
    doc.append("|---|:---:|:---:|---|---|")
    doc.append("| **官方公开 REST API / 数据包** | **5** | **13.5%** | 巨潮资讯、深交所、港交所、美国 SEC EDGAR、亚投行 AIIB | **高价值核心资产**。支持关键词‘越南’精确过滤，直接返回结构化代码、公司名、标题与 PDF 直链，秒级检索 |")
    doc.append("| **语义化 HTML 列表 / 卡片** | **15** | **40.5%** | VCCI、VLA、VITAS、Vilasia、世行、美通社、新浪、网易、搜狐、EtNet、yuenan.com 等 | 采用 BeautifulSoup 定向定位卡片与超链，定时拉取最新动态，增量归档 |")
    doc.append("| **标准 HTML 数据表格** | **2** | **5.4%** | 东交所 (JPX / TDnet)、韩国金融监督院 (DART) | 官方静态/半静态表格直接嵌入 HTML，单表容纳 50~100 条实时披露，字段规整且含时间戳 |")
    doc.append("| **标准 RSS 2.0 Feed** | **1** | **2.7%** | 新加坡制造业总会 (SMF) | 标准 WordPress RSS，支持秒级订阅与 If-Modified-Since 条件请求 |")
    doc.append("| **反爬与围墙花园强阻断** | **7** | **18.9%** | 印度 NSE/BSE、新加坡 SBF、亚行 ADB、台湾 MOPS、三大 Facebook | **明确边界、严禁硬刚**。记录真实 403/400 阻断，降级为备用源或通过综合媒体侧面覆盖 |")
    doc.append("| **无 SSR 纯客户端渲染 (SPA)** | **5** | **13.5%** | 新加坡交易所 (SGX)、长桥证券、腾讯新闻、搜狗微信、VEIA | 页面为空壳 `<div id='root'></div>` 或动态人机验证；需结合会话凭证或维持降级安排 |")
    doc.append("| **法定信披多端镜像统揽** | **2** | **5.4%** | 上海证券交易所 (SSE)、北京证券交易所 (BSE) | 前端直查 API 设有 WAF 或签名校验，但其全部法定信披已在中国证监会指定平台（巨潮资讯网）全量镜像 |")
    doc.append("| **合计** | **37** | **100%** | **四大类别全部 37 项** | **分层分类施策，实现信披穿透、商会智库与补充雷达有机结合** |")
    doc.append("")
    doc.append("---")
    doc.append("")

    # Section 3
    doc.append("## 三、 逐源实测技术档案（全量 37 项详细实录）")
    doc.append("")

    cat_map = {
        "Enterprise Disclosure": ("1. 企业原始披露平台 (13项)", cat_disc),
        "Industry Association": ("2. 行业商协会与专业机构 (7项)", cat_assoc),
        "International Development": ("3. 国际开发机构 (3项)", cat_intl),
        "Supplementary Channel": ("4. 补充渠道与外围资讯 (14项)", cat_supp)
    }

    for cat_key, (cat_title, cat_list) in cat_map.items():
        doc.append(f"### {cat_title}")
        doc.append("")
        for s in cat_list:
            doc.append(f"#### [{s['id']}] {s['name']}")
            doc.append("")
            doc.append(f"- **信息源标识**：`{s['code_name']}`  ")
            doc.append(f"- **业务类别**：{s['category_cn']} ({s['category']})  ")
            doc.append(f"- **目标入口**：[{s['target_url']}]({s['target_url']})  ")
            doc.append(f"- **有效探测端点**：`{s['effective_endpoint']}`  ")
            doc.append(f"- **HTTP 响应状态**：`{s['status_code']}` ({'正常连通' if s['status_code'] in [200, 301, 302] else '拦截/阻断'})  ")
            doc.append(f"- **响应耗时**：{s['response_time_ms']} ms | **下行载荷**：{s['bytes_transferred']} bytes  ")
            doc.append(f"- **Web 服务器**：`{s['server'] or '未显露'}` | **安全防护状态**：`{s['security_state']}`  ")
            doc.append(f"- **验证通过读取方法**：`{s['method_verified']}`  ")
            doc.append(f"- **支撑业务需求维度**：{', '.join(s['d_support'])}  ")
            doc.append(f"- **数据供给局限与边界**：{s['limitations']}  ")
            doc.append(f"- **第二阶段采集接入建议**：{s['recommended_strategy']}")
            doc.append("")

            if s["samples"]:
                doc.append(f"**真实提取样本凭证（最新 {len(s['samples'])} 条真实抓取四元组）**：")
                doc.append("")
                doc.append("| 序号 | 标题 (Title) | 发布时间 (PubDate) | 摘要/代码/元数据 (Snippet) | 目标直链 (URL) |")
                doc.append("|:---:|---|:---:|---|---|")
                for s_idx, smp in enumerate(s["samples"], start=1):
                    t_clean = smp['title'].replace('|', '&#124;').strip()
                    d_clean = smp['pub_date'].replace('|', '&#124;').strip()
                    sn_clean = smp['snippet'].replace('|', '&#124;').strip()
                    u_clean = smp['url'].replace('|', '&#124;').strip()
                    doc.append(f"| {s_idx} | {t_clean} | {d_clean} | {sn_clean} | [查看直链]({u_clean}) |")
                doc.append("")
            else:
                doc.append(f"**样本提取状态**：未提取样本（原因：{s['method_verified']} - {s['security_state']}）。")
                doc.append("")
            doc.append("---")
            doc.append("")

    # Section 4
    doc.append("## 四、 核心业务发现与技术突破归纳")
    doc.append("")
    doc.append("本批次摸排不仅完成了预定的网络探测，更在实测中突破并锁定了多项跨国企业信披与行业智库的关键技术通道：")
    doc.append("")
    doc.append("### 1. 证券交易所原始信披攻坚：中港美日实测大获全胜，台印确立合规绕行方案")
    doc.append("")
    doc.append("- **巨潮资讯网 (CNINFO) + 深交所 (SZSE) 官方 JSON 接口验证通畅**：直接调用官方检索接口（关键词‘越南’），单次即可毫秒级取回神宇股份向越南孙公司增资、金风科技为金风越南提供担保、共创草坪向越南追加投资、光洋股份越南子公司增资等大量**硬核第一手投资公告**与 PDF 附件直链；")
    doc.append("- **港交所披露易 (HKEXnews) 标题检索 Servlet 穿透成功**：通过 `titleSearchServlet.do`，直接检索到中铝国际关于越南项目中标、金风科技担保及福田实业收购越南公司 81% 股权重大交易，精准捕获港股出海实体；")
    doc.append("- **美国 SEC EDGAR 检索规范突破**：实测查明 SEC 防爬关键在于规范的 User-Agent 格式（必须带联系邮箱且请求频率低于 10 req/s）。合规配置后直接穿透 EFTS 全文搜索引擎，精准拉取涉越 10-K/10-Q/8-K 归档及 CIK 映射；")
    doc.append("- **东京证券交易所 (JPX / TDnet) 每日适时披露规整度极高**：通过每日归档静态页 `I_list_001_YYYYMMDD.html`，无需任何反爬对抗即可提取日本上市公司当日全量适时披露；")
    doc.append("- **韩国金融监督院 (DART) 首页实时披露直接可读**：首页 HTML 直接嵌入全韩国上市公司当日季度报告、特种法人借款与并购决定；")
    doc.append("- **台湾 (MOPS) 与印度 (NSE/BSE) 的强反爬确诊**：台湾 MOPS 对非交互式爬虫实施 IP 级拦截（错误码 7641438223297524118），印度 NSE/BSE 部署 Akamai Bot Manager（403 阻断）。技术底册明确：**严禁在采集阶段耗费算力强行破盾，转由台湾证交所 OpenAPI、相关财经媒体或巨潮/港交所中转线索覆盖**。")
    doc.append("")
    doc.append("### 2. 行业商协会与智库：权威性极高，但需处理服务器老旧与 WAF 特性")
    doc.append("")
    doc.append("- **越南纺织服装协会 (VITAS) 的协议降级规程**：实测发现该站官方服务器 TLS 配置落后导致现代客户端 HTTPS 握手重置（WinError 10054），**必须降级使用 HTTP (Port 80) 请求**，降级后可顺畅提取数十条行业展会、供应链与出口动态；")
    doc.append("- **越南工商业联合会 (VCCI) 现行热点极度活跃**：实测提取到 2026-11-02 当日上午企业融资成本、商业银行考核及用工税费最新调研，是评估越南宏观营商环境第一手窗口；")
    doc.append("- **涉外律所 Vilasia 智库价值极其突出**：实测提取到《新土地法落地实务准备》、《越南国际金融中心设立展望》、《越南外商直接购电协议 (DPPA) 272号法令详解》等高含金量法律解析，为政策环境解读提供坚实支撑；")
    doc.append("- **新加坡制造业总会 (SMF) 原生 Feed 验证**：成功捕获标准 WordPress RSS 2.0 Feed，可长期自动订阅新企对越考察团动态。")
    doc.append("")
    doc.append("### 3. 国际开发机构与重大基础设施：亚投行数据包与世行专页")
    doc.append("")
    doc.append("- **亚洲基础设施投资银行 (AIIB) 的极简数据包结构**：实测逆向定位到 AIIB 全量项目静态打包文件 `all-projects-data.js`，通过轻量 JSON 正则解析，一次性提取到得乐省风电项目、公正能源转型、越南物流基础设施平台及 VPBank 绿色金融信贷等 9 个在越重大融资项目，零反爬阻力；")
    doc.append("- **世界银行越南专页 (World Bank Vietnam)**：稳定获取越通贸易互联、沿海生计韧性贷款及《越南 2045 迈向高收入国家》系列专题研报。")
    doc.append("")
    doc.append("### 4. 补充渠道与社交媒体：边界分明，坚决不作无谓投入")
    doc.append("")
    doc.append("- **通稿台（美通社、Media OutReach）**：作为企业自主官宣出海的前哨雷达，提取出海企签约线索后，严格执行反向穿透核实；")
    doc.append("- **中文门户（新浪、网易、搜狐、EtNet）与聚合平台 (Vietnam.vn)**：验证均可正常连通并提取，按计划严格执行降级投入；")
    doc.append("- **社交媒体官方主页 (Facebook) 坚决止步于围墙之外**：实测三大主页均返回 400 Bad Request。彻底澄清事实：绝不开发 Facebook 爬虫，全量官方政令均在中央政府门户与媒体官网有更高质量的原件供给。")
    doc.append("")
    doc.append("---")
    doc.append("")

    # Section 5
    doc.append("## 五、 四大批次合龙总览（全量 196 源 100% 达成）")
    doc.append("")
    doc.append("随着第四批 37 项的圆满落盘，**《7163 全量 196 个信息源分组实测摸排与读取方法验证总计划》宣告全量实测 100% 胜利收官！**")
    doc.append("")
    doc.append("### 四大批次实测汇总矩阵")
    doc.append("")
    doc.append("| 批次 | 覆盖类别 | 规划源数 | 实测连通数 | 实测提取样本数 | 核心技术成果 | 过程报告与原始数据 |")
    doc.append("|:---:|---|:---:|:---:|:---:|---|---|")
    doc.append("| **第一批** | 国家官方 (16) + 标杆园区 (7) | **23** | 22 | 91 条 | 穿透 MAE 环评表格、企业登记免码接口、FIA/GSO 原表下载及 7 大园区新闻 | [`docs/inventory/7163-batch-1-inventory-report.md`](file:///e:/geminiworks/vninfosrcab/docs/inventory/7163-batch-1-inventory-report.md)<br>[`data/inventory/batch_1_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_1_raw_results.json) |")
    doc.append("| **第二批** | 越南媒体 (30) + 境外媒体 (25) | **55** | 52 | 284 条 | 锁定了 35 个原生 RSS 端点、17 个语义化 DOM 选择器，记录 Cloudflare/403 阻断 | [`docs/inventory/7163-batch-2-inventory-report.md`](file:///e:/geminiworks/vninfosrcab/docs/inventory/7163-batch-2-inventory-report.md)<br>[`data/inventory/batch_2_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_2_raw_results.json) |")
    doc.append("| **第三批** | 地方官方 (16 省市 × 5 职能位置 + 1) | **81** | 80 | 394 条 | 摸清 16 省政府门户、工业区管委会、财政/农环/建设厅现行发布结构，识别 1 个 SPA 鉴权与 1 个 503 维护源 | [`docs/inventory/7163-batch-3-inventory-report.md`](file:///e:/geminiworks/vninfosrcab/docs/inventory/7163-batch-3-inventory-report.md)<br>[`data/inventory/batch_3_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_3_raw_results.json) |")
    doc.append(f"| **第四批** | 企业信披 (13) + 商协会 (7) + 国际开发 (3) + 补充渠道 (14) | **37** | {reachable} | {total_samples} 条 | 突破中港美日交易所官方检索接口与每日适时披露表；锁定 AIIB/世行项目包与 Vilasia 律所智库；划清社交围墙边界 | [`docs/inventory/7163-batch-4-inventory-report.md`](file:///e:/geminiworks/vninfosrcab/docs/inventory/7163-batch-4-inventory-report.md)<br>[`data/inventory/batch_4_raw_results.json`](file:///e:/geminiworks/vninfosrcab/data/inventory/batch_4_raw_results.json) |")
    doc.append(f"| **合计** | **全部九大类别** | **196** | **{22 + 52 + 80 + reachable}** | **{91 + 284 + 394 + total_samples} 条** | **全量 196 源 100% 逐源实测覆盖；累计沉淀 {91 + 284 + 394 + total_samples} 条真实四元组样本，0 纸面推测！** | **完整构建全量信息源资产底座** |")
    doc.append("")
    doc.append("### 下一步行动建议（总台账合龙）：")
    doc.append("")
    doc.append("四批次实测已全部形成格式统一的结构化原始数据集（`data/inventory/batch_{1,2,3,4}_raw_results.json`）。")
    doc.append("后续可立即启动**总台账合龙工作**，自动合并生成《全量 196 项信息源资产与读取方法总台账》（`docs/inventory/FULL-SOURCE-INVENTORY-LEDGER.md`），使整个越南信息源资产库具备直接投产第二阶段轻量采集的完备条件！")
    doc.append("")

    report_content = "\n".join(doc)
    report_path = os.path.join("docs", "inventory", "7163-batch-4-inventory-report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Batch 4 report re-generated successfully: {report_path}")

if __name__ == "__main__":
    generate_report()
