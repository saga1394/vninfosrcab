---
source_id: VN-LOC-16-HT-D
name: "Sở Nông nghiệp và Môi trường Hà Tĩnh"
cluster: legal_approval
target_url: "https://sonnmt.hatinh.gov.vn/sotnmt/portal/folder/home"
archetype_skill: gazette-table-parser
protocol_driver: html_card_driver
check_frequency: daily
priority: P1
expected_column: legal_approval
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: false
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：Sở Nông nghiệp và Môi trường Hà Tĩnh (VN-LOC-16-HT-D)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 3 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：D
* **价值等级**：P1（预期归仓 `legal_approval`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://sonnmt.hatinh.gov.vn/sotnmt/portal/folder/home`
* **底层驱动**：`html_card_driver`（实测通道：`HTML Card / Semantic List`）
* **技术备注**：Thành công trích xuất dữ liệu danh mục công khai.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `gazette-table-parser` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "VN-LOC-16-HT-D",
  "title": "Hà Tĩnh hoàn thiện Đề án phát triển nông nghiệp nông thôn, xây dựng nông thôn mới và giảm nghèo bền vững tỉnh Hà Tĩnh giai đoạn 2026-2030",
  "pub_date_raw": "20/10/2026",
  "subject_entity": "Sở Nông nghiệp và Môi trường Hà Tĩnh",
  "geo_location": "河静",
  "signal_type": "eia_approval",
  "project_scale": null,
  "evidence_snippet": "Hà Tĩnh hoàn thiện Đề án phát triển nông nghiệp nông thôn, xây dựng nông thôn mới và giảm nghèo bền vững tỉnh Hà Tĩnh giai đoạn 2026-2030",
  "direct_url": "https://sonnmt.hatinh.gov.vn/sotnmt/portal/read/tin-hoat-dong/news/ha-tinh-hoan-thien-e-an-phat-trien-nong-nghiep-nong-thon-xay-dung-nong-thon-moi-.html",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
