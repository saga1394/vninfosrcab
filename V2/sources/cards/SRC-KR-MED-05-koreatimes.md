---
source_id: SRC-KR-MED-05
name: "The Korea Times (韩国时报)"
cluster: media_fdi
target_url: "https://www.koreatimes.co.kr"
archetype_skill: media-stream-curator
protocol_driver: html_card_driver
check_frequency: daily
priority: P2
expected_column: macro_policy
status: active
last_audit_date: "2026-11-12"

network_config:
  verify_ssl: true
  timeout: 15
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：The Korea Times (韩国时报) (SRC-KR-MED-05)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 2 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：Korea Media
* **价值等级**：P2（预期归仓 `macro_policy`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www.koreatimes.co.kr`
* **底层驱动**：`html_card_driver`（实测通道：`Lightweight HTML List`）
* **技术备注**：Korea Times national English daily. Extracted 5 latest stories directly from homepage.

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `media-stream-curator` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-KR-MED-05",
  "title": "COVER STORYNorth Korea has every incentive to keep stealing crypto, analysts sayThe $6.36 billion cryptocurrency heist targeting Binance has exposed a troubling reality for the digital asset industry: North Korea is increasingly exploiting security vulnerabilities to bankroll Pyongyang's military ambitions. The stolen amount is equivalent to 22 percent of North Korea's 2025 gross domestic product, making the attack the largest cryptocurrency theft on record and one of the biggest financial crimes in history. Analysts warned Sunday that it is unlikely to be the last. \"We're dealing with sophisticated adversaries who may have substantial resources, years of patience and objectives that extend well beyond financial gain,\" said Michael O'Loughlin, managing partner of Argonautic Global and board member of Blockchain Ireland. Proceeds from cryptocurrency theft have become an increasingly important source of funding for cash-strapped North Korea, alongside an estimated $22 billion in foreign income generated since 2022 through its support for Russia's war in Ukraine. The stolen funds could help finance its nuclear and ballistic missile programs, as well as efforts to modern3MIN READ",
  "pub_date_raw": "2026-11-12",
  "subject_entity": "The Korea Times (韩国时报)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "policy_regulation",
  "project_scale": null,
  "evidence_snippet": "COVER STORYNorth Korea has every incentive to keep stealing crypto, analysts sayThe $6.36 billion cryptocurrency heist targeting Binance has exposed a troubling reality for the digital asset industry: North Korea is increasingly exploiting security vulnerabilities to bankroll Pyongyang's military am",
  "direct_url": "https://www.koreatimes.co.kr/foreignaffairs/northkorea/20261101/cover-story-north-korea-has-every-incentive-to-keep-stealing-crypto-analysts-say",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
