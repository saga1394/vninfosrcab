---
source_id: VN-LOC-12-NA-B
name: "Ban Quản lý Khu kinh tế Đông Nam Nghệ An"
cluster: industrial_park
target_url: "https://dongnam.nghean.gov.vn"
archetype_skill: park-news-inspector
protocol_driver: html_card_driver
check_frequency: daily
priority: P1
expected_column: industrial_park
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: false
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：Ban Quản lý Khu kinh tế Đông Nam Nghệ An (VN-LOC-12-NA-B)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 3 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：B
* **价值等级**：P1（预期归仓 `industrial_park`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://dongnam.nghean.gov.vn`
* **底层驱动**：`html_card_driver`（实测通道：`HTML Card / Semantic List`）
* **技术备注**：Thành công trích xuất dữ liệu danh mục công khai.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `park-news-inspector` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "VN-LOC-12-NA-B",
  "title": "Ban Quản lý KKT Đông Nam Nghệ An tổ chức tập huấn về khu công nghiệp sinh thái, doanh nghiệp sinh",
  "pub_date_raw": "3/7/2026",
  "subject_entity": "Ban Quản lý Khu kinh tế Đông Nam Nghệ An",
  "geo_location": "义安",
  "signal_type": "land_grant",
  "project_scale": null,
  "evidence_snippet": "Ban Quản lý KKT Đông Nam Nghệ An tổ chức tập huấn về khu công nghiệp sinh thái, doanh nghiệp sinh",
  "direct_url": "https://dongnam.nghean.gov.vn/tin-tuc--su-kien/ban-quan-ly-kkt-dong-nam-nghe-an-to-chuc-tap-huan-ve-khu-cong-nghiep-sinh-thai-doanh-nghiep-sinh-thai-va-cong-vu-quan-ly-iso-14001-2026-cho-cac-doanh-nghiep-trong-kkt-kcn-tinh-nghe-an-1075951",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
