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
  verify_ssl: false              # 越南环境部政务网 SSL 证书链常缺失，必须置为 false
  timeout: 20
  resolve_ip: "103.9.85.148"     # 绕过双 IP 轮询故障节点 (103.9.85.134)
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

attachment_probe: true           # 开启环评报告 PDF 首页摘要探针
---

# 信源作业指导卡：越南国家环境影响评价 (ĐTM) 法定公众征询公示平台 (SRC-APP-001)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南农业与环境部（MAE / 原 MONRE）法定公示平台。
* **情报定位**：全网最硬核的重资产工业投资落地法定铁证，记录开工前 15 天环评报告书（ĐTM）公示。
* **价值等级**：P0 级法定硬证据基石源。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://thamvan.mae.gov.vn/Home/DSDTM`
* **底层驱动与容器描述**：
  * **驱动类型**：`html_table_driver`（`verify_ssl: false` 屏蔽证书告警，遍历 ASP.NET `<table><tbody><tr>`）。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 收录制造业新建/扩产、半导体封装、动力电池、服务器液冷、集中污水处理及高标冷链仓储环评公示。

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
* 乡村农业水利灌溉工程、县级生活垃圾转运站、小型公墓及地方教学楼基建。

## 6. 异常与改版判定 (Health & Failure Detection)
* `<table>` 元素缺失或返回 HTTP 500 / 404。
