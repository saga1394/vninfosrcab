"""
V2/pipeline/cognitive/stage1_triage.py
--------------------------------------
阶段 B · Step B1：并发 30 条分包粗裁与时效隔离器 (Ref: 2946 & 9381)。

核心职责：
1. 解析多格式原始日期并隔离 `date_unverified` 与超期 (>72h) 历史文档，彻底封堵旧闻诈尸；
2. 基于“本土主体 + 海外强传导”规则、行业词典与负面噪声词典，淘汰 80%+ 娱乐/社会/纯内政/与越无关杂讯；
3. 按每包 30 条切片并附加 `EventLedger` 历史对照线索，支持并发调度外部 LLM 粗裁器或内置确定性裁量器；
4. 全程零 URL 透传，严格基于 `candidate_id` 流转。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from pipeline.cognitive.event_ledger import EventLedger, signal_to_stage

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NOISE_KEYWORDS = (
    "xổ số", "xo so", "trúng thưởng", "bóng đá", "bong da", "hoa hậu", "hoa hau", "ca sĩ", "diễn viên",
    "tử vong", "đăng ký hộ tịch", "tử hình", "ma túy", "tai nạn giao thông",
    "cướp giật", "kỷ niệm ngày", "đại hội đảng", "học tập và làm theo",
    "văn nghệ", "bóng chuyền", "sea games", "du lịch", "lễ hội",
    "triệu ha lúa", "nông thôn mới", "khám chữa bệnh", "tuyển sinh đại học",
    "bán ròng", "khối ngoại bán", "vn-index", "giá vàng", "giá xăng dầu", "lãi suất huy động",
    "jensen huang", "ceo nvidia",
    "lottery", "miss universe", "football", "murder", "drug trafficking",
)

VIETNAM_GEO_MARKERS = (
    "vietnam", "viet nam", "việt nam", "hà nội", "hanoi", "hồ chí minh", "tp.hcm", "hcm",
    "hải phòng", "haiphong", "bắc ninh", "bac ninh", "quảng ninh", "đồng nai", "dong nai",
    "bình dương", "binh duong", "long an", "tây ninh", "tay ninh", "đà nẵng", "da nang",
    "hưng yên", "hung yen", "thái nguyên", "thai nguyen", "nghệ an", "nghe an",
    "thanh hóa", "thanh hoa", "hà tĩnh", "ha tinh", "khánh hòa", "ninh bình", "phú thọ",
    "vsip", "becamex", "amata", "deep c", "sonadezi", "bw industrial", "long hậu",
    "越南", "越方", "河内", "胡志明", "海防", "北宁", "平阳", "同奈", "岘港", "广宁",
)

SECTOR_AND_FDI_KEYWORDS = (
    "fdi", "đầu tư", "investment", "nhà máy", "factory", "plant", "khu công nghiệp", "kcn",
    "industrial park", "industrial zone", "kkt", "economic zone", "bán dẫn", "semiconductor",
    "data center", "trung tâm dữ liệu", "trí tuệ nhân tạo", "dppa", "điện gió", "điện mặt trời",
    "lng", "bess", "lưu trữ năng lượng", "điện rác", "waste-to-energy", "kho lạnh", "logistics",
    "cảng biển", "khởi công", "động thổ", "đtm", "môi trường", "thuê đất", "giao đất",
    "giấy chứng nhận đăng ký đầu tư", "mở rộng", "tăng vốn", "cổ phần", "m&a", "liên doanh",
    "thuế", "hải quan", "chống bán phá giá", "tariff", "anti-dumping", "supply chain",
    "越南工厂", "设厂", "投产", "开工", "增资", "工业园", "半导体", "数据中心", "储能", "绿电", "环评",
)

BAD_TITLE_MARKERS = (
    "read more", "xem thêm", "chi tiết", "trang chủ", "tìm kiếm", "đăng nhập", "liên hệ",
    "sitemap", "privacy policy", "cookie policy",
)


def normalize_date_iso(raw: str, reference_date: Optional[datetime] = None) -> str:
    ref = reference_date or datetime.now(timezone.utc)
    s = (raw or "").strip()
    if not s or s in ("date_unverified", "-", "N/A", "null"):
        return "date_unverified"

    m_iso = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m_iso:
        try:
            dt = datetime(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)), tzinfo=timezone.utc)
            if dt <= ref + timedelta(days=2):
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # If AM/PM is present (e.g. Baochinhphu ASP.NET "11/12/2026 10:17:00 PM"), interpret MM/DD/YYYY first
    m_slash = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", s)
    if m_slash:
        a, b, y = int(m_slash.group(1)), int(m_slash.group(2)), int(m_slash.group(3))
        is_us = bool(re.search(r"\b(AM|PM)\b", s, re.IGNORECASE))
        candidates = [(y, a, b), (y, b, a)] if is_us else [(y, b, a), (y, a, b)]
        for yy, mm, dd in candidates:
            try:
                dt = datetime(yy, mm, dd, tzinfo=timezone.utc)
                if dt <= ref + timedelta(days=2):
                    return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    m_dash = re.search(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b", s)
    if m_dash:
        dd, mm, yy = int(m_dash.group(1)), int(m_dash.group(2)), int(m_dash.group(3))
        try:
            dt = datetime(yy, mm, dd, tzinfo=timezone.utc)
            if dt <= ref + timedelta(days=2):
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt <= ref + timedelta(days=2):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return "date_unverified"


def infer_target_column(item: Dict[str, Any], card_meta: Optional[Dict[str, Any]] = None) -> str:
    """
    先内容事实抽槽，后映射五大正交栏目（Ref: 9381 盲区 1 纠偏）。
    """
    text = f"{item.get('title', '')} {item.get('evidence_snippet', '')}".lower()
    sig = str(item.get("signal_type") or "").lower()
    cluster = str((card_meta or {}).get("cluster") or "")

    # 1. 法定公示与环评审批优先归 legal_approval
    if sig == "eia_approval" or cluster == "legal_approval" or re.search(
        r"\b(đtm|giấy phép môi trường|đánh giá tác động môi trường|xả thải|chấp thuận chủ trương đầu tư)\b",
        text,
    ):
        return "legal_approval"

    # 2. 重点关注产业专题（半导体、数据中心、DPPA、储能BESS、垃圾发电、LNG、高标冷链、AI基础设施）
    if re.search(
        r"(?:\bsemiconductor\b|\bbán dẫn\b|\bdata center\b|\btrung tâm dữ liệu\b|\bdppa\b|\bbess\b|\bwaste-to-energy\b|\bliquid cooling\b|\bpCB\b|\blng\b|điện rác|pin lưu trữ|kho lạnh|半导体|数据中心|液冷|储能|垃圾发电|绿电直供)",
        text,
        re.IGNORECASE,
    ):
        return "industry_focus"

    # 3. 工业园区一线动态（园区供地、基础设施批复、管委会招商、园区开工；上市公告设厂提“工业园”归 FDI）
    if sig == "land_grant" or (
        cluster not in ("corporate_disclosure", "job_radar")
        and sig not in ("factory_setup", "capital_increase")
        and re.search(
            r"(?:\bkhu công nghiệp\b|\bkcn\b|\bcụm công nghiệp\b|\bindustrial park\b|\bindustrial zone\b|\bvsip\b|\bbecamex\b|\bamata\b|\bdeep c\b|\bbw industrial\b|giao đất|thuê đất|giải phóng mặt bằng|hạ tầng kcn|工业园|工业区|清表|供地)",
            text,
            re.IGNORECASE,
        )
    ):
        return "industrial_park"

    # 3.5 宏观协定/关税/国内银行配股/财政税收/纯本土国企提前截断，防止误入 FDI
    if re.search(
        r"(?:\bfTA\b|\bvefta\b|hiệp định|thuế suất|thuế quan|thủ tục hải quan|giải ngân vốn đầu tư công|ngân hàng|chào bán.*cổ phiếu|chia cổ tức|\bvinasteel\b|\bvietinbank\b|\bacb\b)",
        text,
        re.IGNORECASE,
    ):
        return "macro_policy"

    # 4. FDI 外资与企业投资设厂扩产动向
    if (
        cluster in ("corporate_disclosure", "job_radar")
        or sig in ("factory_setup", "ground_breaking", "capital_increase", "investment_mou")
        or re.search(
            r"(?:\bfdi\b|\bnhà máy\b|\bfactory\b|\bplant\b|\bkhởi công\b|\bđộng thổ\b|\bvận hành\b|\btăng vốn\b|\bm&a\b|\bdây chuyền sản xuất\b|\blập công ty con\b|\bliteon\b|\bđầu tư\b.*\b(?:triệu|tỷ|million|billion)\s*(?:usd|\$)|设厂|建厂|投产|增资|扩产|施工合同|投资于越南|factory director|plant manager)",
            text,
            re.IGNORECASE,
        )
    ):
        return "fdi"

    # 5. 宏观财税/电价/法规/多式联运走廊
    return "macro_policy"


def _evaluate_candidate(
    item: Dict[str, Any],
    ref_dt: datetime,
    window_days: int,
    registry_map: Dict[str, Dict[str, Any]],
    ledger: EventLedger,
) -> Dict[str, Any]:
    title = (item.get("title") or "").strip()
    snippet = (item.get("evidence_snippet") or "").strip()
    combined = f"{title} {snippet}".lower()
    sid = str(item.get("source_id") or "")
    card_meta = registry_map.get(sid, {})

    date_iso = normalize_date_iso(str(item.get("pub_date_raw") or ""), ref_dt)
    if date_iso == "date_unverified":
        return {"candidate_id": item["candidate_id"], "decision": "isolate_unverified", "reason": "date_unverified", "score": 0}

    try:
        dt = datetime.strptime(date_iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age_days = (ref_dt.date() - dt.date()).days
    except ValueError:
        return {"candidate_id": item["candidate_id"], "decision": "isolate_unverified", "reason": "bad_date", "score": 0}

    if age_days > window_days:
        return {"candidate_id": item["candidate_id"], "decision": "drop_stale", "reason": f"age_{age_days}d", "score": 0, "date_iso": date_iso}

    if len(title) < 8 or any(b == title.lower() for b in BAD_TITLE_MARKERS):
        return {"candidate_id": item["candidate_id"], "decision": "drop_noise", "reason": "nav_or_short", "score": 0}

    if any(nk in combined for nk in NOISE_KEYWORDS):
        return {"candidate_id": item["candidate_id"], "decision": "drop_noise", "reason": "noise_keyword", "score": 0}

    cluster = str(card_meta.get("cluster") or "")
    priority = str(card_meta.get("priority") or "P2")
    is_vn_domestic = sid.startswith(("SRC-A", "SRC-B", "SRC-APP", "SRC-IP", "SRC-JOB", "SRC-MED", "SRC-VN", "VN-LOC"))
    has_vn_link = is_vn_domestic or any(gm in combined for gm in VIETNAM_GEO_MARKERS)

    if not has_vn_link:
        return {"candidate_id": item["candidate_id"], "decision": "drop_irrelevant", "reason": "no_vietnam_conduction", "score": 0}

    if ledger.is_already_reported(title=title):
        return {"candidate_id": item["candidate_id"], "decision": "drop_reported", "reason": "already_reported", "score": 0}

    score = 0
    if priority == "P0":
        score += 35
    elif priority == "P1":
        score += 25
    else:
        score += 15

    if age_days <= 1:
        score += 20
    elif age_days <= 2:
        score += 12
    else:
        score += 6

    kw_hits = sum(1 for kw in SECTOR_AND_FDI_KEYWORDS if kw in combined)
    score += min(kw_hits * 12, 48)
    if re.search(r"(\d+[\.,]?\d*\s*(triệu|tỷ|million|billion|ha|mw|gw|usd|亿|万))", combined):
        score += 15

    if not is_vn_domestic and cluster == "media_fdi" and kw_hits == 0:
        return {"candidate_id": item["candidate_id"], "decision": "drop_noise", "reason": "weak_overseas_macro", "score": score}

    if kw_hits == 0 and priority == "P2" and score < 40:
        return {"candidate_id": item["candidate_id"], "decision": "drop_low_signal", "reason": "low_industrial_signal", "score": score}

    col = infer_target_column(item, card_meta)
    stage = signal_to_stage(str(item.get("signal_type") or ""), f"{title} {snippet}")
    hist = ledger.lookup_historical_context(
        title=title,
        entity=str(item.get("subject_entity") or ""),
        province=str(item.get("geo_location") or ""),
        candidate_stage=stage,
    )
    if hist and hist.get("is_regression"):
        return {"candidate_id": item["candidate_id"], "decision": "drop_regression", "reason": "lifecycle_stage_regression", "score": score}

    return {
        "candidate_id": item["candidate_id"],
        "source_id": sid,
        "source_name": card_meta.get("name", item.get("subject_entity", sid)),
        "priority": priority,
        "date_iso": date_iso,
        "age_days": age_days,
        "title": title,
        "evidence_snippet": snippet,
        "geo_location": item.get("geo_location", ""),
        "signal_type": item.get("signal_type", ""),
        "project_scale": item.get("project_scale"),
        "target_column": col,
        "lifecycle_stage": stage,
        "is_follow_up": bool(hist and hist.get("is_progression")),
        "history_match": hist,
        "score": score,
        "decision": "keep",
    }


def _norm_title_key(title: str) -> str:
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fffÀ-ỹ]+", "", (title or "").lower())[:48]


def _event_cluster_key(title: str) -> Optional[str]:
    """Extract coarse event key (entity/topic + significant number) to merge multi-media reprints."""
    low = (title or "").lower()
    nums = [n.replace(".", "").replace(",", "") for n in re.findall(r"\b\d{2,4}(?:[.,]\d+)?\b", low)]
    # Ignore current year numbers in clustering
    sig_nums = [n for n in nums if n not in ("2025", "2026", "2027")]
    if not sig_nums:
        return None
    topic_hits = [
        tok for tok in ("lng", "vsip", "gia lách", "cần giờ", "meiko", "aspower", "phù mỹ", "thép", "bán dẫn", "振邦智能")
        if tok in low
    ]
    if topic_hits:
        return f"{topic_hits[0]}|{sig_nums[0][:3]}"
    return None


def run_stage1_triage(
    payloads: List[Dict[str, Any]],
    registry_entries: List[Dict[str, Any]],
    ledger: Optional[EventLedger] = None,
    reference_date: Optional[datetime] = None,
    window_days: int = 3,
    batch_size: int = 30,
    max_workers: int = 6,
    llm_batch_fn: Optional[Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """
    执行 Step B1 30 条分包并行粗裁：
    - 若传入 llm_batch_fn，则按 30 条/包并发调度大模型粗裁；
    - 否则执行零成本确定性规则+历史台账并发粗裁，同时落盘 30 条分包队列供审计或 LLM 复核。
    """
    ref_dt = reference_date or datetime.now(timezone.utc)
    reg_map = {str(e["source_id"]): e for e in registry_entries}
    db_ledger = ledger or EventLedger()

    batches: List[List[Dict[str, Any]]] = [
        payloads[i : i + batch_size] for i in range(0, len(payloads), batch_size)
    ]

    kept: List[Dict[str, Any]] = []
    stats = {
        "total_input": len(payloads),
        "batch_count": len(batches),
        "batch_size": batch_size,
        "isolate_unverified": 0,
        "drop_stale": 0,
        "drop_noise": 0,
        "drop_irrelevant": 0,
        "drop_reported": 0,
        "drop_low_signal": 0,
        "drop_regression": 0,
        "drop_duplicate": 0,
        "kept": 0,
    }

    def _process_batch(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if llm_batch_fn is not None:
            return llm_batch_fn(batch)
        return [_evaluate_candidate(it, ref_dt, window_days, reg_map, db_ledger) for it in batch]

    all_evals: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as pool:
        futs = [pool.submit(_process_batch, b) for b in batches]
        for fut in as_completed(futs):
            all_evals.extend(fut.result())

    seen_titles: Dict[str, Dict[str, Any]] = {}
    seen_events: Dict[str, Dict[str, Any]] = {}
    for ev in all_evals:
        dec = ev.get("decision", "drop_noise")
        if dec != "keep":
            stats[dec] = stats.get(dec, 0) + 1
            continue
        tkey = _norm_title_key(ev.get("title", ""))
        ekey = _event_cluster_key(ev.get("title", ""))
        match = seen_titles.get(tkey) or (seen_events.get(ekey) if ekey else None)
        if match is not None:
            stats["drop_duplicate"] += 1
            match.setdefault("merged_candidate_ids", [match["candidate_id"]]).append(ev["candidate_id"])
            if ev["score"] > match["score"]:
                match["score"] = ev["score"]
            continue
        ev["merged_candidate_ids"] = [ev["candidate_id"]]
        seen_titles[tkey] = ev
        if ekey:
            seen_events[ekey] = ev
        kept.append(ev)

    kept.sort(key=lambda x: (x.get("score", 0), x.get("date_iso", "")), reverse=True)
    stats["kept"] = len(kept)

    return {
        "reference_date": ref_dt.strftime("%Y-%m-%d"),
        "window_days": window_days,
        "stats": stats,
        "batches_preview": [
            {"batch_index": idx + 1, "count": len(b), "candidate_ids": [x["candidate_id"] for x in b]}
            for idx, b in enumerate(batches)
        ],
        "kept_candidates": kept,
    }


def export_triage_artifacts(result: Dict[str, Any], out_dir: str, date_str: str) -> Tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    batches_path = os.path.join(out_dir, f"{date_str}_triage_batches.json")
    kept_path = os.path.join(out_dir, f"{date_str}_triage_kept.json")
    with open(batches_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "reference_date": result["reference_date"],
                "window_days": result["window_days"],
                "stats": result["stats"],
                "batches": result["batches_preview"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    with open(kept_path, "w", encoding="utf-8") as f:
        json.dump(result["kept_candidates"], f, ensure_ascii=False, indent=2)
    return batches_path, kept_path
