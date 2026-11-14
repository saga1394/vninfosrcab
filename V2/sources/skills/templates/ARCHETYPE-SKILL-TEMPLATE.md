---
name: archetype-skill-template
description: V2 双层解耦架构下上层“业务原型认知技能”标准模板。接收 ParsedSourceCard 并委托底层协议驱动抓取。
inputs:
  parsed_card: ParsedSourceCard
outputs:
  items: List[RawExtractedItem]
---

# 业务认知技能定义：{{archetype_name}}

## 1. 技能定位与双层职责边界
本技能属于上层**业务认知技能（Archetype Skill）**，完全剥离网络通信细节：
* **网络委托驱动**：严格读取卡片 YAML 中的 `protocol_driver` 与 `network_config`，调用 `get_protocol_driver(...)` 执行物理拉取；
* **附件探针增强**：若卡片 `attachment_probe: true`，调用 `probe_pdf_attachments(...)` 提取公报 PDF 首页摘要；
* **业务语义提纯**：执行信号归类、地理与规模字段启发式抽取及卡片第 5 节噪音剔除。

## 2. 健康状态回执契约
* 物理请求抛错或结构异常 -> 调用 `SourceHealthLedger.record_failure(source_id, err)`；
* 顺利执行完成 -> 调用 `SourceHealthLedger.record_success(source_id)`。
