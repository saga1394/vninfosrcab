# 项目历史、过程与实验文件归档索引 (Archive Ledger)

**归档日期**：2026-11-05  
**归档范围**：最新生产版本（`run_all.py` / 38核心源采集引擎 / 认知归仓 / 研判渲染 / 邮件分发）以及核心历史数据库（`collector.db`、`projects.db`、`historical_repository.json`、`data/historical_reports/`）之外的全部阶段性规划、探索性脚本、中间过程转储与测试产物。

---

## 归档目录结构一览

```
archive/
├── README.md                                  # 本归档索引说明文档
├── archive_process_and_history_20261105.zip   # 完整归档打包 ZIP 压缩文件
│
├── plans_and_reports/                         # 17 个历史阶段计划与里程碑报告
│   ├── 2026-11-01-ADJUSTED-SOURCES.md
│   ├── 2026-11-01-PROJECT-RESULTS.md
│   ├── 2491-2026-11-03-hybrid-automation-and-llm-workflow-trial.md
│   ├── 3719-2026-11-01-PROBE-REPORT.md
│   ├── 3719-2026-11-01-rss-and-lightweight-probe-plan.md
│   ├── 4178-2026-11-02-stage-report-core-sources-and-automated-workflow.md
│   ├── 5392-2026-11-02-stage2-entity-alignment-and-project-profiling-plan.md
│   ├── 5832-2026-11-04-briefing-taxonomy-and-content-reconstruction-plan.md
│   ├── 5921-2026-11-01-probe-results-review-report.md
│   ├── 6152-2026-11-03-historical-intelligence-repository-construction.md
│   ├── 6824-2026-11-02-stage-report-workflow-review-and-broad-to-broad-evolution.md
│   ├── 7163-2026-11-02-full-source-inventory-and-verification-plan.md
│   ├── 7294-2026-11-05-purge-enterprise-registration-task-plan.md
│   ├── 8253-2026-11-02-routine-inspection-framework-and-trial-run.md
│   ├── 8294-2026-11-04-routine-inspection-report-and-intelligence-delivery.md
│   ├── 9154-2026-11-05-routine-intelligence-inspection-and-delivery-plan.md
│   └── 9481-2026-11-02-stage-report-full-source-inventory.md
│
├── scripts_experimental/                      # 探索、嗅探与中间分析脚本
│   ├── inventory/                             # 84 个信源摸底、接口嗅探与协议测试脚本
│   ├── root_and_collector/                    # 原 3719 嗅探脚本、workflow runner 原型与数据清洗脚本
│   │   ├── 3719_probe.py
│   │   ├── workflow_runner.py
│   │   └── clean_and_verify.py
│   └── stage2_interim/                        # 22 个 Stage2 开发过渡、单日增量试验与临时诊断脚本
│       ├── analyze_project_signals.py
│       ├── apply_cognitive_classification.py
│       ├── apply_d5_signals.py
│       ├── apply_today_signals.py
│       ├── apply_today_signals_1104.py
│       ├── archive_20261104.py
│       ├── audit_vn_relevance.py
│       ├── check_unclassified.py
│       ├── deep_inspect.py
│       ├── dump_high_signal.py
│       ├── export_delta.py
│       ├── find_d5.py
│       ├── find_vietnam_targets.py
│       ├── inspect_items_10_25.py
│       ├── inspect_key_unclassified.py
│       ├── inspect_records.py
│       ├── inspect_today.py
│       ├── inspect_today_59.py
│       ├── llm_judge_items.py
│       ├── save_signals.py
│       ├── search_vietnam_local.py
│       └── update_expectation_categories.py
│
├── data_process_dumps/                        # 阶段性过程数据转储
│   ├── 3719_probe_results.json                # 11-01 嗅探原始产物
│   ├── inventory/                             # batch 1~4 信源摸底原始 JSON
│   └── daily_dumps/                           # 历次巡检运行明细报告与待审转储
│       ├── 2026-11-02_run_report.json
│       ├── 2026-11-03_run_report.json
│       ├── 2026-11-04_run_report.json
│       ├── 2026-11-04_extracted_59.json
│       ├── 2026-11-05_run_report.json
│       ├── nov_items_to_judge.json
│       └── pending_delta.json
│
└── docs_process_and_drafts/                   # 中间阶段性文档与测试排版残留
    ├── inventory/                             # 7163 批次摸底台账与报告 (Batch 1~4)
    └── test.pdf                               # 历史排版调试生成 PDF (2.5MB)
```

---

## 核心生产保留清单（未变动，保持纯净稳定）

1. **根目录生产文件**：
   - `run_all.py`：全流程总调度入口
   - `requirements.txt`：生产运行依赖项
   - `AGENTS.md`：核心工作纪律、系统记忆与栏目规范
   - `PROJECT-LOG.md`：项目演进全生命周期流水总账
   - `.github/workflows/daily_intel.yml`：CI/CD 自动化流水线
2. **核心配置目录 `config/`**：
   - `sources_core_39.json`：收敛后 38 个高净值实体源配置
   - `email_config.json`：三人矩阵独立投递配置
3. **活跃业务脚本 `scripts/`**：
   - `scripts/collector/collector_engine.py`：Stage 1 极速并发采集器
   - `scripts/delivery/send_report_email.py`：内联 CSS 邮件分发器
   - `scripts/stage2/entity_pipeline.py`：实体对齐与项目时空事件库组装器
   - `scripts/stage2/generate_dimensional_report.py`：全维简报生成器
   - `scripts/stage2/generate_dossier_portfolio.py`：项目档案库生成器
   - `scripts/stage2/generate_html_report.py`：五大正交大盘看板与高清 PDF 生成器
   - `scripts/stage2/generate_rss_feed.py`：公开 RSS 动态流发生器
   - `scripts/stage2/query_history.py`：历史库命令行反向检索工具
   - `scripts/stage2/generate_historical_repository_doc.py`：历史沉淀知识库编译
   - `scripts/stage2/ingest_historical_reports.py`：历史报告知识抽取管道
4. **核心历史数据库与原始资料 `data/`**：
   - `data/daily/collector.db`：原始材料 SQLite 主库
   - `data/daily/YYYY-MM-DD.jsonl`：每日抓取增量流日志
   - `data/stage2/projects.db`：实体项目对齐 SQLite 数据库
   - `data/stage2/historical_repository.json`：全量历史知识库底册 (~1MB)
   - `data/stage2/projects_dossier.json`：项目画像集
   - `data/historical_reports/`：2026年7月至11月历次历史简报底册及资产
5. **线上交付产物 `docs/`**：
   - `docs/index.html`：GitHub Pages 线上大盘
   - `docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-REPORT.html`
   - `docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-REPORT.pdf`
   - `docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-BRIEF.md`
   - `docs/stage2/HISTORICAL-INTELLIGENCE-REPOSITORY.md`
   - `docs/stage2/PROJECT-DOSSIER-PORTFOLIO.md`
   - `docs/stage2/feed.xml`
