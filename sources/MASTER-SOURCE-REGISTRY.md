# 越南产业与 FDI 全景信源总册 (Master Source Registry)

> **自动编译时间戳**：2026-11-12 21:56:32  
> **重要警告**：本文件由 `sources/interfaces/compile_registry_md.py` 依据各卡片 YAML 与健康账本自动生成，**严禁手工直接修改本表格**！新增/调整信源请修改对应卡片文件并重新执行编译。

- **总纳管信源数**：`3` 项（活跃 `active`: **3** | 降级 `degraded`: **0**）

| `source_id` | `name` | `cluster` | `archetype_skill` | `protocol_driver` | `priority` | `expected_column` | `check_frequency` | `status` | `card_path` | `last_audit_date` |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| `SRC-APP-001` | 越南国家环境影响评价 (ĐTM) 法定公众征询公示平台 | `legal_approval` | `gazette-table-parser` | `html_table_driver` | **P0** | `legal_approval` | `daily` | **active** | [SRC-APP-001-dsdtm.md](cards/SRC-APP-001-dsdtm.md) | 2026-11-12 |
| `SRC-IP-001` | Becamex IDC 工业地产与招商动态 | `industrial_park` | `park-news-inspector` | `html_card_driver` | **P1** | `industrial_park` | `daily` | **active** | [SRC-IP-001-becamex.md](cards/SRC-IP-001-becamex.md) | 2026-11-12 |
| `SRC-JOB-001` | VietnamWorks 越南高端招聘雷达 | `job_radar` | `job-radar-scanner` | `html_card_driver` | **P0** | `fdi` | `daily` | **active** | [SRC-JOB-001-vietnamworks.md](cards/SRC-JOB-001-vietnamworks.md) | 2026-11-12 |
