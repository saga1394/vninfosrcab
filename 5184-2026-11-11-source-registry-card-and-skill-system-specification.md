# 5184-2026-11-11 越南产业情报信源“造册、建卡与通用Skill”顶层架构设计与工程规范

> **【自启动提示词（新会话一键调用）】**  
> 请阅读并严格遵循信源管理与作业体系规范文档 `E:\geminiworks\vninfosrcab\5184-2026-11-11-source-registry-card-and-skill-system-specification.md`（引用码：**5184**）。  
> **核心目标**：彻底终结项目前期“说到哪里做哪里、抓取逻辑与特定网站死死绑定、缺乏规范化信源中枢”的混乱局面。正式确立**“1 个全景总册 + 5 大通用原型 Skill + 200 张专属作业指导卡”**的解耦工程架构。  
> **执行原则**：  
> 1. **双模兼容原则**：卡片与总册必须同时满足“机器零开销快速解析路由”与“AI 深度通读执行及人类清晰审阅”；  
> 2. **拒绝技能膨胀**：禁止为 200 个源编写 200 个独立代码脚本，必须抽象收敛为 5 大通用原型 Skill，卡片仅作为参数与语义指令挂载；  
> 3. **强类型接口契约**：总册、卡片、Skill 抽取输出至后续 AI 对账层，必须严格执行 `sources/interfaces/contracts.py` 中定义的强类型 Schema；  
> 4. **全生命周期闭环**：新源必须走“沙盒试探 -> 建卡入册 -> 常态轮巡 -> 异常降级 -> 退役归档”的规范流程，严禁随意临时硬编码。  
> 后续所有新信源录入、采集引擎重构与日常自动化巡查，必须无条件遵循本规范。

---

## 一、 系统架构愿景与破局点

在既往 17 个会话中，系统反复遭遇“38 源盲目萎缩”、“假链接死链横行”、“微商垃圾侵入”等挫败。其根源在于：**试图用一套通用的死板爬虫代码去强行适配全网形态迥异的 200 多个网站。**

实际上，全网信源的形态天差地别：
* 招聘网站是**动态职位流**（需搜寻“厂长/筹建负责人”等超前微信号）；
* 工业园区官网是**现场新闻卡片**（需盯紧“供地、奠基、签约”）；
* 政府审批部门是**复杂的 ASP.NET 数据表格**（需扒取环评 ĐTM、排污许可公文）；
* 境外交易所是**格式化的上市公司对外投资决议**。

**破局核心**：
将“信源管理”与“执行动作”彻底解耦：
1. **造册（Registry）**：作为调度总指挥表，集中管理全网 200+ 源的编号、大类、频次与健康状态；
2. **建卡（Cards）**：给每个源量身定制一张**专属作业指导书（Skill/Card）**，讲透它的版面怎么看、入口在哪里、抓什么核心信号；
3. **通用 Skill 矩阵**：底层只编写 **5 个通用的抓取与理解技能**，动态挂载 200 张卡片执行作业。

---

## 二、 总册架构与管理规范 (Master Source Registry)

总册存放在 `sources/MASTER-SOURCE-REGISTRY.md`，由调度引擎在每天清晨自动加载。

### 2.1 字段规范与强类型定义
| 字段键名 | 类型 | 说明与枚举约束 |
| :--- | :--- | :--- |
| `source_id` | String | 唯一信源编号，格式：`SRC-[JOB\|IP\|APP\|SEC\|MED]-[三位序号]` |
| `name` | String | 机构或媒体的标准官方中文/越文全称 |
| `cluster` | Enum | 五大业务大类：`job_radar` \| `industrial_park` \| `legal_approval` \| `corporate_disclosure` \| `media_fdi` |
| `target_url` | String | 精准监控的二级专版或直达频道 URL（严禁填粗糙首页） |
| `archetype_skill`| Enum | 绑定的底层通用技能：`job-radar-scanner` \| `park-news-inspector` \| `gazette-table-parser` \| `disclosure-sniffer` \| `media-stream-curator` |
| `check_frequency`| Enum | 巡检频次：`daily`（每日）\| `weekly`（低频周巡） |
| `status` | Enum | 运行状态：`Active`（正常）\| `Degraded`（异常降级）\| `Low_Freq`（低频）\| `Retired`（退役） |
| `card_path` | String | 专属作业卡相对路径，如 `sources/cards/SRC-JOB-001-vietnamworks.md` |
| `last_audit_date`| String | 最近一次实测审计日期（`YYYY-MM-DD`） |

---

## 三、 卡片架构与规范 (Source Operational Card)

卡片存放在 `sources/cards/` 目录下，文件命名遵循 `SRC-[大类]-[序号]-[英文简写].md`。

### 3.1 双模兼容规范（Machine-Parsable + Human/Agent-Readable）
卡片必须严格采用 **头部 YAML 元数据 + 正文语义指导规范**：

```markdown
---
source_id: SRC-JOB-001
name: VietnamWorks 越南高端招聘雷达
cluster: job_radar
target_url: https://www.vietnamworks.com/tim-viec-lam
archetype_skill: job-radar-scanner
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: 2026-11-11
---

# 信源作业指导卡：[官方全称] ([编号])

## 1. 信源定位与情报价值
- 机构属性、在产业链所处阶段、核心前瞻/公文价值。

## 2. 页面布局与巡检路径
- 精准入口 URL；
- 版面交互步骤（搜索参数、分页范围、卡片容器位置）。

## 3. 核心信号捕捉规则
- 必抓关键词组与投资动作特征（奠基、供地、选址筹备、环评批复等）；
- 涉及的关键产业领域（半导体、液冷散热、光伏电池、汽车等）。

## 4. 抽取字段契约
- 严格遵循 `ExtractedCandidate` 结构规范输出字段。

## 5. 噪声屏蔽与跳过准则
- 明确列出该网站特有的干扰项（如无关社会新闻、代招中介、老厂日常流水线普工招聘），一票否决。

## 6. 异常与改版判定
- 明确何种情况判定为改版或阻断（404/500/Cloudflare/列表为空），自动上报 `Degraded`。
```

---

## 四、 5 大通用原型技能体系 (Archetype Skills)

系统坚决不编写 200 个散碎脚本，统一抽象收口为以下 5 个通用技能：

```
+-----------------------------------------------------------------------------------+
| 1. job-radar-scanner (招聘前瞻雷达技能)                                            |
|    - 行为特征: 接收搜索词组，检索招聘流，解析岗位职责，挖掘新设法人、选址地块与建厂规模。 |
+-----------------------------------------------------------------------------------+
| 2. park-news-inspector (工业园区现场技能)                                         |
|    - 行为特征: 解析园区卡片列表，定向匹配供地、开工、厂房交付动向，提取租地面积与签约方。|
+-----------------------------------------------------------------------------------+
| 3. gazette-table-parser (法定公文表格技能)                                        |
|    - 行为特征: 遍历行政公文数据表格，解析环评/排污批文，提取建设主体、产品产能与文号。    |
+-----------------------------------------------------------------------------------+
| 4. disclosure-sniffer (境外母公司信披技能)                                        |
|    - 行为特征: 检索上市公司公告系统，提取对越投资、设立境外孙公司、增资决议公告及金额。    |
+-----------------------------------------------------------------------------------+
| 5. media-stream-curator (主流财经专版技能)                                        |
|    - 行为特征: RSS 快速抓取或图文专栏解析，广谱兜底获取全网重大经济动向与政策调整。       |
+-----------------------------------------------------------------------------------+
```

---

## 五、 接口契约与数据流定义 (Contracts & Data Flow)

所有模块间的数据交互全部受控于强类型契约 `sources/interfaces/contracts.py`：

```
[总册: RegistryEntry]
       │
       ▼ (分派活跃源)
[卡片: SourceCard] ──注入参数──> [通用 Skill: ArchetypeSkill]
                                        │
                                        ▼ (提取候选条目)
                               [ExtractedCandidate]
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                 [安全脱敏 Payload]              [物理映射底账]
             (去除去除 direct_url,             (保留 direct_url 与真实引用,
              仅保留 Candidate_ID)             供最终交付回填，杜绝幻觉)
                         │                             │
                         ▼                             │
               [大模型认知研判与对账]                    │
             (查历史库合并同类项、串接脉络)                 │
                         │                             │
                         └──────────────┬──────────────┘
                                        │
                                        ▼ (安全回填真实链接)
                              [最终交付 Brief & 入库]
```

---

## 六、 信源全生命周期管理 SOP (Lifecycle Governance)

为保持 200+ 信源的长期鲜活，必须执行以下动态进出规则：

1. **新源准入 (Intake)**：
   * 发现新信源后，必须先由人工或 Agent 进行 1 次单点沙盒实测；
   * 依照 `SOURCE-CARD-TEMPLATE.md` 编制新卡片；
   * 在 `MASTER-SOURCE-REGISTRY.md` 登记一行，标记为 `Active`。
2. **日常巡查与健康度降级 (Degradation)**：
   * 若某源连续 2 天无法返回有效结构或触发 403/404，状态自动切换为 **`Degraded`**，系统发出运维告警，暂停每日扫描；
   * Agent 或维护人员根据报错更新其卡片中的选择器或 URL 端点后，恢复 `Active`。
3. **低频调适 (Low Frequency)**：
   * 某些高价值但低频发布的源（如投资局月报），标记为 **`Low_Freq`**，由每日轮巡降为每周日轮巡。
4. **淘汰退役 (Retirement)**：
   * 确认永久关停或失去跟踪价值的源，标记为 **`Retired`**，从日常扫描彻底移除，卡片归入 `archive/` 备查。

---

## 七、 实施交付资产对照表

本项目已在 `sources/` 目录下完成全套样板与规范的物理落盘：
1. **空总册样板**：[`sources/templates/MASTER-REGISTRY-TEMPLATE.md`](file:///E:/geminiworks/vninfosrcab/sources/templates/MASTER-REGISTRY-TEMPLATE.md)
2. **空卡片样板**：[`sources/templates/SOURCE-CARD-TEMPLATE.md`](file:///E:/geminiworks/vninfosrcab/sources/templates/SOURCE-CARD-TEMPLATE.md)
3. **第一批典型样板卡**：
   * 招聘类：[`sources/cards/SRC-JOB-001-vietnamworks.md`](file:///E:/geminiworks/vninfosrcab/sources/cards/SRC-JOB-001-vietnamworks.md)
   * 园区类：[`sources/cards/SRC-IP-001-becamex.md`](file:///E:/geminiworks/vninfosrcab/sources/cards/SRC-IP-001-becamex.md)
   * 公文类：[`sources/cards/SRC-APP-001-dsdtm.md`](file:///E:/geminiworks/vninfosrcab/sources/cards/SRC-APP-001-dsdtm.md)
4. **Skill 体系规范与样板**：
   * [`sources/skills/ARCHETYPE-SKILLS-SPEC.md`](file:///E:/geminiworks/vninfosrcab/sources/skills/ARCHETYPE-SKILLS-SPEC.md)
   * [`sources/skills/templates/ARCHETYPE-SKILL-TEMPLATE.md`](file:///E:/geminiworks/vninfosrcab/sources/skills/templates/ARCHETYPE-SKILL-TEMPLATE.md)
5. **强类型接口契约代码**：
   * [`sources/interfaces/contracts.py`](file:///E:/geminiworks/vninfosrcab/sources/interfaces/contracts.py)
