---
source_id: SRC-DISC-10
name: "美国证券交易委员会 EDGAR (SEC EDGAR)"
cluster: corporate_disclosure
target_url: "https://efts.sec.gov/LATEST/search-index?q=Vietnam"
archetype_skill: disclosure-sniffer
protocol_driver: rest_api_driver
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: true
  timeout: 20
  headers:
    User-Agent: "VnInvestmentResearch AdminContact@vnresearch.org"
    Accept: "application/json"

api_spec:
  method: GET
  json_path: "hits.hits"
  title_template: "[{form}] {display_names}"
  detail_url_template: "https://www.sec.gov/edgar/browse/?CIK={ciks}"
  date_field: "file_date"

attachment_probe: false
---
# 信源作业指导卡：美国证券交易委员会 EDGAR (SEC EDGAR) (SRC-DISC-10)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 4 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：企业原始披露
* **价值等级**：P0（预期归仓 `fdi`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://efts.sec.gov/LATEST/search-index?q=Vietnam`
* **底层驱动**：`rest_api_driver`（实测通道：`REST API (EFTS Search Index)`）
* **技术备注**：Compliant Header Required (HTTP 200)

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `disclosure-sniffer` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-DISC-10",
  "title": "[497K] VanEck ETF Trust  (CIK 0001137360): Filing referencing Vietnam",
  "pub_date_raw": "2022-12-09",
  "subject_entity": "美国证券交易委员会 EDGAR (SEC EDGAR)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "capital_increase",
  "project_scale": null,
  "evidence_snippet": "[497K] VanEck ETF Trust  (CIK 0001137360): Filing referencing Vietnam",
  "direct_url": "https://www.sec.gov/Archives/edgar/data/0001137360/000113736022001187/",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
