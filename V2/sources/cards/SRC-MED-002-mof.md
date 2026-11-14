---
source_id: SRC-MED-002
name: Bộ Tài chính 越南财政部官方门户 (SPA REST API)
cluster: media_fdi
target_url: https://www.mof.gov.vn/api/article/reads?offset=0&limit=20
archetype_skill: media-stream-curator
protocol_driver: rest_api_driver
check_frequency: daily
priority: P0
expected_column: macro_policy
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

api_spec:
  method: POST
  headers:
    Accept: "application/json"
  payload_template: {}
  json_path: "data"
  detail_url_template: "https://www.mof.gov.vn/chi-tiet-tin/{slug}"

attachment_probe: false
---

# 信源作业指导卡：Bộ Tài chính 越南财政部官方门户 (SRC-MED-002)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **机构/媒体法理属性**：越南财政部（主管税收、海关、企业所得税与土地出让金中央部委）。
* **情报定位**：直接绕过 Vue SPA 前端渲染，直调后台 JSON REST 接口获取减税、全球最低税（Pillar Two）及海关监管新规。
* **价值等级**：P0 级财政税制核心源（补丁 2 边缘 SPA/API 示范卡）。

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www.mof.gov.vn/api/article/reads?offset=0&limit=20`
* **底层驱动与容器描述**：`rest_api_driver` 读取 `api_spec`，按 `json_path: "data"` 提取文章数组。

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 捕获 `thuế thu nhập doanh nghiệp`、`thuế tối thiểu toàn cầu`、`hoàn thuế GTGT`、`tiền thuê đất`、`hải quan`。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-MED-002",
  "title": "Quy định chi tiết về giảm thuế thu nhập doanh nghiệp theo Nghị quyết 43/2026/QH16",
  "pub_date_raw": "2026-11-10",
  "subject_entity": "Bộ Tài chính (越南财政部)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "Nghị định 398/2026/NĐ-CP quy định chi tiết giảm thuế thu nhập doanh nghiệp cho các dự án đầu tư mới.",
  "direct_url": "https://www.mof.gov.vn/chi-tiet-tin/quy-dinh-chi-tiet-giam-thue-tdn",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 机关内部工会活动、模范公务员表彰与内部软硬件采购公告。

## 6. 异常与改版判定 (Health & Failure Detection)
* 接口返回非 JSON、401/403 或 `json_path` 连续 2 次提取为空。
