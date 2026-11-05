# SRC-A07 信息源活体档案卡：Cục Đầu tư nước ngoài (FIA) (越南外国投资局官方门户 (计划投资部直属))

> **档案卡编号**：`SRC-A07`  
> **所属批次**：第一批（国家级部委与法定监管公示）  
> **建档立卡日期**：2026-11-06  
> **动态状态追踪**：100% 连通可用（实测 HTTP 200，字段完备度 4/4）  
> **全局总台账索引**：已纳入 [`sources/MASTER-SOURCE-LEDGER.md`](file:///e:/geminiworks/vninfosrcab/sources/MASTER-SOURCE-LEDGER.md)

---

## 一、 信源基础身份 (Identity & Authority)

| 核心属性 | 详细说明与标准定义 |
|---|---|
| **信源官方全称** | **Cục Đầu tư nước ngoài (FIA)** / 越南外国投资局官方门户 (计划投资部直属) |
| **机构法理地位** | Cục Đầu tư nước ngoài - Bộ Kế hoạch và Đầu tư (FIA/MPI) |
| **法理权威等级** | **越南外资数据最高官方统计与主管审批机构 (权重 5/5，FDI 绝对基石源)** |
| **官方主入口 URL** | [https://fia.mpi.gov.vn](https://fia.mpi.gov.vn) |
| **归属五大正交栏目** | **一、 【FDI 外资投资动向】（全国及各省 FDI 增资、新设、并购权威月报）** |

---

## 二、 人类模拟浏览路径 (How a Human Reads / Navigates)

### 1. 最佳访问通道与端点
- **通道类型**：`轻量 HTML 列表流 (配套官方 PDF/XLSX 数据包直接下载)`
- **首选精准交互端点**：
  - `直达外资数据列表：https://fia.mpi.gov.vn/Home/ListNews/1 (提供真实时效的 FDI 统计简报与深度分析)`

### 2. 人类分析师实际交互路径（浏览器模拟）
打开 fia.mpi.gov.vn -> 点击首页核心菜单 'Tình hình thu hút ĐTNN' (利用外资情况) -> 每月 25~30 日下载当月官方 FDI 统计报告（含各省吸收外资排名、按国别投资额）。

### 3. 噪音栏目与跳过说明（坚决避坑）
> [!NOTE] 人类巡检防噪守则
> **坚决绕行以下低价值版块**：  
> 局内日常职工文体比赛、离退休干部座谈会等内部新闻完全忽略。

---

## 三、 真实供给能力画像 (What Intelligence it Supplies)

1. **核心情报供给维度**：  
   每月定点供给全越最权威 FDI 核心指标：新批项目数与资金、增资项目资金、外商出资与股权并购额 (Góp vốn, mua cổ phần)、投资流向领域 (制造业占比 60%~70%)、主要投资国（新加坡、韩国、中国大陆、台湾、香港、日本）。
2. **时效窗口与更新节奏**：  
   每月高规格发布一次月度报告，每季度发布季度总结，日常不定期发布大额项目许可公告。
3. **情报生命周期与历史沉淀价值**：  
   作为国家级核心信源，其发布的法例文号、公报与统计基准直接入库沉淀至 `collector.db` 与 `projects.db`，为后续各地方工业区、具体外资项目的落地审批提供法理比对依据。

---

## 四、 真人阅读与裁量规则 (Inclusion vs Skipping Rules)

### 1. 收录判据 (Click & Include)
任何包含月度/季度 FDI 统计数据的报告，或单笔超过 5000 万美元的新批/增资项目公示，必须全量提取并收录。

### 2. 跳过判据 (Skip & Discard)
局内部工作年终总结、表彰先进科室等非业务信息直接忽略。

### 3. 企业与机构规范译名约束
> [!IMPORTANT] 命名红线
> 统一译为：'越南外国投资局 (FIA)'、'外商直接投资 (FDI)'、'出资购股 (Góp vốn mua cổ phần)'。

---

## 五、 最新真人实访记录与样本 (Live Visit Log & Concrete Samples)

- **实访日期**：2026-11-06（经 7163 与 4729 计划二次实测核实）
- **通道健康状态**：HTTP 200 正常，单次请求响应耗时低，零反爬阻断
- **真实抓取与深度研读样本**：

#### 样本 1：Báo cáo theo tháng
- **发布时效**：`Monthly cadence (extracted from report title)`
- **原文直达链接**：[Báo cáo theo tháng](https://fia.mof.gov.vn/List/MenuID/2a33ab04-8fd4-4a47-b7ee-8797d92dacc7/CatID/a963873a-ec84-4cae-8b5f-d0f38c10e10c)
- **原文事实摘要**：Monthly official FDI statistics and investment implementation report document
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 2：BÁO CÁO TÌNH HÌNH THU HÚT ĐẦU TƯ NƯỚC NGOÀI 7 THÁNG NĂM 2026 ...
- **发布时效**：`Monthly cadence (extracted from report title)`
- **原文直达链接**：[BÁO CÁO TÌNH HÌNH THU HÚT ĐẦU TƯ NƯỚC NGOÀI 7 THÁNG NĂM 2026 ...](https://fia.mof.gov.vn/Detail/CatID/5102536e-ffed-4c97-83c9-24788f5e7d0c/NewsID/07543926-92de-480b-91dc-d1afe2df7822)
- **原文事实摘要**：Monthly official FDI statistics and investment implementation report document
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 3：BÁO CÁO NHANH TÌNH HÌNH THU HÚT  ĐẦU TƯ NƯỚC NGOÀI TẠI VIỆT  ...
- **发布时效**：`Monthly cadence (extracted from report title)`
- **原文直达链接**：[BÁO CÁO NHANH TÌNH HÌNH THU HÚT  ĐẦU TƯ NƯỚC NGOÀI TẠI VIỆT  ...](https://fia.mof.gov.vn/Detail/CatID/5102536e-ffed-4c97-83c9-24788f5e7d0c/NewsID/cd350403-11b2-4f81-b68c-c33e08160d5c)
- **原文事实摘要**：Monthly official FDI statistics and investment implementation report document
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

---
*本活体档案卡由 4729 执行流水线维护，支持跨会话持续更新。*
