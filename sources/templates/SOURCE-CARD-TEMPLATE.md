---
source_id: SRC-XXX-000           # 格式: SRC-[JOB|IP|APP|SEC|MED]-[三位序号]
name: 机构或媒体标准官方名称
cluster: job_radar               # 枚举: job_radar | industrial_park | legal_approval | corporate_disclosure | media_fdi
target_url: https://example.com/target-section
archetype_skill: job-radar-scanner # 上层业务技能: job-radar-scanner | park-news-inspector | gazette-table-parser | disclosure-sniffer | media-stream-curator
protocol_driver: html_card_driver  # 底层协议驱动: rss_driver | html_card_driver | html_table_driver | rest_api_driver | sitemap_driver
check_frequency: daily           # 枚举: daily | weekly | monthly
priority: P1                     # 枚举: P0 | P1 | P2
expected_column: fdi             # 枚举: fdi | industrial_park | industry_focus | legal_approval | macro_policy
status: active                   # 枚举(严格小写): active | degraded | low_freq | retired
last_audit_date: "2026-11-12"

# 【必选】底层网络握手参数配置
network_config:
  verify_ssl: true               # 政务证书过期站点(如部分越南部委)必须置为 false
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 【可选】带参搜索模板 (适用于招聘、交易所检索类信源，严禁写模糊人类操作动作)
search_spec:
  endpoint_template: "https://example.com/search?q={keyword}&sort=date"
  keywords:
    - "Keyword 1"
    - "Keyword 2"

# 【可选】REST API / SPA 接口参数配置 (适用于 rest_api_driver)
# api_spec:
#   method: POST
#   headers:
#     Content-Type: "application/json"
#   payload_template:
#     page: 1
#     size: 20
#   json_path: "data.items"

# 【可选】是否自动探测并抽取列表页内嵌的 PDF 公报附件文本 (适用于统计局/外资局公报)
attachment_probe: false
---

# 信源作业指导卡：{{name}} ({{source_id}})

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：[政府部委 / 工业区管委会 / 标杆地产开发商 / 招聘平台 / 证券交易所 / 垂直财经媒体]
* **情报定位**：[说明本源在越南产业情报链条中处于哪一个环节，提供什么性质的线索]
* **价值等级**：[P0 核心前瞻 / P1 一线承载 / P2 辅助印证]

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`{{target_url}}`
* **底层驱动与容器描述**：
  * **驱动类型**：`{{protocol_driver}}`
  * **列表/数据定位特征**：[清晰说明 HTML 标签结构、表格 `<tr>` 列顺序、XML `<loc>` 节点或 JSON 字段映射路径]
  * **日期与链接定位**：[说明日期字段格式如 `dd/mm/yyyy` 及详情页链接拼接规则]

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
业务认知技能（`{{archetype_skill}}`）扫描本源提取的原始列表时，重点识别并纳入具备以下特征的动态：
* **必须收录的核心触发词/动向**：
  * 关键词组 A（动作）：[如：Lễ khởi công (奠基), Bàn giao đất (供地), Factory Setup (新厂筹建)]
  * 关键词组 B（主体）：[如：Dự án FDI (外资项目), Doanh nghiệp (企业), Nhà đầu tư (投资者)]
* **核心业务特征**：[例如：提及具体投资金额、用地面积、开工日期、产品线产能]

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
巡检驱动与认知层提取必须严格对齐 `sources/interfaces/contracts.py` 中的 `RawExtractedItem` 数据类（运行态的 `candidate_id` 与 `extracted_at` 由调度框架统一生成注入）：
```json
{
  "source_id": "{{source_id}}",
  "title": "原始外文标题或职位名",
  "pub_date_raw": "源头显示的原始时间文本",
  "subject_entity": "涉案企业/投资主体名称（原文 + 规范中文名）",
  "geo_location": "涉及的省份 / 工业园区全称",
  "signal_type": "factory_setup",
  "project_scale": "投资额（万美元）或用地面积（公顷），无则填 null",
  "evidence_snippet": "佐证该动向的一两句核心外文原文摘录",
  "direct_url": "直达该动态或职位的真实 URL（必须 200 可访问）",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
遇到以下情形，坚决跳过并丢弃，不予采录：
* **噪音类别 1**：[如：非涉企的民生社会新闻、普通技工日常流转招聘]
* **噪音类别 2**：[如：超过 72 小时的历史陈旧归档或无日期常青页面]

## 6. 异常与改版判定 (Health & Failure Detection)
出现以下特征时，自动递增 `source_health` 表的 `consecutive_failures` 计数，连续 2 次触发即自动降级为 `degraded`：
* **页面 404 / 500 / 网络超时**；
* **结构解析为空**：页面 HTTP 200 但解析返回 0 条记录且不符合预期（疑似网站改版）；
* **WAF 阻断**：返回 403 / 429 或检测到 Cloudflare 拦截特征。
