# 越南产业与 FDI 全景信源总册标准模板 (Master Source Registry Template)

> **版本**：v1.1.0（已合入 8492 QA 强类型对齐与协议双层解耦补丁）  
> **更新日期**：2026-11-12  
> **维护规则**：本表为只读编译产物，由 `sources/interfaces/compile_registry_md.py` 依据 `sources/cards/*.md` 与 `source_health` 状态账本自动生成，严禁手工篡改。

---

## 一、 核心元数据枚举字典 (Data Dictionary)

* **归属集群大类 (`cluster`)**：`job_radar` | `industrial_park` | `legal_approval` | `corporate_disclosure` | `media_fdi`
* **上层业务认知技能 (`archetype_skill`)**：`job-radar-scanner` | `park-news-inspector` | `gazette-table-parser` | `disclosure-sniffer` | `media-stream-curator`
* **底层网络协议驱动 (`protocol_driver`)**：
  * `rss_driver`：原生 RSS / Atom 极速流
  * `html_card_driver`：规整图文卡片容器解析
  * `html_table_driver`：规整 HTML / ASP.NET 数据表格解析
  * `rest_api_driver`：JSON REST API / SPA 接口请求
  * `sitemap_driver`：XML Sitemap 增量流解析
* **调度优先级 (`priority`)**：`P0`（核心前瞻/硬证据） | `P1`（重点日常） | `P2`（辅助印证）
* **预期归仓栏目 (`expected_column`)**：`fdi` | `industrial_park` | `industry_focus` | `legal_approval` | `macro_policy`
* **巡检频次 (`check_frequency`)**：`daily` | `weekly` | `monthly`
* **运行状态 (`status`)**：`active` | `degraded` | `low_freq` | `retired`（严格全小写）

---

## 二、 全景信源总册登记表 (Standard Scaffold)

| `source_id` | `name` | `cluster` | `archetype_skill` | `protocol_driver` | `priority` | `expected_column` | `check_frequency` | `status` | `card_path` | `last_audit_date` |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| `SRC-JOB-001` | VietnamWorks 越南高端招聘雷达 | `job_radar` | `job-radar-scanner` | `html_card_driver` | **P0** | `fdi` | `daily` | **active** | `sources/cards/SRC-JOB-001-vietnamworks.md` | 2026-11-12 |
| `SRC-IP-001`  | Becamex IDC 工业地产与招商动态 | `industrial_park` | `park-news-inspector` | `html_card_driver` | **P1** | `industrial_park` | `daily` | **active** | `sources/cards/SRC-IP-001-becamex.md` | 2026-11-12 |
| `SRC-APP-001` | 越南国家环境影响评价 (ĐTM) 公示 | `legal_approval` | `gazette-table-parser` | `html_table_driver` | **P0** | `legal_approval` | `daily` | **active** | `sources/cards/SRC-APP-001-dsdtm.md` | 2026-11-12 |
