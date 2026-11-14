---
source_id: SRC-A05
name: "Bộ Xây dựng (Ministry of Construction - MOC)"
cluster: industrial_park
target_url: "https://moc.gov.vn/vn/Pages/Trangchu.aspx"
archetype_skill: park-news-inspector
protocol_driver: html_card_driver
check_frequency: daily
priority: P1
expected_column: industrial_park
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: false
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：Bộ Xây dựng (Ministry of Construction - MOC) (SRC-A05)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 1 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：National Official
* **价值等级**：P1（预期归仓 `industrial_park`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://moc.gov.vn/vn/Pages/Trangchu.aspx`
* **底层驱动**：`html_card_driver`（实测通道：`Lightweight HTML List Scraping`）
* **技术备注**：Provides key real estate project transfer guidelines, urban planning, and construction legal consultations.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `park-news-inspector` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-A05",
  "title": "Đảng ủy Bộ Xây dựng tổ chức Hội nghị quán triệt, triển khai các văn bản mới của Đảng và bồi dưỡng tập huấn nghiệp vụ công tác đảng năm 2026",
  "pub_date_raw": "2026-11-12",
  "subject_entity": "Bộ Xây dựng (Ministry of Construction - MOC)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "land_grant",
  "project_scale": null,
  "evidence_snippet": "Đảng ủy Bộ Xây dựng tổ chức Hội nghị quán triệt, triển khai các văn bản mới của Đảng và bồi dưỡng tập huấn nghiệp vụ công tác đảng năm 2026",
  "direct_url": "http://moc.gov.vn/vn/tin-tuc/1173/97817/dang-uy-bo-xay-dung-to-chuc-hoi-nghi-quan-triet-trien-khai-cac-van-ban-moi-cua-dang-va-boi-duong-tap-huan-nghiep-vu-cong-tac-dang-nam-2026.aspx",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
