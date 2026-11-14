# 越南产业情报雷达系统 V2 (Ref: 8492 / 2946 / 9381)

本目录为依据 [`8492`](../8492-2026-11-11-source-architecture-qa-audit-report.md)、[`2946`](../2946-2026-11-12-patched-system-architecture-and-implementation-plan.md) 与 [`9381`](../9381-2026-11-10-source-dossier-redesign-dual-model-consultation-report.md) 全量构建的 **V2 独立工程实现**，与根目录原有 V1 版本（`scripts/`、`run_all.py`、`data/`、`config/`）保持物理隔离（仅邮件凭据只读复用 `config/email_config.json`，历史项目库初次运行只读克隆至 `V2/data/projects.db`）。

## 目录结构

* `sources/interfaces/`：强类型契约中心（`contracts.py`）、SQLite 健康账本（`health_ledger.py`）、只读总册编译器（`compile_registry_md.py`）。
* `sources/drivers/`：下层 5 大无状态协议驱动（`rss_driver`、`html_card_driver`、`html_table_driver`、`rest_api_driver`、`sitemap_driver`）、域名级并发节流阀（`HostThrottle <= 2`）与公报 PDF 附件首页摘要探针（`pdf_probe.py`）。
* `sources/skills/`：上层 5 大业务原型认知技能（`job-radar-scanner`、`park-news-inspector`、`gazette-table-parser`、`disclosure-sniffer`、`media-stream-curator`）。
* `sources/cards/` & `sources/rules/global/`：全量 197 张机读参数化信源卡片，以及不可变全局裁量规则 `GLOBAL-JUDGEMENT.md` 与 `GLOBAL-TRANSLATION.md`。
* `pipeline/cognitive/`：阶段 B 认知引擎（`event_ledger.py` 历史台账查重/生命周期防倒退/资产里程碑写回、`stage1_triage.py` 30 条分包并发粗裁与 `date_unverified` 隔离、`stage2_curate.py` AI 草稿解析 + 物理真链回填与 Lazy Probe 死链替补）。
* `pipeline/delivery/`：阶段 C 渲染与分发引擎（`brief_renderer.py` 五大纯净正交栏目 `<80KB` 内联 HTML 渲染与 Pre-Flight 门禁、`email_sender.py` 单一安全测试收件人投递）。
* `run_v2.py`：V2 主调度入口，支持 `--compile-only`、`--collect`、`--full-pipeline` 全链路运行。
* `tests/`：`test_v2_suite.py` 自动化测试套件与 `golden_set.json` 黄金集回归用例。

## 快速运行

```bash
# 1. 运行契约与 197 张卡片全量编译校验
.venv\Scripts\python.exe V2/sources/interfaces/test_contracts.py

# 2. 运行 V2 全链路单元测试与 Golden Set 回归测试
.venv\Scripts\python.exe V2/tests/test_v2_suite.py

# 3. 仅编译生成 V2 只读总册与 JSON 配置
.venv\Scripts\python.exe V2/run_v2.py --compile-only

# 4. 仅运行全量采集（产出 CandidateVault 与脱敏 LLM Payloads）
.venv\Scripts\python.exe V2/run_v2.py --collect

# 5. 全链路 Stage A -> B -> C（Dry-Run 预览，不发邮件）
.venv\Scripts\python.exe V2/run_v2.py --full-pipeline --date YYYY-MM-DD

# 6. 复用当日采集与外部 AI 研判草稿执行渲染 + 安全单人试发 + 里程碑入库
.venv\Scripts\python.exe V2/run_v2.py --full-pipeline --skip-collect --date YYYY-MM-DD --draft-json V2/data/runs/YYYY-MM-DD_curated_draft.json --send-email
```
