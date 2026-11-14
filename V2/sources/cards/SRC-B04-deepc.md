---
source_id: SRC-B04
name: "DEEP C Industrial Zones"
cluster: industrial_park
target_url: "https://deepc.vn/vi/blog/category/tin-tuc/"
archetype_skill: park-news-inspector
protocol_driver: html_card_driver
check_frequency: daily
priority: P1
expected_column: industrial_park
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：DEEP C Industrial Zones (SRC-B04)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 1 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：Benchmark Industrial Parks
* **价值等级**：P1（预期归仓 `industrial_park`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://deepc.vn/vi/blog/category/tin-tuc/`
* **底层驱动**：`html_card_driver`（实测通道：`Lightweight HTML Card Scraping`）
* **技术备注**：Structured blog list on /thong-tin-chuyen-nganh/tin-tuc-su-kien/. Features Haiphong & Quang Ninh customer events, community and park updates.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `park-news-inspector` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-B04",
  "title": "Tiệc Tri ân Khách hàng DEEP C 2026",
  "pub_date_raw": "2026-11-12",
  "subject_entity": "DEEP C Industrial Zones",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "land_grant",
  "project_scale": null,
  "evidence_snippet": "Tiệc Tri ân Khách hàng DEEP C 2026",
  "direct_url": "https://deepc.vn/vi/blog/tiec-tri-an-khach-hang-deep-c-2026/",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
