# 2946-2026-11-12 越南产业与 FDI 情报雷达系统：全量补丁合龙版顶层架构与分阶段实施计划

> **【自启动提示词（新会话一键调用）】**  
> 请阅读并严格执行本项目全量补丁合龙版顶层架构与实施计划 `E:\geminiworks\vninfosrcab\2946-2026-11-12-patched-system-architecture-and-implementation-plan.md`（引用码：**2946**）。  
> **核心目标**：基于经独立 QA（7629、8492）双重审计且已完成全套补丁固化的底层契约底座，按四阶段稳步推进：实现 5 大无状态协议驱动、完成全量 177+ 可用源与招聘雷达的逐源建卡入册、贯通“AI 查历史库对账 + 防幻觉 URL 回填”研判中枢，并完成全链路端到端每日自动化早报投递。  
> **执行铁律与关键边界**：  
> 1. **唯一事实源**：严禁手工编辑 `MASTER-SOURCE-REGISTRY.md`，所有信源变更必须在 `sources/cards/*.md` 中完成并通过 `compile_registry_md.py` 自动编译同步；  
> 2. **强类型测试先行**：每次变更卡片或契约，必须跑通 `python sources/interfaces/test_contracts.py`；  
> 3. **彻底终结四大历史顽疾**：废除 38 源萎缩（激活全量可用源且不设无理条数限制，做到应收尽收）；严格执行 `Candidate_ID` 脱敏与物理回填（剥夺 AI 输出 URL 的权力）；强制以两阶段流水线与 `date_unverified` 隔离带杜绝旧闻炒冷饭；  
> 4. **严谨语言与交付**：保持产业分析师客观克制风格，五大正交栏目绝对纯净无副标题，QQ 邮箱内联 HTML 体积 <80KB、零附件，统一落款【太空建筑观察】越南组。

---

## 一、 补丁合入现状与最新底座资产清单

本计划已正式吸收并落地了架构规范（`6528`、`5184`）与两次独立 QA 审计（`7629`、`8492`）的全部 12 项核心修订补丁，**底层工程底座已于 2026-11-12 通过 100% 自动化测试**：

| 底座资产模块 | 物理路径 | 核心职责与已验证状态 |
| :--- | :--- | :--- |
| **强类型契约中心** | [`sources/interfaces/contracts.py`](file:///E:/geminiworks/vninfosrcab/sources/interfaces/contracts.py) | 统一定义 `RegistryEntry`, `RawExtractedItem`, `ExtractedCandidate`, `CuratedBriefItem`、`backfill_candidate_urls()` 及基于 PyYAML 的 `SourceCardParser`（已修复大小写容错、URL 井号截断、TypeError 报错）。 |
| **健康状态机账本** | [`sources/interfaces/health_ledger.py`](file:///E:/geminiworks/vninfosrcab/sources/interfaces/health_ledger.py) | 基于 SQLite `state_ledger.db` 实现 `source_health` 表，自动维护连续失败计数并触发 `active <-> degraded` 流转。 |
| **只读总册编译器** | [`sources/interfaces/compile_registry_md.py`](file:///E:/geminiworks/vninfosrcab/sources/interfaces/compile_registry_md.py) | 自动扫描所有卡片并与健康账本同步，确定性生成只读 `MASTER-SOURCE-REGISTRY.md` 与 `config/master_sources_registry.json`。 |
| **自动化测试套件** | [`sources/interfaces/test_contracts.py`](file:///E:/geminiworks/vninfosrcab/sources/interfaces/test_contracts.py) | 验证卡片解析、防幻觉回填、健康状态机与总册编译的全链路回归测试（**100% PASS**）。 |
| **标准总册与卡片模板** | [`sources/templates/`](file:///E:/geminiworks/vninfosrcab/sources/templates/SOURCE-CARD-TEMPLATE.md) | 包含 `protocol_driver`、`network_config`（SSL容错）、`search_spec`（参数化搜索模板）、`api_spec` 与 `attachment_probe` 声明。 |
| **首批高保真示范卡** | [`sources/cards/`](file:///E:/geminiworks/vninfosrcab/sources/cards/SRC-JOB-001-vietnamworks.md) | 覆盖招聘前瞻雷达 (`SRC-JOB-001`)、工业园区一线 (`SRC-IP-001`)、环评公文 (`SRC-APP-001`)。 |

---

## 二、 打补丁后的全景系统运转架构

```
+======================================================================================+
| 阶段 A：配置与调度层 (1 个总册 + 5 大业务认知技能 + 5 大底层协议驱动 + 200 张卡片)      |
+======================================================================================+
  1. [调度器] 读取编译产物 config/master_sources_registry.json，过滤 status == 'active'
  2. [双层分离执行] 按卡片的 protocol_driver 调度底层驱动，并注入 network_config / search_spec:
     - rss_driver        (原生 RSS/Atom 秒级流)
     - html_card_driver  (规整图文卡片 & Next.js __NEXT_DATA__ 树提取)
     - html_table_driver (ASP.NET / 政务结构化表格 <tr> 遍历)
     - rest_api_driver   (SPA 后端 API / 静态 JS 数据数组抽取)
     - sitemap_driver    (XML Sitemap 增量抽取，覆盖 VBPL 等)
     - [增强器] 若 attachment_probe=true，提取并解析公报 PDF 附件首页摘要
  3. [应收尽收原则] 不设主观“仅抓3~5条”死限制，抓取当日/近72h所有有效新增，失败自动记入健康账本
  4. [赋码脱敏] 框架将 RawExtractedItem 赋码为不可变 Candidate_ID (如 C-SRC-JOB-001-0001)
     并生成剔除 direct_url 的安全 Payload，彻底封死 AI 编造链接的路径

                                         │
                                         ▼ (每日全网毛坯池: 150~300 条)

+======================================================================================+
| 阶段 B：AI 认知对账与防幻觉研判中枢 (Two-Stage Curation + 历史库对账)                  |
+======================================================================================+
  Step B1 [并行分包粗裁] (解决 Lost in the Middle 与长文本超时):
     - 每 30 条为一批，并发执行轻量评估：识别真时效(近48~72h，无锚点旧文档标 date_unverified 隔离)
       + 辨析越南本土/海外强传导因果链 + 过滤卡片第5节定义的具体噪声，淘汰 80%+ 杂讯
  Step B2 [深度对账与脉络串接] (核心增值大脑):
     - 携带 Step B1 筛选出的候选，反查本地 projects.db / 历史情报库，完成三项核心工作:
       (a) 语义排重合并：多家媒体同日报一件事 -> 合并为一，多视角拼接完整事实
       (b) 历史后续追踪：识别“前月招厂长/签约意向 -> 今日环评/奠基开工”，打标 [is_follow_up=true]
       (c) 严密归仓与规范加工：分入五大正交纯净栏目，翻译规范中文企名，写好【事实】与【看点】
     - 输出严格受限于 CuratedBriefItem Schema，仅返回 ref_candidate_ids

                                         │
                                         ▼

+======================================================================================+
| 阶段 C：安全回填、延迟探活与双轨交付                                                    |
+======================================================================================+
  1. [物理回填] backfill_candidate_urls() 根据 ref_candidate_ids 100% 映射回真实 direct_url
  2. [延迟探活 Lazy Probe] 仅对最终选中的 15~25 条交付 URL 执行最终 200 OK 校验（省90%探活开销与防封）
  3. [门禁容错] 周末公休日若【行政审批】为 0 条，自动渲染标准占位符而不触发异常熔断
  4. [双轨交付]
     - 邮件轨：紧凑内联 CSS (<80KB, 零附件)，直发 18677106863@qq.com，落款【太空建筑观察】越南组
     - 资产轨：今日新核实主体、金额、园区、项目阶段里程碑增量写入 projects.db，供明日继续对账
```

---

## 三、 分阶段实施路线图 (Execution Roadmap)

### 阶段 0：契约底座与样板固化（【已完成】 2026-11-12）
* **任务内容**：合入 8492 QA 报告全部 5 项补丁，重写 `contracts.py`，构建 `health_ledger.py` 与 `compile_registry_md.py`，更新示范卡片并通过 `test_contracts.py` 验证。
* **状态**：**100% 完成并验证通过**。

---

### 阶段 1：5 大底层协议驱动研发与单点探活验证（预期周期：1~2 会话）
* **核心任务**：
  1. 在 `sources/drivers/` 下研发 5 个无状态协议驱动与 1 个 PDF 附件探针：
     * `rss_driver.py`
     * `html_card_driver.py`（必须支持从 `search_spec.endpoint_template` 参数化拼接请求及 `__NEXT_DATA__` JSON 抽取）
     * `html_table_driver.py`
     * `rest_api_driver.py`
     * `sitemap_driver.py`
     * `pdf_probe.py`（基于 `pypdf` 抽取公报首页摘要）
  2. **集成 Host-level 并发节流阀**：建立域名信号量控制（同 Host 并发 ≤ 2），防范同省多厅局集中请求引发 429 封锁；透传各卡片 `network_config.verify_ssl`。
* **验收门禁**：
  * 用这 5 个驱动实际对接跑通现有的 3 张示范卡（`SRC-JOB-001`、`SRC-IP-001`、`SRC-APP-001`）外加 1 个 RSS 源与 1 个 Sitemap 源，真实返回有效 `RawExtractedItem` 列表，且状态机自动记为 `active`。

---

### 阶段 2：全量信源分批“实测建卡”与总册合龙（彻底终结 38 源萎缩）
* **核心纪律**：**严禁根据旧文档拍脑袋批量盲生成卡片！** 必须按大类分批，逐源实际请求探测版面结构、验证协议与筛选规则，确保每张卡**建一张、通一张、入册一张**：
  * **第 1 批（前瞻微信号先行，~20 项）**：
    * 新增并摸清高价值招聘雷达（VietnamWorks、TopCV、ITviec、CareerBuilder VN、LinkedIn 重点涉越制造搜索）；
    * 境外母公司信披（巨潮资讯 A 股涉越、台交所 MOPS、港交所披露易）。
  * **第 2 批（国家级法定审批与标杆工业园区，~35 项）**：
    * 环评 DSDTM、排污许可 DSGiayPhep、外资局 FIA（含 PDF 探针）、统计局 NSO、VSIP、Becamex、Deep C、Viglacera、KBC、Sonadezi、IDICO、Amata 等标杆园区开发商。
  * **第 3 批（高召回财经媒体专版，~45 项）**：
    * VIR、CafeF 房地产与工业版、VnExpress 商业版、Tuổi Trẻ、VietnamPlus、The Investor（Sitemap）、Nikkei Asia、DIGITIMES 等。
  * **第 4 批（16 重点省市工业区管委会与投资计划厅攻坚，~70+ 项）**：
    * 根据 7163 摸排结果，逐一实测北宁、海防、广宁、平阳、同奈、隆安、义安、太原等省市管委会与厅局，死链或不更新的直接打标 `retired` / `low_freq`，存活且高质量的正式制卡入册。
* **验收门禁**：
  * 全部卡片必须通过 `test_contracts.py` 强类型检查，并经由 `compile_registry_md.py` 自动合拢生成全量版 `MASTER-SOURCE-REGISTRY.md`。

---

### 阶段 3：AI 认知对账流水线与防幻觉闭环集成（接入 9381 全局规则）
* **核心任务**：
  1. 在 `pipeline/cognitive/` 实现两阶段认知调度器：
     * **Stage 1（并发分包粗裁）**：每 30 条一批并行筛选，过滤噪声与 `date_unverified` 历史文档；
     * **Stage 2（历史库对账精编）**：挂载 9381 报告确立的《12 大类认知操作手册》与《全局研判规则》，实时反查 `projects.db` 进行实体去重合并、不同角度拼接与前后进展串接，输出 `CuratedBriefItem`。
  2. 接入 `backfill_candidate_urls()` 物理回填链接 + **Lazy Probe 延迟探活**（仅对最终选入早报的 Top 15~25 条链接发起最终 200 OK 校验，失效自动启用备选池替补）。

---

### 阶段 4：端到端稳态验收与常态化自动化交付
* **核心任务**：
  1. 重构项目入口 `run_all.py` 严格按照“阶段 A -> 阶段 B -> 阶段 C”单向流水线串联；
  2. 注入公休日自适应空仓占位逻辑（周末【行政审批】为 0 时正常出报不报错）；
  3. 实际触发 1 轮全量大池子试运行，发送真实简报至 `18677106863@qq.com` 完成肉眼验收。
* **最终验收标准（一票否决线）**：
  * **真实性**：简报中 100% 链接点击即达原文，无 404 或首页占位符；
  * **覆盖度**：不再局限于 38 个源，真正囊括了招聘前瞻、一线园区、跨国信披与全越各重点省份；
  * **时效与排重**：近 48~72 小时最新动态，绝对零旧闻炒冷饭，且跨媒体同事件已完美合并；
  * **体量与风格**：邮件 <80KB、内联 CSS 手机端无截断、五大正交栏目纯净无副标题、客观严谨的【事实】与【看点】。

---

## 四、 立即执行的下一步建议

当前 **阶段 0 底座已经焊死并测试通过**。建议下一动作直接启动 **阶段 1（研发 5 大底层协议驱动 + Host 节流阀）**，用真正的底层驱动把已经做好的 `SRC-JOB-001`、`SRC-IP-001`、`SRC-APP-001` 三张示范卡从线上实打实地把真数据抓回来，彻底验证全链路闭环！
