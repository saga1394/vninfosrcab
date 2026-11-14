---
source_id: SRC-APP-002
name: VBPL 越南国家法律法规数据库 (XML Sitemap 增量流)
cluster: legal_approval
target_url: https://vbpl.vn/sitemap/1.xml
archetype_skill: gazette-table-parser
protocol_driver: sitemap_driver
check_frequency: daily
priority: P1
expected_column: macro_policy
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

attachment_probe: false
---

# 信源作业指导卡：VBPL 越南国家法律法规数据库 (SRC-APP-002)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南司法部主管国家级法律法规效力数据库。
* **情报定位**：通过 XML Sitemap 毫秒级增量流监控最新生效的投资法、土地法、电力法及地方工业区配套法规（补丁 2 Sitemap 边缘源示范卡）。
* **价值等级**：P1 级法理效力校验主轴源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://vbpl.vn/sitemap/1.xml`
* **底层驱动与容器描述**：`sitemap_driver` 解析标准 Sitemap XML `<url><loc>` 与 `<lastmod>`，筛选近 72 小时更新法规。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 关注工业投资、外汇管理、电力交易、工业用地租赁及税务抵免相关法律/议定/通告。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-APP-002",
  "title": "Nghị định sửa đổi quy định về quản lý khu công nghiệp và khu kinh tế",
  "pub_date_raw": "2026-11-11",
  "subject_entity": "Bộ Tư pháp / VBPL (越南国家法律法规库)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "Sitemap incremental entry (2026-11-11): Nghị định sửa đổi quy định về quản lý khu công nghiệp.",
  "direct_url": "https://vbpl.vn/van-ban/chi-tiet/nghi-dinh-kcn-2026",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 交通违章罚款标准、婚姻家庭、民事继承及纯校园教师职称规定。

## 6. 异常与改版判定 (Health & Failure Detection)
* XML 解析异常、HTTP 404/500 或连续 2 次返回空列表。
