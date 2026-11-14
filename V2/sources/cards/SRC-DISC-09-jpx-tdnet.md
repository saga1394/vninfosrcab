---
source_id: SRC-DISC-09
name: "东京证券交易所 (JPX / TDnet)"
cluster: corporate_disclosure
target_url: "https://www.release.tdnet.info/inbs/I_list_001_20261102.html"
archetype_skill: disclosure-sniffer
protocol_driver: html_table_driver
check_frequency: daily
priority: P1
expected_column: fdi
status: active
last_audit_date: "2026-11-13"

network_config:
  verify_ssl: true
  timeout: 20
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

attachment_probe: false
---
# 信源作业指导卡：东京证券交易所 (JPX / TDnet) (SRC-DISC-09)

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 4 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：企业原始披露
* **价值等级**：P1（预期归仓 `fdi`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`https://www.release.tdnet.info/inbs/I_list_001_20261102.html`
* **底层驱动**：`html_table_driver`（实测通道：`HTML Table (Daily Timely Disclosure List)`）
* **技术备注**：Open (HTTPS List)

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `disclosure-sniffer` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{
  "source_id": "SRC-DISC-09",
  "title": "[60850] Ｇ－アーキテクツＳＪ: 第三者割当により発行された第５回新株予約権（行使価額修正条項付）の月間行使状況に関するお知らせ",
  "pub_date_raw": "2026-11-02 12:15",
  "subject_entity": "东京证券交易所 (JPX / TDnet)",
  "geo_location": "Vietnam (全国/待定位)",
  "signal_type": "capital_increase",
  "project_scale": null,
  "evidence_snippet": "[60850] Ｇ－アーキテクツＳＪ: 第三者割当により発行された第５回新株予約権（行使価額修正条項付）の月間行使状況に関するお知らせ",
  "direct_url": "https://www.release.tdnet.info/inbs/140120261102562562.pdf",
  "attachment_urls": []
}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
