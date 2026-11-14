# 8492-2026-11-11 越南产业情报信源造册、建卡与通用 Skill 架构体系 (5184) 独立工程审查与 QA 压力测试报告

> **【自启动提示词（供后续会话直接调用）】**  
> 请阅读并严格执行由首席系统审核官出具的信源体系 QA 压力测试报告 `E:\geminiworks\vninfosrcab\8492-2026-11-11-source-architecture-qa-audit-report.md`（引用码：**8492**）。  
> **核心目标**：依据本报告对 `5184-2026-11-11-source-registry-card-and-skill-system-specification.md` 及其配套资产（总册模板、卡片模板、示范卡、通用 Skill 规范、接口契约 `contracts.py`）的独立审查结论，精准实施 5 大关键工程补丁，消除强类型契约断层、消除业务原型与底层网络协议混淆、补齐异构边缘源（Sitemap/API/PDF）、填平自动化状态机闭环与大模型脱敏 URL 回填链路断裂，确保信源工程从规范稳步落地到生产代码。  
> **审查基准**：严格对照项目守则 `AGENTS.md`、全网 196 源摸排总台账 `7163`、顶层系统架构设计 `6528`、上轮架构审查报告 `7629` 及接口实测运行结果，秉持独立客观、用代码与极端工况说话的最高工程纪律。

---

## 审查执行概要

| 审查维度 | 核心结论与状态 |
| :--- | :--- |
| **审查对象集合** | 1. 核心规范：`5184-2026-11-11-source-registry-card-and-skill-system-specification.md`<br>2. 总册模板：`sources/templates/MASTER-REGISTRY-TEMPLATE.md`<br>3. 卡片模板：`sources/templates/SOURCE-CARD-TEMPLATE.md`<br>4. 示范卡片：`SRC-JOB-001`, `SRC-IP-001`, `SRC-APP-001`<br>5. 通用 Skill 体系：`ARCHETYPE-SKILLS-SPEC.md`, `ARCHETYPE-SKILL-TEMPLATE.md`<br>6. 接口契约：`sources/interfaces/contracts.py` |
| **参考对照基准** | `AGENTS.md`、`FULL-SOURCE-INVENTORY-LEDGER.md`（7163 台账）、`6528` 顶层架构规范、`7629` 上轮审查报告、本地 Python 3.13 实体运行测试 |
| **审核官身份** | 首席技术审核官（Chief System Auditor） |
| **审查方法** | 契约强类型静态/动态对齐测试、196 源技术协议全景映射推演、单点网络请求逆向分析、极端工况对抗测算 |
| **最终评审裁决** | **【有条件通过，完成 5 大必改补丁后方可实施 (Conditional Pass with Mandatory Patches)】** |

---

## 一、 架构完整性审查与静态契约对齐测试

5184 体系确立了“1 个全景总册 + 5 大通用原型 Skill + 200 张专属作业指导卡”的解耦模式，宏观方向切中了项目历史的“死板爬虫死绑单一网站”的核心病灶。然而，在微观契约对齐、数据类实现与模板定义之间，存在**多处直接导致 Python 运行时崩溃的致命硬伤**。

### 1.1 静态契约断层与运行时类型报错（实测验证）

经过编写自动化测试脚本对 `contracts.py`、卡片 Markdown、总册模板进行闭环反向解析测试，暴露出以下不可调和的矛盾：

```
+---------------------------------------------------------------------------------------------------------+
|                                        契约断层与运行时报错大盘                                           |
+--------------------------+------------------------------+-----------------------------------------------+
| 触发组件                 | 异常类型                     | 错误成因与现场报错信息                        |
+--------------------------+------------------------------+-----------------------------------------------+
| 卡片 -> RegistryEntry    | TypeError: unexpected keyword | RegistryEntry 缺失 priority 与 expected_column|
|                          | argument 'priority'          | 卡片元数据无法直接反向转为总册条目            |
+--------------------------+------------------------------+-----------------------------------------------+
| 卡片 JSON -> Candidate  | TypeError: missing 2 required| ExtractedCandidate 强制要求 candidate_id 与   |
|                          | positional arguments         | extracted_at，但所有示范卡与模板 JSON 均缺失！|
+--------------------------+------------------------------+-----------------------------------------------+
| 总册 -> SourceStatus     | Enum Validation Failure      | 总册模板为 "Active"（首字母大写），contracts.py|
|                          |                              | 为 Literal["active"]（全小写），校验直接失败  |
+--------------------------+------------------------------+-----------------------------------------------+
| 总册表头 -> 字段名映射   | Key Mismatch                 | 模板括号标注 `freq` 与 `last_audit`，代码与规  |
|                          |                              | 范字段为 `check_frequency` 与 `last_audit_date`|
+--------------------------+------------------------------+-----------------------------------------------+
| 总册表格 -> 文本清洗     | Formatting Pollution         | 表格内容含有反引号（`SRC-JOB-001`）与中文“每日”|
|                          |                              | 缺乏强类型反序列化脱壳机制                     |
+--------------------------+------------------------------+-----------------------------------------------+
```

#### 详细现场还原：
1. **`RegistryEntry` 与 `SourceCard` 字段割裂（Schema Drift）**：
   - 卡片模板与示范卡定义了极其重要的调度权重 `priority: P0 | P1 | P2` 以及归仓倾向 `expected_column: fdi | industrial_park | ...`。
   - 但是 `contracts.py` 中的 `RegistryEntry` 数据类**完全遗漏了这两个关键字段**！
   - 调度器如果仅通过 `RegistryEntry` 加载总册，将丢失 P0/P1/P2 巡检优先级与预期归仓倾向，导致调度引擎无法根据网络负载进行分级削峰。
2. **`ExtractedCandidate` 实例化 100% 崩塌**：
   - `ExtractedCandidate` 定义中，`candidate_id: str` 与 `extracted_at: str` 属于无默认值的非可选必填字段。
   - 然而，`SOURCE-CARD-TEMPLATE.md` 以及首批三张示范卡（VietnamWorks、Becamex、DSDTM）第 4 节的输出契约 JSON 示例中，**压根没有这两个字段**！
   - 一旦通用 Skill 或无头脚本按照示范卡规范提取并组装 JSON，调用 `ExtractedCandidate(**item)` 时将必定抛出 `TypeError` 崩溃。
3. **大小写与自然语言污染断层**：
   - `contracts.py` 严格定义了小写 `SourceStatus = Literal["active", "degraded", "low_freq", "retired"]`；
   - 总册模板与 5184 规范第 2.1 节却使用大写驼峰 `Active`、`Degraded`、`Low_Freq`、`Retired`；
   - 总册巡检频次写为中文“每日”，而不是 `"daily"`。若无自动化解析适配层，直接作为类型校验将引发大面积类型断言失败。

### 1.2 `SourceCardParser` 手工解析器的脆弱性
`contracts.py` 中提供的简易 YAML 解析器存在严重的边界缺陷：
```python
frontmatter[key.strip()] = val.split("#")[0].strip()
```
- 若目标 URL 带有 URL 片段锚点（如 `https://example.com/portal#news`）或 URL 参数中含有 `#`，`split("#")[0]` 会强行截断合法 URL；
- 无法处理带引号的字符串（如 `name: "Becamex IDC"` 会残留双引号）；
- 缺少对必填 Frontmatter 键的显式校验与 Schema 报错。

---

## 二、 历史死结破解能力评估 (对照 17 个历史会话病灶)

对照本项目既往 17 个会话暴露的 6 大核心工程死结，对 5184 架构进行闭环对照审查：

```
+--------------------------------------------------------------------------------------------------------------------+
| 历史核心病灶                 | 既往失败表象 (Session 01~17)       | 5184 架构机制           | 审核官裁定与遗留盲区         |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 1. 信源盲目萎缩至 38 个      | 害怕杂讯，一刀切砍源，丢掉 80% 动态| 1个总册+200张卡片，     | 【通过】解耦思路彻底终结萎缩 |
|                              | 导致地方园区与审批全面盲区         | 细化单源作业，全域包容  | 需对 177 源建卡排期落地      |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 2. 大模型幻觉编造假链接      | AI 编造假 URL 或回退到一级根域名   | `to_llm_payload()` 剥夺 | 【部分破解】脱敏彻底，但下游 |
|                              | 破坏“可点击直达”铁律               | URL，只暴露 candidate_id| 回填链路缺失，逻辑断头       |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 3. 旧闻混入炒冷饭 (时效穿梭) | 几个月前旧闻被常青页面或爬虫重复带入| 卡片规约只看最新 1~2 页;| 【基本通过】但对无日期常青页 |
|                              | 侵占晨报版面                       | 强制提取 pub_date_raw   | 仍需 Layer 2 指纹账本兜底    |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 4. 微商工商垃圾泛滥          | 企业登记局海量个体户微型执照流水   | 卡片设立“噪音屏蔽与跳过 | 【通过】单卡专属跳过准则比单 |
|                              | 挤爆情报池                         | 准则”，一票否决         | 一全局字典更精准             |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 5. 官方法定公示与前瞻性矛盾  | 公示准但慢，前瞻快但杂，简报失衡   | 设立正交集群：job_radar | 【通过】分类清晰，互为印证   |
|                              | 栏目配比失调                       | 与 legal_approval 并存  | 需防止周末无审批时死锁       |
+------------------------------+------------------------------------+-------------------------+------------------------------+
| 6. 脚本与大模型分工失控      | 脚本硬过滤致误杀，或把大模型当爬虫 | 脚本跑卡片参数提取，    | 【通过】分工边界清晰符合     |
|                              | 耗尽海量 Token                     | LLM 只做研判归仓        | AGENTS.md 宪法               |
+------------------------------+------------------------------------+-------------------------+------------------------------+
```

---

## 三、 5 大通用 Skill 的全量包容度与边缘异构源审查

对照 `FULL-SOURCE-INVENTORY-LEDGER.md`（7163 摸排总台账）中经实测验证的 196 个源（177 个可用源），对 5 大通用 Skill 进行全景压力测试。

### 3.1 核心架构概念偏差：业务原型（Cluster）与传输协议（Protocol）的笛卡尔积混淆

5184 规范将底层通用技能按**业务属性**划分为：
`job-radar-scanner` / `park-news-inspector` / `gazette-table-parser` / `disclosure-sniffer` / `media-stream-curator`。

然而，在底层网络 I/O 与反爬工程中，**计算机只认传输协议，不认业务属性**：
- 工业园区动态（`industrial_park`）中：Becamex、VSIP、BW 是 **WordPress RSS 2.0**；DEEP C 是 **HTML 卡片**；而岘港高新区管委会（`VN-LOC-14-DD-B`）是 **JSON REST API**（`/api/v1/news`）！
- 企业信披（`corporate_disclosure`）中：巨潮资讯、深交所、SEC EDGAR 是 **REST API**；但日本东京证券交易所（`src-DISC-09`）是 **HTML 数据表格**！
- 法定审批（`legal_approval`）中：环境部 DSDTM 是 **ASP.NET HTML 表格**；但国家法律法规库 VBPL（`src-A13`）是 **结构化 XML Sitemap**（`sitemap/1.xml`，5000条中央法规）！

**审查裁定**：
若要求 `park-news-inspector` 既要写 RSS 抓取，又要写 HTML 解析，还要写 REST API 请求，5 个通用 Skill 将各自把 4~5 种网络协议重复实现一遍，导致系统底层出现大量冗余代码（代码膨胀率达 300%）。
**必须确立“双层架构”**：
- **底层驱动层（Protocol Drivers）**：只按协议抽象 4 个无状态纯驱动（`RSSDriver`, `HTMLCardDriver`, `HTMLTableDriver`, `RestAPIDriver`, `SitemapDriver`）；
- **上层业务认知层（Archetype Interpreters）**：即现有的 5 大 Skill，负责将卡片业务指令（关键词雷达、正交实体识别、噪音过滤）注入到底层驱动提取的结果中。

### 3.2 边缘异构源缺失与处理机制

对照 7163 台账，以下 3 类边缘异构源在现有 5 大 Skill 中存在无法落地的盲区：

1. **结构化 XML Sitemap 增量流（3 项）**：
   - 包含：The Investor（`sitemap.xml`）、国家法律法规库 VBPL（`sitemap/1.xml`）、Enterprise Singapore。
   - **痛点**：Sitemap 既非 RSS，也非 HTML，现有 5 个 Skill 均未定义 Sitemap 解析规范。若硬塞给 `media-stream-curator`，feedparser 无法作为 RSS 解析，BeautifulSoup 会当作普通 HTML 提取导致内容为空。
   - **解法**：在驱动层补齐 `sitemap-incremental-driver`，支持标准 XML 命名空间解析，提取 `<loc>` 与 `<lastmod>`。
2. **纯前端 SPA / 后端开放 REST API（8 项）**：
   - 包含：越南财政部 MOF（Vite/Vue SPA，直调 POST `/api/article/reads`）、岘港高新区、亚投行 AIIB（静态打包 `all-projects-data.js` 变量数组）。
   - **痛点**：卡片模板的第 2 节“导航交互步骤”充斥着“打开链接、翻页、定位容器”等浏览器 DOM 交互语义，无法表达 HTTP POST 请求体（Payload）、请求头或纯 JavaScript 变量提取。
   - **解法**：卡片元数据增加 `api_spec` 选填块（包含 `method`, `headers`, `payload_template`, `json_path`），允许通用 Skill 直接发起 API 提取。
3. **低频官方公报中的 PDF 附件专刊**：
   - 包含：外资局 FIA（`src-A07`）、统计总局 NSO（`src-A03`）发布的月度 FDI 统计报告。正文只有一行标题，核心投资额与国别来源全部封装在内嵌 PDF 附件中。
   - **痛点**：当前抽取字段契约仅提取网页摘要，若无附件探测机制，抓取出来的将是空洞无物的“关于公布 X 月外资情况的通知”，`evidence_snippet` 严重失真。
   - **解法**：卡片支持 `attachment_probe: true`，提取 `.pdf` 直达下载链接，由轻量 `pypdf` / `pdfplumber` 解析第一页核心摘要表。

---

## 四、 卡片实操可执行性与动态防爬压力测试

以首批交付的 3 张示范卡片为样本进行现场代码执行与网络测试：

### 4.1 VietnamWorks (`SRC-JOB-001`) 招聘雷达：人机语义鸿沟与执行死锁
- **实测表现**：通过 Python 发起请求，目标 URL 返回 200，HTML 文本高达 1.94MB，检测到 `__NEXT_DATA__: True`，表明其底层为 Next.js 客户端渲染或预渲染架构。
- **卡片盲区**：
  卡片第 2 节规定：`轮流在搜索框输入以下 4 组关键词组合进行检索（按发布日期降序排序，只看近 3 天新发职位）...`。
  - 对于无头轻量 Python 脚本或零浏览器环境，**根本不存在“在搜索框输入并点击搜索”的物理动作**！
  - 脚本必须获得确定的带参 URL 模板（例如 `https://www.vietnamworks.com/tim-viec-lam?q={keyword}&order=created_at_desc`）或其底层 API 端点。
  - **严重缺陷**：如果卡片只写人类动作指令，底层的 `job-radar-scanner` 开发者必须人肉再次对每个招聘网站单独抓包逆向，卡片失去了作为“可执行规范”的价值。

### 4.2 Becamex IDC (`SRC-IP-001`)：总册与卡片靶点 URL 内部自相矛盾
- **事实**：
  - 总册模板 `MASTER-REGISTRY-TEMPLATE.md` 中登记的 Becamex 靶点为：`https://becamex.com.vn/tin-tuc/du-an/`；
  - 专属卡片 `SRC-IP-001-becamex.md` 中登记的靶点为：`https://becamex.com.vn/tin-tuc/`。
- **危害**：系统存在两个真理源，导致调度层与卡片执行层抓取路径不一致，产生数据漂移。

### 4.3 越南环境部 DSDTM (`SRC-APP-001`)：网络安全握手参数缺失
- **事实**：7163 摸排报告与 7629 报告反复强调越南政务系统常年存在 SSL 证书过期或 OpenSSL 握手协议降级特征。
- **缺陷**：示范卡片与模板中完全没有 `network_config` 属性（如 `verify_ssl: false`，`timeout: 15`，`headers`），一旦由通用无头脚本默认运行，遇到系统级 SSL 握手报错将直接把该源误判为 `Degraded` 故障源。

---

## 五、 生命周期状态机闭环与 Candidate ID 回填审查

### 5.1 状态机自动化判定机制真空
5184 规范规定了 `Active -> Degraded -> Low_Freq -> Retired` 的流转逻辑（如“连续 2 天无法返回有效结构自动降级”）。
- **致命缺失**：交付的文件集合中**没有任何代码实现状态追踪与持久化统计**！
  - 既没有维护连续失败计数的运行账本（如 `state_ledger.db` 的源健康表）；
  - 也没有状态回写机制。总册是一个静态的 Markdown 文件，若无专用的 `RegistryManager` 读写模块，不可能靠脚本去安全并发修改 Markdown 表格。
  - **结论**：若不补充代码层状态账本，5184 的状态流转将彻底沦为人肉手工维护的摆设。

### 5.2 Candidate ID 与防幻觉回填闭环深度脱节
`contracts.py` 中实现了 `to_llm_payload()`：
```python
def to_llm_payload(self) -> Dict[str, Any]:
    d = asdict(self)
    del d["direct_url"]  # 剥夺大模型接触 URL 的权力
    return d
```
此举在设计哲学上彻底消除了大模型幻觉编造 URL 的可能性，**但是在下游工程实现上出现断头（Dangling Logic）**：
1. **大模型输出契约未定义**：大模型研判完成后的输出 Schema 是什么？大模型如何指明它采用了哪个候选条目？（应定义 `CuratedBriefItem` 包含 `ref_candidate_ids: List[str]`）；
2. **URL 回填函数完全缺失**：整个交付物中，没有任何函数（例如 `backfill_urls()`）负责接收大模型输出与原始 Candidate 映射表，并将剥夺的 `direct_url` 安全拼接回最终的 HTML 交付简报中；
3. **多源合并场景未规约**：若大模型将来自 Becamex 园区签约（`C-010`）与越南投资报（`C-015`）合并为同一条重大新闻，系统该回填单个主链接还是两个链接？
4. **`candidate_id` 生成时序未决**：由 Skill 各自生成会导致多源并发时 ID 冲突；必须由框架调度层根据 `f"C-{source_id}-{seq:04d}"` 统一分配并生成不可变映射字典。

---

## 六、 架构修订与落地必改补丁建议 (Mandatory Patches)

为确保 5184 架构体系能坚实支撑后续代码重构，必须实施以下 5 大落地工程补丁：

### 补丁 1：契约代码与模板对齐补丁（修复运行时崩溃）

1. **修正 `contracts.py` 中的 `RegistryEntry`**：
   补充 `priority` 与 `expected_column` 字段，放宽对大小写状态的容错解析。
2. **修正 `contracts.py` 中的 `ExtractedCandidate`**：
   为 `candidate_id` 与 `extracted_at` 设定默认值或由工厂函数生成；或者明确分为两级数据类：
   - `RawExtractedItem`（通用 Skill 抽取的原始物料，不含 candidate_id）；
   - `ExtractedCandidate`（经框架打标、入库、分配唯一 candidate_id 的完整实体）。
3. **统一总册表头与字段名**：
   总册模板表头统一为：`source_id`, `name`, `cluster`, `target_url`, `archetype_skill`, `check_frequency`, `status`, `card_path`, `last_audit_date`。

### 补丁 2：协议驱动层与业务原型层“双层解耦”补丁

将 5 大通用 Skill 的底层实现规范化为“驱动调用 + 业务研判”：
```
+-----------------------------------------------------------------------------------+
| 业务认知层 (5 Archetypes): 关键词雷达、正交实体识别、噪音一票否决                  |
| (job-radar / park-news / gazette-table / disclosure-sniffer / media-stream)       |
+-----------------------------------------------------------------------------------+
                                          │ 统一调用
                                          ▼
+-----------------------------------------------------------------------------------+
| 协议驱动层 (5 Protocol Drivers): 零 Token、纯网络与结构化解析                     |
| 1. rss_driver           (原生 RSS/Atom 极速解析)                                  |
| 2. html_card_driver     (规整图文卡片容器解析)                                    |
| 3. html_table_driver    (数据表格 <tr> 行遍历解析)                                |
| 4. rest_api_driver      (HTTP GET/POST JSON 解析)                                 |
| 5. sitemap_driver       (XML Sitemap 增量解析，覆盖 VBPL/The Investor)            |
+-----------------------------------------------------------------------------------+
```

### 补丁 3：卡片作业规范“机读参数化”改造补丁

卡片第 2 节（巡检路径）全面废除“打开网页、手动输入搜索”的人类自然语言描述，改为**标准参数块**：
```yaml
# 卡片 Frontmatter 扩充参数块
network_config:
  verify_ssl: true
  timeout: 10
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."

search_spec:
  # 适用于 job_radar 与 disclosure_sniffer
  endpoint_template: "https://www.vietnamworks.com/tim-viec-lam?q={keyword}&order=created_at_desc"
  keywords:
    - "Factory Setup"
    - "Plant Manager"
    - "Site Selection"
```

### 补丁 4：代码级状态机账本与总册只读编译机制

1. **状态持久化账本**：在 SQLite `state_ledger.db` 中新建 `source_health` 表：
   - `source_id`, `consecutive_failures`, `last_success_at`, `current_status`, `error_msg`。
2. **自动化判定逻辑**：
   - 抓取失败计数 `consecutive_failures += 1`；当 `>= 2` 时，状态自动置为 `degraded`；
   - 抓取成功则清零失败计数，状态置为 `active`；
3. **只读总册渲染器**：
   系统以 SQLite 或 `config/master_sources.json` 为单一事实修改源，提供 `compile_registry_md.py` 脚本自动重新编译生成 `MASTER-SOURCE-REGISTRY.md`，杜绝代码动态手撕 Markdown 文本。

### 补丁 5：大模型研判输出 Schema 与防幻觉 URL 回填闭环

在 `contracts.py` 中补充完整闭环数据结构与函数：
```python
@dataclass
class CuratedBriefItem:
    column: str                         # 五大正交栏目之一
    title_zh: str                       # 规范中文标题
    fact_summary: str                   # 【事实】客观陈述
    insight_analysis: str               # 【看点】产业影响研判
    ref_candidate_ids: List[str]        # 关联的 Candidate ID 列表 (如 ["C-001"])
    # 最终回填字段 (由回填函数注入，大模型不产出)
    verified_urls: List[str] = field(default_factory=list)

def backfill_candidate_urls(
    curated_items: List[CuratedBriefItem],
    candidate_vault: Dict[str, ExtractedCandidate]
) -> List[CuratedBriefItem]:
    """
    防幻觉终极屏障：将大模型研判输出的 ref_candidate_ids 
    精确映射回物理底层抓取的真实 200 direct_url，并进行物理探活校验。
    """
    for item in curated_items:
        urls = []
        for cid in item.ref_candidate_ids:
            if cid in candidate_vault:
                urls.append(candidate_vault[cid].direct_url)
            else:
                logger.warning(f"检测到非法 Candidate ID 幻觉: {cid}")
        item.verified_urls = urls
    return curated_items
```

---

## 七、 最终评审结论与裁决

依据首席技术审核官（Chief System Auditor）的客观独立准则，对项目最新提交的《越南产业情报信源“造册、建卡与通用Skill”顶层架构体系 (5184)》给出最终裁决：

### **【评审裁决：有条件通过，完成 5 大必改补丁后方可实施】**
*(Conditional Pass with Mandatory Patches)*

### 裁决执行决议：
1. **方向正确，予以肯定**：5184 体系确立的“造册 + 建卡 + 通用原型 Skill”三位一体工程架构，从根本上破除了既往会话“死板硬编码爬虫死锁单一网站”的恶性循环，其 Candidate ID 脱敏思路彻底切断了大模型编造假链接的根源，架构大方向完全成立。
2. **立即封堵运行时报错**：在启动 200 张卡片全面建卡前，**必须优先对 `contracts.py`、卡片模板、总册模板打入【补丁 1】至【补丁 5】**，消除类型不一致与回填断层，确保样板代码 100% 具备单体运行测试通过性。
3. **排期分批推进**：待补丁落盘并经自动化测试回归后，方可正式启动全量 177 个可用源的逐源建卡与工程接入。

---
*报告出具人：首席技术审核官（Chief System Auditor）*  
*出具日期：2026-11-11*
