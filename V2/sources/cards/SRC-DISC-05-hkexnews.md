---
source_id: SRC-DISC-05
name: "港交所披露易 (HKEXnews)"
cluster: corporate_disclosure
target_url: "https://www1.hkexnews.hk/search/titleSearchServlet.do"
archetype_skill: disclosure-sniffer
protocol_driver: rest_api_driver
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: false
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    Referer: "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"

api_spec:
  method: GET
  payload_template: {"sortDir": 0, "sortByOptions": "DateTime", "category": 0, "market": "SEHK", "stockId": -1, "documentType": -1, "fromDate": "{ago_30d_yyyymmdd}", "toDate": "{today_yyyymmdd}", "title": "越南", "searchType": 0, "t1code": -2, "t2Gcode": -2, "t2code": -2, "rowRange": 20, "lang": "ZH"}
  nested_json_field: "result"
  title_template: "[{STOCK_CODE}] {STOCK_NAME}: {TITLE}"
  detail_url_template: "https://www1.hkexnews.hk{FILE_LINK}"
  date_field: "DATE_TIME"

attachment_probe: false
---
# 信源作业指导卡：港交所披露易 (HKEXnews) (SRC-DISC-05)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 4 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：企业原始披露
* **价值等级**：P0（预期归仓 `fdi`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www1.hkexnews.hk/search/titleSearchServlet.do`
* **底层驱动**：`rest_api_driver`（实测通道：`REST API (JSON SearchServlet)`）
* **技术备注**：Open (HTTPS API)

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `disclosure-sniffer` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-DISC-05",
  "title": "[02068] 中鋁國際: 中鋁國際工程股份有限公司關於越南項目中標的公告",
  "pub_date_raw": "26/10/2026",
  "subject_entity": "港交所披露易 (HKEXnews)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "capital_increase",
  "project_scale": null,
  "evidence_snippet": "[02068] 中鋁國際: 中鋁國際工程股份有限公司關於越南項目中標的公告",
  "direct_url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/1026/2026102601093_c.pdf",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
