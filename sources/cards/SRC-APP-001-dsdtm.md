---
source_id: SRC-APP-001
name: 越南国家环境影响评价 (ĐTM) 法定公众征询公示平台
cluster: legal_approval
target_url: https://thamvan.mae.gov.vn/Home/DSDTM
archetype_skill: gazette-table-parser
protocol_driver: html_table_driver
check_frequency: daily
priority: P0
expected_column: legal_approval
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: false              # 越南环境部政务网常存在 SSL 证书链缺失，必须关闭强校验避免误判宕机
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

attachment_probe: true           # 开启环评报告 PDF/DOCX 附件直达链接探针提取
---

# 信源作业指导卡：越南国家环境影响评价 (ĐTM) 法定公众征询公示平台 (SRC-APP-001)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南环境管理法定机关（Bộ Nông nghiệp và Môi trường / 原自然资源与环境部 MONRE）。
* **情报定位**：**全网最硬核的重资产工业投资落地法定铁证**。任何重大工业实体开工前必须完成 15 天环评报告书（ĐTM）公示。
* **价值等级**：P0 级法定硬证据基石源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://thamvan.mae.gov.vn/Home/DSDTM`
* **底层驱动与容器描述**：
  * **驱动类型**：`html_table_driver`（须读取 `network_config.verify_ssl=false` 绕过部委级证书异常）。
  * **表格遍历特征**：定位 ASP.NET 主体 `<table class="table">` 中的 `<tbody><tr>` 行，抓取第 1 页最新 15~20 行。
  * **字段列映射**：项目名称（Tên dự án）、建设单位（Chủ dự án）、所在地（Địa điểm）、公示起止日期（Thời gian tham vấn）、详情与报告下载链接（`<a href="/Home/ChiTietDSDTM?id=...">` 及附件 `.pdf`）。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
`gazette-table-parser` 通读项目名称与建设单位：
* **必须收录的行业特征**：
  * 制造业：电子元器件、芯片半导体封装、动力电池、服务器液冷机箱、精密注塑、新材料；
  * 重点园区基建：工业区集中污水处理厂扩容、高标保税冷链物流仓储。
* **时间过滤**：检查 `Thời gian tham vấn` 起始日期，只取近 72 小时新登载公示。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-APP-001",
  "title": "Tham vấn ĐTM: Dự án Nhà máy sản xuất linh kiện bán dẫn Amkor Technology Việt Nam (Giai đoạn 2)",
  "pub_date_raw": "2026-11-10",
  "subject_entity": "Amkor Technology / 安靠科技",
  "geo_location": "Bắc Ninh (北宁省) / KCN Yên Phong II-C",
  "signal_type": "eia_approval",
  "project_scale": "5.4 亿美元, 23 ha",
  "evidence_snippet": "Báo cáo ĐTM dự án mở rộng nhà máy sản xuất và lắp ráp linh kiện bán dẫn công suất 1.2 tỷ sản phẩm/năm tại KCN Yên Phong II-C.",
  "direct_url": "https://thamvan.mae.gov.vn/Home/ChiTietDSDTM?id=98765",
  "attachment_urls": [
    "https://thamvan.mae.gov.vn/Uploads/DTM/amkor_phase2_dtm.pdf"
  ]
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 纯乡村农业水利灌溉排涝工程；
* 县级普通生活垃圾转运站；
* 乡村小型公墓、地方学校教学楼等非涉工基建项目。

## 6. 异常与改版判定 (Health & Failure Detection)
* `<table>` 元素缺失或提示 SQL Server 数据库异常；
* 返回 HTTP 500 / 404（注意：SSL 报错已由 `verify_ssl: false` 屏蔽，不再误判为故障）。
