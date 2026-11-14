---
source_id: SRC-IP-001
name: Becamex IDC 工业地产与招商动态
cluster: industrial_park
target_url: https://becamex.com.vn/tin-tuc/
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
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

attachment_probe: false
---

# 信源作业指导卡：Becamex IDC 工业地产与招商动态 (SRC-IP-001)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南平阳省属超大型综合工业地产开发商。
* **情报定位**：FDI 外资落地物理承载最前线，覆盖平阳、平福、广治辖区工业园供地、开工奠基与签约租赁动态。
* **价值等级**：P1 级一线物理承载核心源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://becamex.com.vn/tin-tuc/`（与总册严格一致，杜绝双源漂移）
* **底层驱动与容器描述**：
  * **驱动类型**：`html_card_driver`（提取第 1 页最新文章卡片 `.news-item` / `.post-item` / `<article>`）。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 触发词：`Lễ ký kết`、`Ký hợp đồng`、`Lễ khởi công`、`Động thổ`、`Bàn giao đất`、`Thuê nhà xưởng`。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-IP-001",
  "title": "Becamex IDC ký kết thỏa thuận cho thuê 15 ha đất tại KCN Bàu Bàng",
  "pub_date_raw": "2026-11-09",
  "subject_entity": "Co-Win Optoelectronics / 协赢光电",
  "geo_location": "Bình Dương (平阳省) / KCN Bàu Bàng (包邦工业区)",
  "signal_type": "land_grant",
  "project_scale": "15 ha, 8000 万美元",
  "evidence_snippet": "Becamex IDC đã bàn giao 15 ha đất công nghiệp cho đối tác sản xuất linh kiện quang học với tổng vốn đầu tư 80 triệu USD.",
  "direct_url": "https://becamex.com.vn/tin-tuc/le-ky-ket-hop-dong-thue-dat-bau-bang-101",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 党建、工会文体比赛、慈善助学通稿及超过 72 小时的存量旧闻。

## 6. 异常与改版判定 (Health & Failure Detection)
* 列表容器返回 0 条记录或返回 HTTP 404 / 500。
