# 5 大业务技能与 5 大底层驱动双层解耦规范 (Two-Layer Skill & Driver Architecture)

> **版本**：v1.1.0（已合入 8492 QA 审查“双层解耦”补丁）  
> **核心原则**：彻底解除业务语义与网络协议的耦合（消除 5×5=25 倍的代码重复），系统收敛为**“5 大上层业务原型认知技能 + 5 大底层无状态协议驱动”**。

---

## 一、 双层解耦架构全景图

```
+-----------------------------------------------------------------------------------+
| 上层：业务认知层 (5 Archetype Cognitive Skills) —— 负责“懂业务、知深浅、滤噪音”     |
|  1. job-radar-scanner       (招聘前瞻信号识别，提取筹建高管与园区线索)             |
|  2. park-news-inspector     (园区招商动态识别，提取供地面积、奠基、签约实体)        |
|  3. gazette-table-parser    (法定公文批复识别，过滤乡村基建、提炼制造业环评产能)    |
|  4. disclosure-sniffer      (上市公司对外投资决议，提炼出海母公司、金额与子公司)    |
|  5. media-stream-curator    (财经专版高召回提纯，捕获宏观税制、产业趋势与并购传闻)  |
+-----------------------------------------------------------------------------------+
                                          │ 统一调用协议路由 (依卡片 protocol_driver)
                                          ▼
+-----------------------------------------------------------------------------------+
| 下层：物理协议驱动层 (5 Protocol Drivers) —— 负责“网络握手、SSL容错、结构化读取”  |
|  1. rss_driver              (原生 RSS/Atom 秒级流式解析，优先用于 44 个 RSS 源)     |
|  2. html_card_driver        (通用图文卡片 & Next.js `__NEXT_DATA__` 抽取，含参数化URL) |
|  3. html_table_driver       (规整 HTML / ASP.NET `<tr>` 表格行遍历解析)             |
|  4. rest_api_driver         (HTTP GET/POST REST API、SPA 后端接口及静态 JS 数组抽取)|
|  5. sitemap_driver          (XML Sitemap 增量 `<loc>`/`<lastmod>` 解析，覆盖 VBPL 等)|
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼ (若卡片设置 attachment_probe: true)
+-----------------------------------------------------------------------------------+
| 公共增强器：PDF 公报附件文本探针 (Attachment PDF Probe)                             |
|  - 针对统计总局 (NSO)、外资局 (FIA)、环评全本，提取内嵌 PDF 链接并解析首页摘要表。 |
+-----------------------------------------------------------------------------------+
```

---

## 二、 边缘异构源的 100% 包容机制

对照全网 196 个源的摸排总台账（7163），双层架构完美覆盖了既往存在盲区的 3 类边缘源：

1. **XML Sitemap 增量流（3 项）**：
   * 涵盖 `The Investor`、国家法律法规库 `VBPL`（`sitemap/1.xml`）、`Enterprise Singapore`；
   * 卡片设置 `protocol_driver: sitemap_driver`，由底层 `sitemap_driver` 自动解构命名空间并筛选近 72 小时的 `<lastmod>` 增量 URL。
2. **纯前端 SPA / 后端开放 REST API（8 项）**：
   * 涵盖越南财政部 `MOF`（Vue SPA 后端 POST `/api/article/reads`）、岘港高新区、亚投行 `AIIB`；
   * 卡片配置 `protocol_driver: rest_api_driver` 并注入 `api_spec`（`method`, `payload_template`, `json_path`），直接零浏览器消耗拿下结构化 JSON。
3. **带参动态搜索门户（如招聘平台 Next.js 应用）**：
   * 卡片配置 `search_spec.endpoint_template` 与 `keywords` 阵列，驱动层直接构造完整带参请求或提取 `__NEXT_DATA__` 树，消灭人机交互鸿沟。
4. **官方月报/批文 PDF 附件**：
   * 卡片配置 `attachment_probe: true`，驱动在抓取表格或详情页的同时自动收集 `.pdf` 直链，通过轻量 `pypdf` 抽取核心统计指标并填入 `evidence_snippet` 与 `attachment_urls`。
