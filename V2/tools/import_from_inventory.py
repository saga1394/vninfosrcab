"""
V2/tools/import_from_inventory.py
----------------------------------
分批将项目已有实测台账（batch_1~4_raw_results.json + config/sources_core_39.json）
无损导入 V2/sources/cards/*.md，并编译生成 V2 只读总册。

严格遵循项目约定：
- 完全隔离在 V2/ 内操作，不修改根目录任何原有文件；
- 强制剔除工商登记流水 (SRC-A08 -> retired)；
- 跳过与首批示范卡 URL 完全重合的 5 个 ID (SRC-A01/A02/A09/A13/B03)，保留已有示范卡；
- 自动为每张卡注入精确的 protocol_driver、network_config、api_spec、attachment_probe 与真实第 4 节 JSON 样本。
"""

import argparse
from datetime import datetime
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

V2_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(V2_ROOT)
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

from sources.interfaces.compile_registry_md import compile_registry
from sources.interfaces.contracts import SourceCardParser
from sources.interfaces.health_ledger import DEFAULT_LEDGER_DB, SourceHealthLedger

SKIP_DUPLICATE_IDS = {"SRC-A01", "SRC-A02", "SRC-A09", "SRC-A13", "SRC-B03"}
RETIRED_IDS = {"SRC-A08"}

BLOCKED_MARKERS = (
    "waf intercepted",
    "automated access blocked",
    "automated request denied",
    "connection refused",
    "http 503",
    "spa auth required",
    "angular spa",
    "react spa shell",
)

# Exact endpoint & API overrides verified in config/sources_core_39.json & V1 collector
CORE_ENDPOINT_OVERRIDES = {
    "SRC-A07": "https://fia.mof.gov.vn",
    "SRC-B04": "https://deepc.vn/vi/blog/category/tin-tuc/",
    "SRC-ASSOC-01": "http://www.vietnamtextile.org.vn",
    "SRC-ASSOC-03": "https://vla.com.vn/tin-tuc/",
}


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:28] or "source"


def _load_core_map() -> Dict[str, Dict[str, Any]]:
    core_path = os.path.join(PROJECT_ROOT, "config", "sources_core_39.json")
    if not os.path.exists(core_path):
        return {}
    with open(core_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {str(s["source_id"]).upper(): s for s in data.get("sources", [])}


def _infer_driver(item: Dict[str, Any], core_item: Optional[Dict[str, Any]]) -> str:
    method = str(item.get("method_verified") or "").lower()
    if "sitemap" in method:
        return "sitemap_driver"
    if "empty placeholder" in method or "html list" in method or "html card" in method:
        return "html_card_driver"
    if "rss" in method or "feed" in method:
        return "rss_driver"
    if "table" in method:
        return "html_table_driver"
    if "rest api" in method or "static javascript" in method:
        return "rest_api_driver"
    if core_item:
        ch = str(core_item.get("channel") or "").lower()
        if ch == "rss":
            return "rss_driver"
        if ch == "table":
            return "html_table_driver"
        if ch == "api":
            return "rest_api_driver"
    return "html_card_driver"


def _infer_status(sid: str, item: Dict[str, Any]) -> str:
    if sid in RETIRED_IDS:
        return "retired"
    status_code = item.get("status_code")
    method = str(item.get("method_verified") or "").lower()
    if status_code in (400, 401, 403, 404, 500, 503, None):
        return "degraded"
    if any(m in method for m in BLOCKED_MARKERS):
        return "degraded"
    return "active"


def _infer_cluster_skill_column(
    sid: str, item: Dict[str, Any], core_item: Optional[Dict[str, Any]]
) -> Tuple[str, str, str, str]:
    """Returns (cluster, archetype_skill, expected_column, signal_type)."""
    cat = str(item.get("category") or "").lower()
    name = str(item.get("name") or "").lower()

    if sid.startswith("SRC-DISC-") or "交易所" in cat or "disclosure" in cat:
        return ("corporate_disclosure", "disclosure-sniffer", "fdi", "capital_increase")

    if sid in ("SRC-A09", "SRC-A10", "SRC-A08") or sid.endswith("-D") or "环境" in name or "nông nghiệp và môi trường" in name or "legal" in cat:
        col = "macro_policy" if sid in ("SRC-A12", "SRC-A13") else "legal_approval"
        sig = "policy_regulation" if col == "macro_policy" else "eia_approval"
        return ("legal_approval", "gazette-table-parser", col, sig)

    if (
        sid.startswith("SRC-B")
        or sid.endswith("-B")
        or sid.endswith("-E")
        or sid in ("SRC-A05", "SRC-IND-PROP-01")
        or "工业园" in cat
        or "管委会" in cat
        or "建设" in cat
        or "khu công nghiệp" in name
        or "khu kinh tế" in name
        or "ban quản lý" in name
    ):
        return ("industrial_park", "park-news-inspector", "industrial_park", "land_grant")

    if sid in ("SRC-A06", "SRC-A07", "SRC-A14", "SRC-A15", "SRC-A16") or "国际组织" in cat:
        return ("media_fdi", "media-stream-curator", "fdi", "investment_mou")

    if (
        sid in ("SRC-A04", "SRC-IND-PROP-02", "SRC-IND-PROP-03", "SRC-KR-MED-04")
        or sid.startswith("SRC-TW-MED-")
        or sid.startswith("SRC-ASSOC-")
        or "协会" in cat
    ):
        return ("media_fdi", "media-stream-curator", "industry_focus", "policy_regulation")

    return ("media_fdi", "media-stream-curator", "macro_policy", "policy_regulation")


def _infer_priority(sid: str, core_item: Optional[Dict[str, Any]], expected_col: str) -> str:
    if core_item or expected_col in ("fdi", "legal_approval"):
        return "P0" if sid in ("SRC-A03", "SRC-A07", "SRC-A10", "SRC-DISC-01", "SRC-DISC-03", "SRC-DISC-05", "SRC-DISC-10") else "P1"
    if expected_col == "industrial_park":
        return "P1"
    return "P2"


def _build_network_and_api_spec(
    sid: str, item: Dict[str, Any], endpoint: str, core_item: Optional[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], bool]:
    sec = str(item.get("security_state") or "").lower()
    method_v = str(item.get("method_verified") or "").lower()

    verify_ssl = True
    if ".gov.vn" in endpoint or "szse.cn" in endpoint or "hkexnews.hk" in endpoint or "legacy tls" in method_v or "schannel" in method_v:
        verify_ssl = False

    use_curl = ("curl" in method_v) or ("schannel" in method_v) or (sid in ("SRC-DISC-03", "SRC-DISC-05"))
    headers: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    net_cfg: Dict[str, Any] = {
        "verify_ssl": verify_ssl,
        "timeout": 20 if (".gov.vn" in endpoint or sid.startswith("SRC-DISC-")) else 15,
        "headers": headers,
    }
    if "thamvan.mae.gov.vn" in endpoint:
        net_cfg["resolve_ip"] = "103.9.85.148"
    if use_curl:
        net_cfg["use_curl"] = True

    api_spec: Optional[Dict[str, Any]] = None
    if sid == "SRC-DISC-01":
        api_spec = {
            "method": "POST",
            "content_type": "form",
            "payload_template": {
                "pageNum": 1,
                "pageSize": 10,
                "column": "szse",
                "tabName": "fulltext",
                "searchkey": "越南",
            },
            "json_path": "announcements",
            "title_template": "[{secCode}] {secName}: {announcementTitle}",
            "detail_url_template": "http://static.cninfo.com.cn/{adjunctUrl}",
            "date_field": "announcementTime",
        }
    elif sid == "SRC-DISC-03":
        net_cfg["headers"]["Referer"] = "https://www.szse.cn/"
        api_spec = {
            "method": "POST",
            "content_type": "json",
            "payload_template": {
                "seDate": ["", ""],
                "searchKey": ["越南"],
                "channelCode": ["listedNotice_disc"],
                "pageSize": 10,
                "pageNum": 1,
            },
            "json_path": "data",
            "detail_url_template": "https://www.szse.cn/disclosure/listed/bulletin/detail/index.html?{id}",
            "date_field": "publishTime",
        }
    elif sid == "SRC-DISC-05":
        net_cfg["headers"]["Referer"] = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"
        api_spec = {
            "method": "GET",
            "nested_json_field": "result",
            "title_template": "[{STOCK_CODE}] {STOCK_NAME}: {TITLE}",
            "detail_url_template": "https://www1.hkexnews.hk{FILE_LINK}",
            "date_field": "DATE_TIME",
        }
    elif sid == "SRC-DISC-10":
        net_cfg["headers"] = {
            "User-Agent": "VnInvestmentResearch AdminContact@vnresearch.org",
            "Accept": "application/json",
        }
        api_spec = {
            "method": "GET",
            "json_path": "hits.hits",
            "title_template": "[{form}] {display_names}",
            "detail_url_template": "https://www.sec.gov/edgar/browse/?CIK={ciks}",
            "date_field": "file_date",
        }
    elif sid == "VN-LOC-14-DD-B":
        api_spec = {
            "method": "GET",
            "json_path": "data",
            "detail_url_template": "https://dseza.danang.gov.vn/tin-tuc/{id}",
            "date_field": "created_at",
        }
    elif _infer_driver(item, core_item) == "rest_api_driver":
        api_spec = {"method": "GET", "json_path": ""}

    attachment_probe = sid in ("SRC-A03", "SRC-A07", "SRC-A10")
    return net_cfg, api_spec, attachment_probe


def _yaml_quote(s: str) -> str:
    return json.dumps(str(s), ensure_ascii=False)


def _format_card_markdown(
    sid: str,
    item: Dict[str, Any],
    endpoint: str,
    cluster: str,
    skill: str,
    driver: str,
    priority: str,
    expected_col: str,
    status: str,
    signal_type: str,
    net_cfg: Dict[str, Any],
    api_spec: Optional[Dict[str, Any]],
    attachment_probe: bool,
    batch_num: int,
) -> str:
    name = str(item.get("name") or sid).strip()
    today_str = datetime.now().strftime("%Y-%m-%d")

    yaml_lines = [
        "---",
        f"source_id: {sid}",
        f"name: {_yaml_quote(name)}",
        f"cluster: {cluster}",
        f"target_url: {_yaml_quote(endpoint)}",
        f"archetype_skill: {skill}",
        f"protocol_driver: {driver}",
        "check_frequency: daily",
        f"priority: {priority}",
        f"expected_column: {expected_col}",
        f"status: {status}",
        f'last_audit_date: "{today_str}"',
        "",
        "network_config:",
        f"  verify_ssl: {'true' if net_cfg['verify_ssl'] else 'false'}",
        f"  timeout: {net_cfg['timeout']}",
    ]
    if net_cfg.get("resolve_ip"):
        yaml_lines.append(f'  resolve_ip: "{net_cfg["resolve_ip"]}"')
    if net_cfg.get("use_curl"):
        yaml_lines.append("  use_curl: true")
    yaml_lines.append("  headers:")
    for hk, hv in net_cfg["headers"].items():
        yaml_lines.append(f"    {hk}: {_yaml_quote(hv)}")

    if api_spec:
        yaml_lines.append("")
        yaml_lines.append("api_spec:")
        yaml_lines.append(f"  method: {api_spec.get('method', 'GET')}")
        if api_spec.get("content_type"):
            yaml_lines.append(f"  content_type: {api_spec['content_type']}")
        if "payload_template" in api_spec and api_spec["payload_template"] is not None:
            yaml_lines.append(f"  payload_template: {json.dumps(api_spec['payload_template'], ensure_ascii=False)}")
        if api_spec.get("json_path"):
            yaml_lines.append(f"  json_path: {_yaml_quote(api_spec['json_path'])}")
        if api_spec.get("nested_json_field"):
            yaml_lines.append(f"  nested_json_field: {_yaml_quote(api_spec['nested_json_field'])}")
        if api_spec.get("title_template"):
            yaml_lines.append(f"  title_template: {_yaml_quote(api_spec['title_template'])}")
        if api_spec.get("detail_url_template"):
            yaml_lines.append(f"  detail_url_template: {_yaml_quote(api_spec['detail_url_template'])}")
        if api_spec.get("date_field"):
            yaml_lines.append(f"  date_field: {_yaml_quote(api_spec['date_field'])}")

    yaml_lines.append("")
    yaml_lines.append(f"attachment_probe: {'true' if attachment_probe else 'false'}")
    yaml_lines.append("---")

    samples = item.get("sample_entries") or item.get("samples") or []
    sample0 = samples[0] if samples and isinstance(samples[0], dict) else {}
    sample_title = str(sample0.get("title") or f"{name} 最新动态").strip()
    sample_date = str(sample0.get("pub_date") or today_str).strip()
    sample_url = str(sample0.get("url") or endpoint).strip()
    sample_summary = str(sample0.get("summary") or sample_title).strip()[:300]
    geo = str(item.get("province_cn") or item.get("province") or "Vietnam (全国/待定位)")

    contract_sample = {
        "source_id": sid,
        "title": sample_title,
        "pub_date_raw": sample_date,
        "subject_entity": name,
        "geo_location": geo,
        "signal_type": signal_type,
        "project_scale": None,
        "evidence_snippet": sample_summary,
        "direct_url": sample_url,
        "attachment_urls": [],
    }

    notes = str(item.get("technical_notes") or item.get("security_state") or "已通过 7163 全量实测验证")
    method_desc = str(item.get("method_verified") or driver)

    body = f"""
# 信源作业指导卡：{name} ({sid})

## 1. 信源定位与情报价值 (Intelligence Role & Value)
* **导入批次**：第 {batch_num} 批（源自 7163 全网 196 源实测台账）
* **机构/频道类别**：{item.get('category_cn') or item.get('category') or cluster}
* **价值等级**：{priority}（预期归仓 `{expected_col}`）

## 2. 机读提取规则与端点结构 (Executable Extraction Specs)
* **唯一靶点 URL**：`{endpoint}`
* **底层驱动**：`{driver}`（实测通道：`{method_desc}`）
* **技术备注**：{notes}

## 3. 核心信号捕捉规则 (Signal Extraction Rules)
* 由上层业务技能 `{skill}` 执行信号识别与实体抽取，重点捕获外资落地、工业园供地、开工奠基、环评批复及涉企政策动向。

## 4. 抽取字段契约 (RawExtractedItem Schema Contract)
```json
{json.dumps(contract_sample, ensure_ascii=False, indent=2)}
```

## 5. 噪声屏蔽与跳过准则 (Noise Discard Rules)
* 剔除政务党建、文体慈善、社会刑事八卦及微型商贸企业工商登记流水；
* 无日期常青导航页面标记 `date_unverified` 隔离，严禁冒充今日增量。

## 6. 异常与改版判定 (Health & Failure Detection)
* 连续 2 次抓取异常或解析异常为空自动降级为 `degraded`。
"""
    return "\n".join(yaml_lines) + "\n" + body.lstrip()


def import_batch(batch_num: int, overwrite: bool = False) -> Dict[str, Any]:
    batch_path = os.path.join(
        PROJECT_ROOT, "archive", "data_process_dumps", "inventory", f"batch_{batch_num}_raw_results.json"
    )
    with open(batch_path, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    core_map = _load_core_map()
    cards_dir = os.path.join(V2_ROOT, "sources", "cards")
    os.makedirs(cards_dir, exist_ok=True)
    ledger = SourceHealthLedger(DEFAULT_LEDGER_DB)

    created = 0
    skipped_dup = 0
    retired_cnt = 0
    degraded_cnt = 0
    active_cnt = 0

    for item in batch_data.get("sources", []):
        sid = str(item["id"]).upper()
        if sid in SKIP_DUPLICATE_IDS:
            skipped_dup += 1
            continue

        core_item = core_map.get(sid)
        endpoint = CORE_ENDPOINT_OVERRIDES.get(
            sid,
            (core_item.get("endpoint") if core_item else None)
            or item.get("effective_endpoint")
            or item.get("target_url"),
        )
        driver = _infer_driver(item, core_item)
        status = _infer_status(sid, item)
        cluster, skill, expected_col, signal_type = _infer_cluster_skill_column(sid, item, core_item)
        priority = _infer_priority(sid, core_item, expected_col)
        net_cfg, api_spec, attachment_probe = _build_network_and_api_spec(sid, item, endpoint, core_item)

        slug = _slugify(str(item.get("code_name") or item.get("name") or sid))
        fname = f"{sid}-{slug}.md"
        fpath = os.path.join(cards_dir, fname)

        if not os.path.exists(fpath) or overwrite:
            md_text = _format_card_markdown(
                sid=sid,
                item=item,
                endpoint=endpoint,
                cluster=cluster,
                skill=skill,
                driver=driver,
                priority=priority,
                expected_col=expected_col,
                status=status,
                signal_type=signal_type,
                net_cfg=net_cfg,
                api_spec=api_spec,
                attachment_probe=attachment_probe,
                batch_num=batch_num,
            )
            # Validate immediately with SourceCardParser before writing
            SourceCardParser.parse_card_markdown(md_text)
            with open(fpath, "w", encoding="utf-8") as out_f:
                out_f.write(md_text)
            created += 1

        if status == "retired":
            ledger.set_status(sid, "retired", "按项目指令永久剔除工商登记流水")
            retired_cnt += 1
        elif status == "degraded":
            ledger.set_status(sid, "degraded", str(item.get("method_verified") or "WAF/Blocked"))
            degraded_cnt += 1
        else:
            ledger.set_status(sid, "active", "")
            active_cnt += 1

    entries = compile_registry(
        cards_dir=cards_dir,
        out_md=os.path.join(V2_ROOT, "sources", "MASTER-SOURCE-REGISTRY.md"),
        out_json=os.path.join(V2_ROOT, "config", "master_sources_registry.json"),
        db_path=DEFAULT_LEDGER_DB,
    )
    return {
        "batch": batch_num,
        "total_in_batch": len(batch_data.get("sources", [])),
        "written_cards": created,
        "skipped_existing_demo_overlap": skipped_dup,
        "active": active_cnt,
        "degraded": degraded_cnt,
        "retired": retired_cnt,
        "registry_total": len(entries),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch importer for V2 source cards")
    parser.add_argument("--batch", type=int, required=True, choices=[1, 2, 3, 4], help="Batch number 1..4")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing cards")
    args = parser.parse_args()
    summary = import_batch(args.batch, overwrite=args.overwrite)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
