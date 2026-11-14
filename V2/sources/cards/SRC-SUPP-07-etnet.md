---
source_id: SRC-SUPP-07
name: "中文商业与转载: EtNet 经济通"
cluster: media_fdi
target_url: "https://www.etnet.com.hk/www/tc/news/categorized_news.php"
archetype_skill: media-stream-curator
protocol_driver: html_card_driver
check_frequency: daily
priority: P2
expected_column: macro_policy
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：中文商业与转载: EtNet 经济通 (SRC-SUPP-07)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 4 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：补充渠道与外围资讯
* **价值等级**：P2（预期归仓 `macro_policy`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www.etnet.com.hk/www/tc/news/categorized_news.php`
* **底层驱动**：`html_card_driver`（实测通道：`HTML List (HK Financial Portal)`）
* **技术备注**：Open (HTTPS)

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `media-stream-curator` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-SUPP-07",
  "title": "真知灼見－溫灼培 | 金價3900美元成短線關鍵支持30/10/2026 12:28",
  "pub_date_raw": "2026-11-02",
  "subject_entity": "中文商业与转载: EtNet 经济通",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "真知灼見－溫灼培 | 金價3900美元成短線關鍵支持30/10/2026 12:28",
  "direct_url": "https://www.etnet.com.hk/www/tc/news/categorized_news_detail.php?newsid=414826&category=us",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
