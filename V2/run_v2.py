"""
V2/run_v2.py
------------
越南产业情报雷达系统 V2 独立调度入口（严格依据 8492 QA 审计报告全量 5 大补丁构建，与 V1 彻底隔离）。

执行流水线：
1. 自动编译只读信源总册 (compile_registry) -> 生成 V2/sources/MASTER-SOURCE-REGISTRY.md & V2/config/master_sources_registry.json；
2. 过滤活跃源 (status == 'active') 并按优先级 (P0 -> P1 -> P2) 调度上层业务技能 (ArchetypeSkill)；
3. 技能层委托底层协议驱动 (ProtocolDriver + HostThrottle<=2) 并发抓取，并回写 SourceHealthLedger；
4. CandidateVault 统一赋码 `C-{source_id}-{seq:04d}`，生成脱敏 LLM Payload（剔除全部 URL）与物理底账；
5. 提供 `finalize_curated_brief()` 完成防幻觉 `backfill_candidate_urls()` 与 Lazy Probe 最终 200 OK 探活校验。

用法：
    python V2/run_v2.py --compile-only
    python V2/run_v2.py --collect --max-workers 6
    python V2/run_v2.py --collect --source-id SRC-MED-001
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

V2_ROOT = os.path.dirname(os.path.abspath(__file__))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sources.drivers import HostThrottle, HttpFetcher
from sources.interfaces.compile_registry_md import compile_registry
from sources.interfaces.contracts import (
    CandidateVault,
    CuratedBriefItem,
    ExtractedCandidate,
    NetworkConfig,
    ParsedSourceCard,
    RawExtractedItem,
    RegistryEntry,
    SourceCardParser,
    backfill_candidate_urls,
)
from sources.interfaces.health_ledger import DEFAULT_LEDGER_DB, SourceHealthLedger
from sources.skills import get_archetype_skill

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
logger = logging.getLogger("v2.runner")


def load_active_cards(
    entries: List[RegistryEntry],
    v2_root: str = V2_ROOT,
    only_source_id: Optional[str] = None,
    only_source_ids: Optional[List[str]] = None,
) -> List[Tuple[RegistryEntry, ParsedSourceCard]]:
    id_filter = set()
    if only_source_id:
        id_filter.update(x.strip().upper() for x in only_source_id.split(",") if x.strip())
    if only_source_ids:
        id_filter.update(x.strip().upper() for x in only_source_ids if x.strip())

    loaded: List[Tuple[RegistryEntry, ParsedSourceCard]] = []
    for entry in entries:
        if id_filter and entry.source_id.upper() not in id_filter:
            continue
        if entry.status != "active" and not id_filter:
            continue
        card_abs = os.path.join(v2_root, entry.card_path)
        with open(card_abs, "r", encoding="utf-8") as f:
            parsed = SourceCardParser.parse_card_markdown(f.read())
        loaded.append((entry, parsed))

    loaded.sort(key=lambda pair: (PRIORITY_ORDER.get(pair[0].priority, 9), pair[0].source_id))
    return loaded


def run_collection_pipeline(
    v2_root: str = V2_ROOT,
    db_path: Optional[str] = None,
    fetcher: Optional[HttpFetcher] = None,
    max_workers: int = 6,
    only_source_id: Optional[str] = None,
    only_source_ids: Optional[List[str]] = None,
    export_dir: Optional[str] = None,
) -> Dict[str, Any]:
    cards_dir = os.path.join(v2_root, "sources", "cards")
    out_md = os.path.join(v2_root, "sources", "MASTER-SOURCE-REGISTRY.md")
    out_json = os.path.join(v2_root, "config", "master_sources_registry.json")
    ledger_db = db_path or os.path.join(v2_root, "data", "state_ledger.db")

    entries = compile_registry(
        cards_dir=cards_dir,
        out_md=out_md,
        out_json=out_json,
        db_path=ledger_db,
        root_dir=v2_root,
    )
    active_cards = load_active_cards(
        entries,
        v2_root=v2_root,
        only_source_id=only_source_id,
        only_source_ids=only_source_ids,
    )

    ledger = SourceHealthLedger(ledger_db)
    http = fetcher or HttpFetcher(throttle=HostThrottle(max_per_host=2))
    vault = CandidateVault()
    errors: Dict[str, str] = {}

    def _run_one(pair: Tuple[RegistryEntry, ParsedSourceCard]) -> Tuple[str, List[RawExtractedItem]]:
        entry, parsed = pair
        skill = get_archetype_skill(entry.archetype_skill)
        items = skill.execute(parsed, fetcher=http, ledger=ledger)
        return entry.source_id, items

    raw_results_by_source: Dict[str, List[RawExtractedItem]] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(active_cards) or 1))) as pool:
        future_map = {pool.submit(_run_one, pair): pair[0].source_id for pair in active_cards}
        for fut in as_completed(future_map):
            sid = future_map[fut]
            try:
                _, items = fut.result()
                raw_results_by_source[sid] = items
            except Exception as exc:
                errors[sid] = str(exc)

    # Deterministic registration order by source_id
    for sid in sorted(raw_results_by_source.keys()):
        vault.register_many(raw_results_by_source[sid])

    # Re-compile registry so any health status transition is reflected immediately
    compile_registry(cards_dir=cards_dir, out_md=out_md, out_json=out_json, db_path=ledger_db, root_dir=v2_root)

    run_dir = export_dir or os.path.join(v2_root, "data", "runs")
    os.makedirs(run_dir, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")

    vault_path = os.path.join(run_dir, f"{today_str}_candidate_vault.json")
    payload_path = os.path.join(run_dir, f"{today_str}_llm_payloads.json")

    vault_dict = {cid: cand.to_dict() for cid, cand in vault.as_dict().items()}
    llm_payloads = vault.to_llm_payloads()

    with open(vault_path, "w", encoding="utf-8") as vf:
        json.dump(vault_dict, vf, ensure_ascii=False, indent=2)
    with open(payload_path, "w", encoding="utf-8") as pf:
        json.dump(llm_payloads, pf, ensure_ascii=False, indent=2)

    return {
        "total_registry_sources": len(entries),
        "dispatched_sources": len(active_cards),
        "succeeded_sources": len(raw_results_by_source),
        "failed_sources": errors,
        "total_candidates": len(vault),
        "vault": vault,
        "vault_path": vault_path,
        "llm_payload_path": payload_path,
    }


def finalize_curated_brief(
    curated_items: List[CuratedBriefItem],
    candidate_vault: Dict[str, ExtractedCandidate],
    fetcher: Optional[HttpFetcher] = None,
    lazy_probe: bool = True,
) -> List[CuratedBriefItem]:
    """
    阶段 C 安全回填与 Lazy Probe 延迟探活：
    1. 将大模型输出的 ref_candidate_ids 映射回真实 direct_url；
    2. 仅对最终选入简报的链接执行 HTTP 200 物理探活校验，过滤死链。
    """
    backfill_candidate_urls(curated_items, candidate_vault)
    if not lazy_probe:
        return curated_items

    http = fetcher or HttpFetcher()
    probe_cfg = NetworkConfig(verify_ssl=False, timeout=10)
    for item in curated_items:
        live_urls: List[str] = []
        for url in item.verified_urls:
            ok, code = http.probe_live(url, probe_cfg)
            if ok:
                live_urls.append(url)
            else:
                logger.warning("Lazy Probe 拦截失效链接 (%s, status=%s)", url, code)
        item.verified_urls = live_urls
    return curated_items


def run_stage_b_and_c(
    v2_root: str = V2_ROOT,
    date_str: Optional[str] = None,
    draft_json_path: Optional[str] = None,
    lazy_probe: bool = True,
    max_items: int = 20,
    send_email: bool = False,
    record_delivery: bool = False,
    fetcher: Optional[HttpFetcher] = None,
) -> Dict[str, Any]:
    """
    执行阶段 B（30 条并发粗裁 + 历史台账对账 + 精选回填）与阶段 C（<80KB 纯净五栏渲染 + 门禁校验 + 安全投递）。
    """
    from pipeline.cognitive.event_ledger import EventLedger
    from pipeline.cognitive.stage1_triage import export_triage_artifacts, run_stage1_triage
    from pipeline.cognitive.stage2_curate import (
        load_vault_as_candidates,
        select_and_curate_candidates,
    )
    from pipeline.delivery.brief_renderer import (
        render_brief_html,
        render_brief_markdown,
        save_brief_artifacts,
        validate_deliverable_gate,
    )
    from pipeline.delivery.email_sender import dispatch_brief_email

    day = date_str or datetime.now().strftime("%Y-%m-%d")
    runs_dir = os.path.join(v2_root, "data", "runs")
    reports_dir = os.path.join(v2_root, "data", "reports")
    reg_path = os.path.join(v2_root, "config", "master_sources_registry.json")
    payload_path = os.path.join(runs_dir, f"{day}_llm_payloads.json")
    vault_path = os.path.join(runs_dir, f"{day}_candidate_vault.json")

    if not os.path.exists(payload_path) or not os.path.exists(vault_path):
        raise FileNotFoundError(f"缺少当日采集产物：{payload_path} 或 {vault_path}，请先执行 --collect。")

    with open(payload_path, "r", encoding="utf-8") as f:
        payloads = json.load(f)
    with open(reg_path, "r", encoding="utf-8") as f:
        registry_entries = json.load(f)

    ledger = EventLedger(db_path=os.path.join(v2_root, "data", "projects.db"))
    triage = run_stage1_triage(payloads, registry_entries, ledger=ledger)
    batches_path, kept_path = export_triage_artifacts(triage, runs_dir, day)

    ai_draft = None
    if draft_json_path and os.path.exists(draft_json_path):
        with open(draft_json_path, "r", encoding="utf-8") as f:
            ai_draft = json.load(f)

    vault = load_vault_as_candidates(vault_path)
    curated_res = select_and_curate_candidates(
        triage["kept_candidates"],
        vault,
        fetcher=fetcher,
        lazy_probe=lazy_probe,
        max_items=max_items,
        ai_curated_draft=ai_draft,
    )
    curated_items: List[CuratedBriefItem] = curated_res["curated_items"]
    cmeta = {
        cid: {
            "candidate_id": cand.candidate_id,
            "source_id": cand.source_id,
            "source_name": cand.subject_entity or cand.source_id,
            "date_iso": cand.pub_date_raw[:10] if cand.pub_date_raw else day,
            "pub_date_raw": cand.pub_date_raw,
        }
        for cid, cand in vault.items()
    }
    for c in triage["kept_candidates"]:
        cmeta[c["candidate_id"]] = c
    html_content = render_brief_html(curated_items, day, candidate_meta=cmeta)
    md_content = render_brief_markdown(curated_items, day)
    gate_ok, gate_errors = validate_deliverable_gate(curated_items, html_content)
    if not gate_ok:
        raise RuntimeError(f"Pre-Flight 门禁拦截: {gate_errors}")

    html_path, md_path = save_brief_artifacts(curated_items, html_content, md_content, reports_dir, day)
    email_res = dispatch_brief_email(html_content, day, dry_run=(not send_email))

    recorded_cnt = 0
    milestone_stats = {"projects_created": 0, "projects_updated": 0, "timeline_events_added": 0}
    if record_delivery or send_email:
        recorded_cnt = ledger.record_briefing_delivery(curated_items, day)
        source_names = {
            e.get("source_id", ""): e.get("name", e.get("source_id", ""))
            for e in registry_entries
        }
        milestone_stats = ledger.record_project_milestones(
            curated_items,
            vault,
            day,
            source_names=source_names,
        )

    return {
        "date": day,
        "triage_stats": triage["stats"],
        "triage_batches_path": batches_path,
        "triage_kept_path": kept_path,
        "curated_count": len(curated_items),
        "column_counts": curated_res["column_counts"],
        "html_bytes": len(html_content.encode("utf-8")),
        "html_path": html_path,
        "md_path": md_path,
        "email_result": email_res,
        "recorded_to_ledger": recorded_cnt,
        "milestone_stats": milestone_stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Vietnam Intelligence Radar V2 Runner (Ref: 8492 & 2946)")
    parser.add_argument("--compile-only", action="store_true", help="Only compile V2 registry MD & JSON")
    parser.add_argument("--collect", action="store_true", help="Run V2 collection via Archetype Skills & Protocol Drivers")
    parser.add_argument("--full-pipeline", action="store_true", help="Run full Stage A -> B -> C pipeline in V2")
    parser.add_argument("--skip-collect", action="store_true", help="Used with --full-pipeline to reuse today's collected payloads")
    parser.add_argument("--draft-json", type=str, default=None, help="Optional AI curated draft JSON (ref_candidate_ids only)")
    parser.add_argument("--no-lazy-probe", action="store_true", help="Skip HTTP 200 lazy probe on selected URLs")
    parser.add_argument("--send-email", action="store_true", help="Actually send email (otherwise dry-run)")
    parser.add_argument("--date", type=str, default=None, help="Target date YYYY-MM-DD (default today)")
    parser.add_argument("--source-id", type=str, default=None, help="Run collection for single or comma-separated source_ids")
    parser.add_argument("--max-workers", type=int, default=6, help="Max worker threads")
    args = parser.parse_args()

    if args.full_pipeline:
        if not args.skip_collect:
            rep = run_collection_pipeline(max_workers=args.max_workers, only_source_id=args.source_id)
            print(
                f"[V2 Stage A] 采集完成: 调度 {rep['dispatched_sources']} 源, "
                f"成功 {rep['succeeded_sources']} 源, 产出候选 {rep['total_candidates']} 条。"
            )
        bc = run_stage_b_and_c(
            date_str=args.date,
            draft_json_path=args.draft_json,
            lazy_probe=(not args.no_lazy_probe),
            send_email=args.send_email,
        )
        print(
            f"[V2 Stage B+C] 粗裁保留 {bc['triage_stats']['kept']}/{bc['triage_stats']['total_input']} 条, "
            f"精选 {bc['curated_count']} 条 ({bc['column_counts']}), HTML 体积 {bc['html_bytes']} bytes (<80KB)。"
        )
        print(f"  - HTML 简报: {bc['html_path']}")
        print(f"  - MD 归档:   {bc['md_path']}")
        print(f"  - 邮件状态:  {bc['email_result']}")
    elif args.collect:
        report = run_collection_pipeline(
            max_workers=args.max_workers,
            only_source_id=args.source_id,
        )
        print(
            f"[V2] 采集完成: 纳管 {report['total_registry_sources']} 源, "
            f"调度 {report['dispatched_sources']} 源, 成功 {report['succeeded_sources']} 源, "
            f"失败 {len(report['failed_sources'])} 源, 产出候选 {report['total_candidates']} 条。"
        )
        print(f"  - 脱敏 LLM Payload: {report['llm_payload_path']}")
        print(f"  - 物理回填底账 Vault: {report['vault_path']}")
        if report["failed_sources"]:
            print(f"  - 异常明细: {report['failed_sources']}")
    else:
        entries = compile_registry(
            cards_dir=os.path.join(V2_ROOT, "sources", "cards"),
            out_md=os.path.join(V2_ROOT, "sources", "MASTER-SOURCE-REGISTRY.md"),
            out_json=os.path.join(V2_ROOT, "config", "master_sources_registry.json"),
            db_path=DEFAULT_LEDGER_DB,
        )
        print(f"[V2] 总册编译完成，共 {len(entries)} 个信源。")


if __name__ == "__main__":
    main()
