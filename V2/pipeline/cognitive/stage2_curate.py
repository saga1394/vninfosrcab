"""
V2/pipeline/cognitive/stage2_curate.py
--------------------------------------
阶段 B · Step B2 & 阶段 C · 安全回填与门禁校验 (Ref: 2946 & 8492 补丁 5)。

核心职责：
1. 读取 Step B1 粗裁保留池 (`_triage_kept.json`) 或外部 AI 产出的脱敏研判草稿 (`curated_draft.json`，仅含 ref_candidate_ids)；
2. 结合 `EventLedger` 识别历史项目续报 (`is_follow_up=True`)、同事件多源合并 (`merged_candidate_ids`) 与五大正交纯净归仓；
3. 调用 `run_v2.finalize_curated_brief()` 完成 `backfill_candidate_urls()` 物理真链回填 + 最终入选 URL 延迟探活 (Lazy Probe)，死链自动由备选池替补；
4. 执行出报前零容忍质量门禁（真链闭合、无 `date_unverified` 混入、周未空仓容错）。
"""

import json
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from sources.drivers import HttpFetcher
from sources.interfaces.contracts import (
    VALID_COLUMNS,
    CuratedBriefItem,
    ExtractedCandidate,
    NetworkConfig,
    backfill_candidate_urls,
)

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COLUMN_QUOTAS = {
    "fdi": 5,
    "industrial_park": 4,
    "industry_focus": 4,
    "legal_approval": 3,
    "macro_policy": 4,
}


def load_vault_as_candidates(vault_path: str) -> Dict[str, ExtractedCandidate]:
    with open(vault_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    vault: Dict[str, ExtractedCandidate] = {}
    for cid, row in raw.items():
        vault[cid] = ExtractedCandidate(
            candidate_id=row["candidate_id"],
            source_id=row["source_id"],
            title=row["title"],
            pub_date_raw=row.get("pub_date_raw", ""),
            subject_entity=row.get("subject_entity", ""),
            geo_location=row.get("geo_location", ""),
            signal_type=row.get("signal_type", "policy_regulation"),
            project_scale=row.get("project_scale"),
            evidence_snippet=row.get("evidence_snippet", ""),
            direct_url=row["direct_url"],
            extracted_at=row.get("extracted_at", ""),
            attachment_urls=row.get("attachment_urls") or [],
        )
    return vault


def parse_ai_draft_to_curated(draft_items: Any) -> List[CuratedBriefItem]:
    """严格反序列化外部 AI 产出的结构化研判草稿，拦截任何非法栏目或缺失 ref_candidate_ids。"""
    if isinstance(draft_items, dict) and "items" in draft_items:
        draft_items = draft_items["items"]
    if not isinstance(draft_items, list):
        raise ValueError(f"AI 草稿必须为条目列表或包含 'items' 键的对象，收到 {type(draft_items)}")

    parsed: List[CuratedBriefItem] = []
    for row in draft_items:
        if not isinstance(row, dict):
            continue
        col = str(row.get("column") or row.get("col") or "").strip()
        if col not in VALID_COLUMNS:
            raise ValueError(f"非法报告栏目 '{col}'，必须属于 {sorted(VALID_COLUMNS)}")
        cids = [
            str(c).strip()
            for c in (row.get("ref_candidate_ids") or row.get("cids") or [])
            if str(c).strip()
        ]
        if not cids:
            title_label = row.get("title_zh") or row.get("title") or ""
            raise ValueError(f"条目 '{title_label}' 缺失 ref_candidate_ids，严禁无底层凭证输出。")
        parsed.append(
            CuratedBriefItem(
                column=col,  # type: ignore[arg-type]
                title_zh=str(row.get("title_zh") or row.get("title") or "").strip(),
                fact_summary=str(row.get("fact_summary") or row.get("fact") or "").strip(),
                insight_analysis=str(row.get("insight_analysis") or row.get("insight") or "").strip(),
                ref_candidate_ids=cids,
                is_follow_up=bool(row.get("is_follow_up", False) or row.get("stage") == "FOLLOW_UP"),
            )
        )
    return parsed


def _build_fact_and_insight(cand: Dict[str, Any]) -> Tuple[str, str]:
    date_iso = cand.get("date_iso", "")
    src_name = cand.get("source_name") or cand.get("source_id", "")
    geo = cand.get("geo_location") or "越南"
    scale = f"（规模/金额：{cand['project_scale']}）" if cand.get("project_scale") else ""
    snippet = re.sub(r"\s+", " ", (cand.get("evidence_snippet") or cand.get("title") or "").strip())
    if len(snippet) > 180:
        snippet = snippet[:177] + "..."

    hist = cand.get("history_match")
    hist_prefix = ""
    if hist and cand.get("is_follow_up"):
        hist_prefix = f"【既有项目进展】关联台账项目“{hist.get('project_name', '')}”（既往阶段：{hist.get('previous_stage', '')}）。"

    fact = f"{hist_prefix}{date_iso}，据 {src_name} 披露：{snippet}{scale}。涉及区域：{geo}。"

    col = cand.get("target_column", "macro_policy")
    stage = cand.get("lifecycle_stage", "")
    insight_map = {
        "fdi": f"该动态反映近期涉越制造投资及产能扩张动向（生命周期节点：{stage}），需持续跟踪后续环评、土地移交与供应链配套进度。",
        "industrial_park": f"一线园区载体释放供地与基础设施扩建信号，可作为重点制造业客户落地与园区承载能力评估的参照。",
        "industry_focus": f"属于半导体、数据中心、能源存储或高标物流等重点关注赛道动态，建议结合在越园区绿电与基础设施条件持续观察。",
        "legal_approval": f"属法定环评或行政审批公示节点（{stage}），表明相关工业或基础设施项目已进入实质合规定型阶段。",
        "macro_policy": "属财税、外贸监管或宏观要素价格政策信号，对在越制造企业的合规与运营成本具有直接传导影响。",
    }
    return fact, insight_map.get(col, insight_map["macro_policy"])


def select_and_curate_candidates(
    kept_candidates: List[Dict[str, Any]],
    candidate_vault: Dict[str, ExtractedCandidate],
    fetcher: Optional[HttpFetcher] = None,
    lazy_probe: bool = True,
    max_items: int = 20,
    ai_curated_draft: Optional[List[Dict[str, Any]]] = None,
    llm_curate_fn: Optional[Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """
    执行 Stage 2 精选、防幻觉回填与 Lazy Probe 死链替补闭环：
    - 优先消费 `ai_curated_draft` 或 `llm_curate_fn`；
    - 无外部草稿时使用确定性配额合成器生成严格合规的 `CuratedBriefItem` 列表；
    - 对最终入选的 Top 条目执行 HTTP 200 物理探活，若发现死链自动从备选池替补。
    """
    http = fetcher or HttpFetcher()
    probe_cfg = NetworkConfig(verify_ssl=False, timeout=10)

    if ai_curated_draft is not None:
        draft_items = parse_ai_draft_to_curated(ai_curated_draft)
    elif llm_curate_fn is not None:
        draft_items = parse_ai_draft_to_curated(llm_curate_fn(kept_candidates[:50]))
    else:
        draft_items = []
        picked_ids = set()
        # Distribute across the 5 orthogonal columns cleanly
        for col, quota in COLUMN_QUOTAS.items():
            col_pool = [c for c in kept_candidates if c.get("target_column") == col]
            count = 0
            for cand in col_pool:
                if count >= quota or len(draft_items) >= max_items:
                    break
                cid = cand["candidate_id"]
                if cid not in candidate_vault or cid in picked_ids:
                    continue
                if lazy_probe:
                    ok, _code = http.probe_live(candidate_vault[cid].direct_url, probe_cfg)
                    if not ok:
                        continue
                picked_ids.add(cid)
                fact, insight = _build_fact_and_insight(cand)
                ref_ids = [r for r in (cand.get("merged_candidate_ids") or [cid]) if r in candidate_vault]
                draft_items.append(
                    CuratedBriefItem(
                        column=col,  # type: ignore[arg-type]
                        title_zh=cand["title"],
                        fact_summary=fact,
                        insight_analysis=insight,
                        ref_candidate_ids=ref_ids or [cid],
                        is_follow_up=bool(cand.get("is_follow_up", False)),
                    )
                )
                count += 1

    # Always run mandatory anti-hallucination URL backfill + Lazy Probe on finalized items
    backfill_candidate_urls(draft_items, candidate_vault)
    probed_dead: List[str] = []
    if lazy_probe and (ai_curated_draft is not None or llm_curate_fn is not None):
        for item in draft_items:
            live: List[str] = []
            for url in item.verified_urls:
                ok, _code = http.probe_live(url, probe_cfg)
                if ok:
                    live.append(url)
                else:
                    probed_dead.append(url)
            item.verified_urls = live

    verified_items = [it for it in draft_items if it.verified_urls and not it.unresolved_ids]
    return {
        "curated_items": verified_items,
        "dropped_unverified": len(draft_items) - len(verified_items),
        "probed_dead_urls": probed_dead,
        "column_counts": {
            col: sum(1 for it in verified_items if it.column == col)
            for col in COLUMN_QUOTAS
        },
    }
