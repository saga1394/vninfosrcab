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
* **机构/媒体法理属性**：越南平阳省属超大型综合工业地产龙头开发商（平阳主力工业区及 VSIP 合资方）。
* **情报定位**：**FDI 外资落地物理承载最前线**。提供平阳省、平福省、广治省等辖区工业园区的现场一手供地、清表平整、开工奠基、中外企业签约租赁一手硬核情报。
* **价值等级**：P1 级一线物理承载核心源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://becamex.com.vn/tin-tuc/`（与总册严格一致，严禁双源漂移）
* **底层驱动与容器描述**：
  * **驱动类型**：`html_card_driver`（兼支持 WordPress 标准文章流或卡片容器提取）。
  * **页面遍历范围**：仅抓取第 1 页最新呈现的新闻卡片（近 72 小时动态）。
  * **DOM 定位特征**：识别文章卡片列表容器 `.news-item` 或 WordPress 标准 `.post-item`，提取 `<a>` 链接与标题、`.date` 日期字符串、`p` 摘要段落。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
`park-news-inspector` 重点从标题与正文导语识别以下触发动作：
* **必须收录的触发词/动向**：
  * `Lễ ký kết` / `Ký hợp đồng`（签约投资 / 租赁工业用地合同）
  * `Lễ khởi công` / `Động thổ`（奠基仪式 / 开工建设）
  * `Bàn giao đất` / `Thuê nhà xưởng`（交付土地 / 租赁标准厂房）
  * `Mở rộng khu công nghiệp`（工业园区扩建 / 规划获批）
* **关键投资主体**：跨国制造业（尤其是中资、台资、日韩大厂）具体租地面积（公顷/m²）与承诺投资额。

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
* 纯集团内部党建、工会活动、员工文体比赛、年终总结会议；
* 慈善捐赠、助学金发放等企业社会责任公关通稿；
* 超过 72 小时的历史存量旧闻。

## 6. 异常与改版判定 (Health & Failure Detection)
* 列表容器返回 0 个卡片项；
* 提示数据库连接异常或返回 HTTP 404 / 500。
