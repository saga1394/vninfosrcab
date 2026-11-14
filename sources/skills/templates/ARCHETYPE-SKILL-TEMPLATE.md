---
name: archetype-skill-template
description: 双层解耦架构下上层“业务原型认知技能”标准模板。接收卡片语义指令并调度底层协议驱动。
inputs:
  parsed_card: ParsedSourceCard   # 解析后的强类型卡片对象
outputs:
  items: List[RawExtractedItem]   # 标准原始提取物料（由调度框架包裹 Candidate ID）
---

# 业务认知技能定义：{{archetype_name}}

## 1. 技能定位与双层职责边界
本技能属于上层**业务认知技能（Archetype Skill）**，完全剥离网络通信细节：
* **只管业务语义**：依据卡片中定义的“核心信号捕捉规则”、“重点赛道要求”与“噪声屏蔽准则”，对抓回来的结构化文本做判别、清洗与规范字段提炼；
* **网络委托驱动**：严格读取卡片 YAML 中的 `protocol_driver`（`rss_driver` / `html_card_driver` / `html_table_driver` / `rest_api_driver` / `sitemap_driver`）与 `network_config`，委托对应底层驱动执行物理拉取。

## 2. 标准执行链路 (Execution Pipeline)
```
[读取 ParsedSourceCard] 
       │
       ▼
[调度对应 protocol_driver 并注入 network_config / search_spec / api_spec]
       │
       ▼
[若有 attachment_probe=true，触发 PDF 摘要解析增强器]
       │
       ▼
[执行业务认知过滤：匹配信号词 + 剔除卡片第5节噪声]
       │
       ▼
[输出 List[RawExtractedItem] 并上报 SourceHealthLedger]
```

## 3. 健康状态回执契约
* 物理请求抛错 / 结构解析异常为空（非正常无更新） -> 调用 `SourceHealthLedger.record_failure(source_id, err)`；
* 顺利抓取（含正常无更新返回 `[]`） -> 调用 `SourceHealthLedger.record_success(source_id)`。
