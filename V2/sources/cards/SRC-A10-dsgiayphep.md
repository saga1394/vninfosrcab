---
source_id: SRC-A10
name: "Tham vấn Giấy phép môi trường (Environmental Permit Application - MAE)"
cluster: legal_approval
target_url: "https://thamvan.mae.gov.vn/Home/DSGiayPhep"
archetype_skill: gazette-table-parser
protocol_driver: html_table_driver
check_frequency: daily
priority: P0
expected_column: legal_approval
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: false
  timeout: 20
  resolve_ip: "103.9.85.148"
  use_curl: true
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: true
---
# 信源作业指导卡：Tham vấn Giấy phép môi trường (Environmental Permit Application - MAE) (SRC-A10)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 1 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：National Official
* **价值等级**：P0（预期归仓 `legal_approval`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://thamvan.mae.gov.vn/Home/DSGiayPhep`
* **底层驱动**：`html_table_driver`（实测通道：`Structured HTML Table (SChannel fallback)`）
* **技术备注**：Standard 11-row HTML table. Contains industrial manufacturing permits with location, owner, and consultation period.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `gazette-table-parser` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-A10",
  "title": "Nhà máy sản xuất thép thành phẩm",
  "pub_date_raw": "2026-11-12",
  "subject_entity": "Tham vấn Giấy phép môi trường (Environmental Permit Application - MAE)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "eia_approval",
  "project_scale": null,
  "evidence_snippet": "Nhà máy sản xuất thép thành phẩm",
  "direct_url": "https://thamvan.mae.gov.vn/XemChiTiet/XemChiTietDuAn?id=6417",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
