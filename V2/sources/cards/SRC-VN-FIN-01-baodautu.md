---
source_id: SRC-VN-FIN-01
name: "Báo Đầu tư (越南投资报 - 计划投资部机关报)"
cluster: media_fdi
target_url: "https://baodautu.vn/"
archetype_skill: media-stream-curator
protocol_driver: html_card_driver
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

search_spec:
  endpoint_template: "https://baodautu.vn/{keyword}/"
  keywords:
    - "bat-dong-san-c3"
    - "dau-tu-phat-trien-c10"

attachment_probe: false
---
# 信源作业指导卡：Báo Đầu tư (越南投资报 - 计划投资部机关报) (SRC-VN-FIN-01)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 2 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：Vietnam Finance & Industry
* **价值等级**：P1（预期归仓 `macro_policy`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://baodautu.vn/dau-tu-c4/`
* **底层驱动**：`html_card_driver`（实测通道：`Lightweight HTML List`）
* **技术备注**：Official newspaper of MPI. HTML list /dau-tu-c4/ yields 33 real investment stories.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `media-stream-curator` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-VN-FIN-01",
  "title": "Doanh nghiệp và kỳ vọng 2026: Sẵn sàng cho chu kỳ tăng trưởng mới",
  "pub_date_raw": "2026-11-12",
  "subject_entity": "Báo Đầu tư (越南投资报 - 计划投资部机关报)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "Doanh nghiệp và kỳ vọng 2026: Sẵn sàng cho chu kỳ tăng trưởng mới",
  "direct_url": "https://baodautu.vn/doanh-nghiep-va-ky-vong-2026-san-sang-cho-chu-ky-tang-truong-moi-d481381.html",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
