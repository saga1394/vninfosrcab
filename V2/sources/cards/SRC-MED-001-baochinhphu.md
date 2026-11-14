---
source_id: SRC-MED-001
name: Báo Chính phủ 越南政府新闻网经济频道
cluster: media_fdi
target_url: https://baochinhphu.vn/kinh-te.rss
archetype_skill: media-stream-curator
protocol_driver: rss_driver
check_frequency: daily
priority: P0
expected_column: macro_policy
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

attachment_probe: false
---

# 信源作业指导卡：Báo Chính phủ 越南政府新闻网经济频道 (SRC-MED-001)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南政府办公厅官方机关报（国家最高行政机关门户）。
* **情报定位**：总理/副总理签署的涉企决定、税收电价调节、重大基础设施规划与国家级 FDI 动向权威一手流。
* **价值等级**：P0 级政策与宏观主轴源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://baochinhphu.vn/kinh-te.rss`
* **底层驱动与容器描述**：`rss_driver` 秒级解析标准 RSS 2.0 `<item>` 流。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 重点捕获 `Nghị quyết`、`Nghị định`、`Quyết định`、电价、税制、投资法、DPPA、工业区与半导体产业动态。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-MED-001",
  "title": "Chính phủ ban hành cơ chế mua bán điện trực tiếp (DPPA) cho khu công nghiệp",
  "pub_date_raw": "2026-11-11",
  "subject_entity": "Chính phủ Việt Nam (越南政府)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "Nghị định mới mở rộng đối tượng doanh nghiệp sản xuất lớn tại các khu công nghiệp được tham gia cơ chế DPPA.",
  "direct_url": "https://baochinhphu.vn/chinh-phu-ban-hanh-co-che-dppa-102261111.htm",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 文体赛事、自然灾害抢险通报、纯礼仪外交拜会与社会治安新闻。

## 6. 异常与改版判定 (Health & Failure Detection)
* RSS XML 解析失败或连续 2 次 HTTP 404 / 500。
