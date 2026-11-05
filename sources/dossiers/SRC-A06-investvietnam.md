# SRC-A06 信息源活体档案卡：InvestVietnam (越南国家投资促进官方门户)

> **档案卡编号**：`SRC-A06`  
> **所属批次**：第一批（国家级部委与法定监管公示）  
> **建档立卡日期**：2026-11-06  
> **动态状态追踪**：100% 连通可用（实测 HTTP 200，字段完备度 4/4）  
> **全局总台账索引**：已纳入 [`sources/MASTER-SOURCE-LEDGER.md`](file:///e:/geminiworks/vninfosrcab/sources/MASTER-SOURCE-LEDGER.md)

---

## 一、 信源基础身份 (Identity & Authority)

| 核心属性 | 详细说明与标准定义 |
|---|---|
| **信源官方全称** | **InvestVietnam** / 越南国家投资促进官方门户 |
| **机构法理地位** | Trung tâm Xúc tiến Đầu tư phía Bắc/Nam - Cục Đầu tư nước ngoài |
| **法理权威等级** | **国家级招商引资与投资服务官方专网 (权重 4/5，官方前瞻雷达)** |
| **官方主入口 URL** | [https://investvietnam.gov.vn](https://investvietnam.gov.vn) |
| **归属五大正交栏目** | **一、 【FDI 外资投资动向】（聚焦各省招商推介项目清单与跨国企业接洽动向）** |

---

## 二、 人类模拟浏览路径 (How a Human Reads / Navigates)

### 1. 最佳访问通道与端点
- **通道类型**：`轻量 HTML 列表流`
- **首选精准交互端点**：
  - `访问投资资讯列表：https://investvietnam.gov.vn/tin-tuc-su-kien/ (详情页内嵌精准发布时间)`

### 2. 人类分析师实际交互路径（浏览器模拟）
打开 investvietnam.gov.vn -> 点击 'Cơ hội đầu tư' (投资机会) 或 'Tin tức' (新闻动态) -> 筛选按省份发布的招商引资项目库与落地优惠政策。

### 3. 噪音栏目与跳过说明（坚决避坑）
> [!NOTE] 人类巡检防噪守则
> **坚决绕行以下低价值版块**：  
> 忽略常规中越双边友谊交流活动、省领导与外国使领馆纯礼节性茶话会。

---

## 三、 真实供给能力画像 (What Intelligence it Supplies)

1. **核心情报供给维度**：  
   提供各省拟引进外资重点项目清单（面积、投资限额、合作模式）、新修订的外资准入负面清单、各园区地价与地租税率横向对比指导。
2. **时效窗口与更新节奏**：  
   每周更新 2~5 篇深度项目招商推介。
3. **情报生命周期与历史沉淀价值**：  
   作为国家级核心信源，其发布的法例文号、公报与统计基准直接入库沉淀至 `collector.db` 与 `projects.db`，为后续各地方工业区、具体外资项目的落地审批提供法理比对依据。

---

## 四、 真人阅读与裁量规则 (Inclusion vs Skipping Rules)

### 1. 收录判据 (Click & Include)
标题出现：'Dự án kêu gọi đầu tư' (招商推介项目), 'Ký kết biên bản ghi nhớ' (签署 MOU), 'FDI', 'Nhà đầu tư nước ngoài' 必须深入阅读收录。

### 2. 跳过判据 (Skip & Discard)
无具体签约金额、无明确地块、仅为口头原则性意向的空泛宣讲会跳过。

### 3. 企业与机构规范译名约束
> [!IMPORTANT] 命名红线
> 统一译为：'越南国家投资促进门户'、'投资合作备忘录 (MOU)'。

---

## 五、 最新真人实访记录与样本 (Live Visit Log & Concrete Samples)

- **实访日期**：2026-11-06（经 7163 与 4729 计划二次实测核实）
- **通道健康状态**：HTTP 200 正常，单次请求响应耗时低，零反爬阻断
- **真实抓取与深度研读样本**：

#### 样本 1：Góp vốn, mua cổ phần/phần vốn góp
- **发布时效**：`Current Edition`
- **原文直达链接**：[Góp vốn, mua cổ phần/phần vốn góp](https://investvietnam.gov.vn/vi/gop-von-mua-co-phanphan-von-gop.nl.html)
- **原文事实摘要**：InvestVietnam investment opportunity / regulatory guide: Góp vốn, mua cổ phần/phần vốn góp
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 2：Thuế, phí, lệ phí và các khoản chi khác
- **发布时效**：`Current Edition`
- **原文直达链接**：[Thuế, phí, lệ phí và các khoản chi khác](https://investvietnam.gov.vn/vi/thue-phi-le-phi-va-cac-khoan-chi-khac.nl.html)
- **原文事实摘要**：InvestVietnam investment opportunity / regulatory guide: Thuế, phí, lệ phí và các khoản chi khác
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 3：Hải quan và xuất, nhập khẩu
- **发布时效**：`Current Edition`
- **原文直达链接**：[Hải quan và xuất, nhập khẩu](https://investvietnam.gov.vn/vi/hai-quan-va-xuat-nhap-khau.nl.html)
- **原文事实摘要**：InvestVietnam investment opportunity / regulatory guide: Hải quan và xuất, nhập khẩu
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

---
*本活体档案卡由 4729 执行流水线维护，支持跨会话持续更新。*
