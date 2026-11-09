# SRC-A10 信息源活体档案卡：Tham vấn Giấy phép môi trường (Environmental Permit) (越南国家排污许可证 (GPMT) 法定核发公示平台)

> **档案卡编号**：`SRC-A10`  
> **所属批次**：第一批（国家级部委与法定监管公示）  
> **建档立卡日期**：2026-11-06  
> **动态状态追踪**：100% 连通可用（实测 HTTP 200，字段完备度 4/4）  
> **全局总台账索引**：已纳入 [`sources/MASTER-SOURCE-LEDGER.md`](file:///e:/geminiworks/vninfosrcab/sources/MASTER-SOURCE-LEDGER.md)

---

## 一、 信源基础身份 (Identity & Authority)

| 核心属性 | 详细说明与标准定义 |
|---|---|
| **信源官方全称** | **Tham vấn Giấy phép môi trường (Environmental Permit)** / 越南国家排污许可证 (GPMT) 法定核发公示平台 |
| **机构法理地位** | Bộ Nông nghiệp và Môi trường (MAE) |
| **法理权威等级** | **国家环境保护法法定工业项目投产试运行前置许可公示 (权重 5/5)** |
| **官方主入口 URL** | [https://thamvan.mae.gov.vn/Home/DSGiayPhep](https://thamvan.mae.gov.vn/Home/DSGiayPhep) |
| **归属五大正交栏目** | **四、 【行政审批与法定公示】（标志工厂建设完毕、即将正式点火/带料试生产）** |

---

## 二、 人类模拟浏览路径 (How a Human Reads / Navigates)

### 1. 最佳访问通道与端点
- **通道类型**：`规整政务 HTML 结构化表格`
- **首选精准交互端点**：
  - `直达公开公示表格：https://thamvan.mae.gov.vn/Home/DSGiayPhep`

### 2. 人类分析师实际交互路径（浏览器模拟）
访问 thamvan.mae.gov.vn/Home/DSGiayPhep -> 查阅最新的 'Tham vấn cấp Giấy phép môi trường' (排污许可证申领公示) -> 提取申请单位、工厂物理地址与排污许可范围。

### 3. 噪音栏目与跳过说明（坚决避坑）
> [!NOTE] 人类巡检防噪守则
> **坚决绕行以下低价值版块**：  
> 无商业或生活娱乐噪音，全为法定合规申报记录。

---

## 三、 真实供给能力画像 (What Intelligence it Supplies)

1. **核心情报供给维度**：  
   工厂进入点火试生产阶段的确定性物理信号！表明厂房土建已完工、机电设备已安装调试，向环境部申请排污许可证以进入商业化量产。提供精确的工业园区地块号与投产产能。
2. **时效窗口与更新节奏**：  
   工作日持续更新，日均新增 1~3 项国家级重点排污许可申请。
3. **情报生命周期与历史沉淀价值**：  
   作为国家级核心信源，其发布的法例文号、公报与统计基准直接入库沉淀至 `collector.db` 与 `projects.db`，为后续各地方工业区、具体外资项目的落地审批提供法理比对依据。

---

## 四、 真人阅读与裁量规则 (Inclusion vs Skipping Rules)

### 1. 收录判据 (Click & Include)
属于高科技制造、重工业、精细化工、大型数据中心或热电联产项目，必须收录，作为项目生命周期由'在建'迈向'投产'的核心里程碑！

### 2. 跳过判据 (Skip & Discard)
医院普通污水处理设施、居民区污水管网接入等非工业涉企事项跳过。

### 3. 企业与机构规范译名约束
> [!IMPORTANT] 命名红线
> 统一规范译名：'环境许可证 (Giấy phép môi trường - GPMT)'、'试运行许可'。

---

## 五、 最新真人实访记录与样本 (Live Visit Log & Concrete Samples)

- **实访日期**：2026-11-06（经 7163 与 4729 计划二次实测核实）
- **通道健康状态**：HTTP 200 正常，单次请求响应耗时低，零反爬阻断
- **真实抓取与深度研读样本**：

#### 样本 1：Nhà máy sản xuất thép thành phẩm
- **发布时效**：`29-10-2026`
- **原文直达链接**：[Nhà máy sản xuất thép thành phẩm](https://thamvan.mae.gov.vn/XemChiTiet/XemChiTietDuAn?id=6417)
- **原文事实摘要**：Chủ dự án: Công ty Cổ phần Vinausteel | Địa điểm: Lô CN2.8, Cụm công nghiệp Đặng Lễ, xã Nguyễn Trãi, tỉnh Hưng Yên | Thời gian còn lại: 11 ngày
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 2：Dự án đầu tư xây dựng Nhà máy giấy Kraft
- **发布时效**：`29-10-2026`
- **原文直达链接**：[Dự án đầu tư xây dựng Nhà máy giấy Kraft](https://thamvan.mae.gov.vn/XemChiTiet/XemChiTietDuAn?id=6418)
- **原文事实摘要**：Chủ dự án: Công ty Cổ phần Giấy Đồng Phát ECO | Địa điểm: Thửa CN-2.3, Lô CN-2, Cụm công nghiệp Kim Thái, xã Vụ Bản, tỉnh Ninh Bình | Thời gian còn lại: 11 ngày
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

#### 样本 3：Nhà máy giấy bao gói thực phẩm, giấy in nhiệt
- **发布时效**：`28-10-2026`
- **原文直达链接**：[Nhà máy giấy bao gói thực phẩm, giấy in nhiệt](https://thamvan.mae.gov.vn/XemChiTiet/XemChiTietDuAn?id=6419)
- **原文事实摘要**：Chủ dự án: Công ty TNHH Đầu tư Linh Giang | Địa điểm: Xóm Đắc Phú, xã Đồng Thịnh, tỉnh Ninh Bình | Thời gian còn lại: 10 ngày
- **分析师看点提炼**：该条情报直接反映国家主管机构最新法治或经济调节动向，具备直接传导效应，无娱乐或水文噪音，符合五大栏目纯净入库标准。

---
*本活体档案卡由 4729 执行流水线维护，支持跨会话持续更新。*
