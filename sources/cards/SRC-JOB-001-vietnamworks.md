---
source_id: SRC-JOB-001
name: VietnamWorks 越南高端招聘雷达
cluster: job_radar
target_url: https://www.vietnamworks.com/tim-viec-lam
archetype_skill: job-radar-scanner
protocol_driver: html_card_driver
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

search_spec:
  endpoint_template: "https://www.vietnamworks.com/tim-viec-lam?q={keyword}&order=created_at_desc"
  keywords:
    - "Factory Setup"
    - "Thanh lap nha may"
    - "Plant Manager"
    - "Site Selection"
    - "EHS Director"

attachment_probe: false
---

# 信源作业指导卡：VietnamWorks 越南高端招聘雷达 (SRC-JOB-001)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南本土最大的白领与高阶工业技术人才招聘门户（Next.js 架构，含 `__NEXT_DATA__` 预渲染 JSON）。
* **情报定位**：**全网最前瞻的早期投资信号雷达**。跨国企业在正式签约落地、媒体公开报道前 3~6 个月，必然提前在越南招聘核心前站团队（选址经理、厂长、EHS总监）。
* **价值等级**：P0 级核心前瞻雷达。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www.vietnamworks.com/tim-viec-lam`
* **底层驱动与容器描述**：
  * **驱动类型**：`html_card_driver`（优先从页面 `<script id="__NEXT_DATA__">` JSON 树中提取职位数组，避免脆弱 CSS DOM 解析）。
  * **参数化遍历方式**：驱动轮流将 `search_spec.keywords` 填入 `endpoint_template` 并发起 GET 请求（只读第 1 页按发布时间降序前 20 条，涵盖近 72 小时新岗）。
  * **核心提取节点**：从 `__NEXT_DATA__.props.pageProps.jobs` 提取 `jobTitle`, `companyName`, `workLocation`, `publishedOn`, `jobUrl`。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
`job-radar-scanner` 对拉取的岗位列表进行语义评估，满足以下特征即纳入候选：
* **必须收录的特征**：
  * 职位标题或职责中明确提及：“New manufacturing plant”、“Greenfield project”、“Start-up factory”、“位于 XX 工业区（KCN）”；
  * 招聘主体为跨国工业制造实体（中资、台资、日韩、欧美制造大厂在越子公司）。
* **关键产业聚焦**：半导体封测、高阶液冷散热、动力电池与储能、新能源车零部件、高标冷链仓储。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-JOB-001",
  "title": "Plant Manager (New Factory Setup - Bac Ninh)",
  "pub_date_raw": "2026-11-10",
  "subject_entity": "立讯精密 / Luxshare-ICT (Vietnam) Co., Ltd.",
  "geo_location": "Bắc Ninh (北宁省) / VSIP Bac Ninh",
  "signal_type": "factory_setup",
  "project_scale": null,
  "evidence_snippet": "Responsible for setting up new production facility of 50,000 sqm in VSIP Bac Ninh from scratch.",
  "direct_url": "https://www.vietnamworks.com/job/plant-manager-new-factory-setup-123456",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 第三方猎头中介代招且对企业、园区完全脱敏的匿名职位；
* 已成熟投产多年的老厂替换性普工、产线操作工、行政前台招聘；
* 纯消费零售、贸易餐饮、软件外包 IT 岗位。

## 6. 异常与改版判定 (Health & Failure Detection)
* 页面无法定位 `<script id="__NEXT_DATA__">` 节点或返回空数组；
* 出现 Cloudflare 人机拦截页面或连续 2 次返回 HTTP 403 / 503。
