"""
V2/pipeline/cognitive/event_ledger.py
-------------------------------------
V2 事件生命周期状态机与项目历史记忆台账（完全隔离在 V2/data/projects.db）。
- 首次初始化时只读复制 V1 已有 406 项历史项目库至 V2/data/projects.db，绝不回写 V1；
- 提供实体/项目反向查库、防阶段倒退校验（Opus 盲区 2）、已报去重指纹校验及里程碑增量写回。
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import os
import re
import shutil
import sqlite3
from typing import Any, Dict, Iterator, List, Optional, Tuple

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(V2_ROOT)
DEFAULT_V2_PROJECTS_DB = os.path.join(V2_ROOT, "data", "projects.db")
V1_SEED_DB = os.path.join(PROJECT_ROOT, "data", "stage2", "projects.db")

STAGE_RANK: Dict[str, int] = {
    "investment_mou": 0,
    "MOU": 0,
    "PROPOSED": 0,
    "IRC_APPROVED": 1,
    "factory_setup": 1,
    "SITE_CLEARANCE": 2,
    "land_grant": 2,
    "EIA_CONSULTED": 3,
    "PERMIT_APPLIED": 3,
    "eia_approval": 3,
    "CONSTRUCTING": 4,
    "ground_breaking": 4,
    "OPERATING": 5,
    "EXPANDING_EXIT": 6,
    "capital_increase": 6,
    "policy_regulation": 0,
}


def signal_to_stage(signal_type: str, text: str = "") -> str:
    low = (text or "").lower()
    if any(k in low for k in ("khánh thành", "vận hành", "đi vào hoạt động", "试产", "投产", "mass production")):
        return "OPERATING"
    if any(k in low for k in ("khởi công", "động thổ", "奠基", "开工", "动工", "groundbreaking")):
        return "CONSTRUCTING"
    if any(k in low for k in ("mở rộng", "tăng vốn", "bổ sung vốn", "扩产", "增资", "并购", "sáp nhập", "m&a")):
        return "EXPANDING_EXIT"
    if any(k in low for k in ("đtm", "báo cáo đánh giá tác động môi trường", "giấy phép môi trường", "环评", "排污许可")):
        return "EIA_CONSULTED"
    if any(k in low for k in ("giao đất", "thuê đất", "giải phóng mặt bằng", "供地", "征地", "清表", "签约土地")):
        return "SITE_CLEARANCE"
    mapping = {
        "eia_approval": "EIA_CONSULTED",
        "land_grant": "SITE_CLEARANCE",
        "ground_breaking": "CONSTRUCTING",
        "capital_increase": "EXPANDING_EXIT",
        "factory_setup": "IRC_APPROVED",
        "investment_mou": "investment_mou",
    }
    return mapping.get(signal_type, "IRC_APPROVED")


def _fingerprint(url: str, title: str) -> str:
    norm = re.sub(r"\s+", " ", f"{url.strip().lower()}|{title.strip().lower()}")
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:24]


class EventLedger:
    def __init__(self, db_path: str = DEFAULT_V2_PROJECTS_DB, seed_from_v1: bool = True):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if seed_from_v1 and not os.path.exists(self.db_path) and os.path.exists(V1_SEED_DB):
            shutil.copy2(V1_SEED_DB, self.db_path)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    project_name_cn TEXT,
                    investor_name TEXT,
                    parent_company TEXT,
                    origin_country TEXT,
                    province TEXT,
                    district_commune TEXT,
                    industrial_park TEXT,
                    sector TEXT,
                    scale_capacity TEXT,
                    current_stage TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS project_timeline (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    event_date TEXT,
                    stage TEXT NOT NULL,
                    title TEXT NOT NULL,
                    snippet TEXT,
                    source_id TEXT,
                    source_name TEXT,
                    raw_fingerprint TEXT,
                    url TEXT
                );
                CREATE TABLE IF NOT EXISTS reported_briefing_items (
                    fingerprint TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    briefing_date TEXT NOT NULL,
                    project_id TEXT,
                    milestone_stage TEXT,
                    reported_at TEXT
                );
                CREATE TABLE IF NOT EXISTS historical_macro_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_date TEXT,
                    registered_usd_bn REAL,
                    disbursed_usd_bn REAL,
                    source_file TEXT,
                    summary TEXT
                );
                """
            )
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        with self._connect() as conn:
            return {
                "projects": conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
                "timeline_events": conn.execute("SELECT COUNT(*) FROM project_timeline").fetchone()[0],
                "reported_items": conn.execute("SELECT COUNT(*) FROM reported_briefing_items").fetchone()[0],
            }

    def is_already_reported(self, url: str = "", title: str = "") -> bool:
        fp = _fingerprint(url, title)
        low_url = (url or "").strip().lower()
        low_title = re.sub(r"\s+", " ", (title or "").strip().lower())
        with self._connect() as conn:
            if low_url:
                row = conn.execute(
                    "SELECT 1 FROM reported_briefing_items WHERE lower(url) = ? LIMIT 1",
                    (low_url,),
                ).fetchone()
                if row:
                    return True
            if low_title and len(low_title) >= 12:
                row = conn.execute(
                    "SELECT 1 FROM reported_briefing_items WHERE fingerprint = ? OR lower(title) = ? LIMIT 1",
                    (fp, low_title),
                ).fetchone()
                if row:
                    return True
        return False

    def lookup_historical_context(
        self,
        title: str,
        entity: str = "",
        province: str = "",
        candidate_stage: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        反向检索 V2 历史项目库：匹配关键企业名/项目词，判定是否为既有跟踪项目的最新进展 (is_follow_up)
        并校验生命周期阶段是否发生倒退 (stage_regression)。
        """
        text = f"{entity} {title}"
        # Extract meaningful proper tokens (>=4 chars) excluding generic noise words
        stopwords = {
            "vietnam", "viet", "nam", "project", "company", "limited", "investment",
            "industrial", "park", "cong", "ty", "tnhh", "du", "an", "dau", "tu",
            "khu", "nghiep", "tinh", "thanh", "pho", "bao", "cao", "moi", "truong",
            "nghi", "dinh", "quyet", "nha", "may", "san", "xuat", "股份", "有限",
            "公司", "关于", "越南", "公告", "投资", "项目",
            "quan", "trac", "chat", "luong", "ket", "qua", "xuc", "tien", "cum",
            "mo", "rong", "quy", "dong", "trieu", "ty", "giay", "phep", "de", "xuat",
            "ha", "tang", "phat", "trien", "thu", "tuc", "cap", "nhat", "thong",
            "bac", "trung", "bo", "nam", "tay", "hai", "hung", "yen", "phong", "hoa",
            "group", "corp", "holdings", "joint", "stock", "bank", "energy", "power",
        }
        tokens: List[str] = []
        # Match proper-case Latin entity tokens (capitalized, len>=4) or CJK company names (len>=2)
        for raw_tok in re.findall(r"\b[A-ZÀ-Ỹ][A-Za-zÀ-ỹ0-9-]{3,}\b|[\u4e00-\u9fff]{2,6}", text):
            if raw_tok.lower() not in stopwords and raw_tok not in tokens and len(tokens) < 6:
                tokens.append(raw_tok)
        if not tokens:
            return None

        cand_rank = STAGE_RANK.get(candidate_stage, 1)
        with self._connect() as conn:
            for tok in tokens:
                like = f"%{tok}%"
                rows = conn.execute(
                    """
                    SELECT project_id, project_name, project_name_cn, investor_name,
                           parent_company, province, industrial_park, current_stage, updated_at
                    FROM projects
                    WHERE investor_name LIKE ? OR parent_company LIKE ? OR project_name LIKE ? OR project_name_cn LIKE ?
                    ORDER BY updated_at DESC
                    LIMIT 5
                    """,
                    (like, like, like, like),
                ).fetchall()
                for row in rows:
                    if province and row["province"]:
                        p_low = row["province"].lower()
                        if p_low not in province.lower() and province.lower().split("(")[0].strip() not in p_low:
                            continue
                    prev_stage = row["current_stage"] or ""
                    prev_rank = STAGE_RANK.get(prev_stage, 0)
                    last_ev = conn.execute(
                        "SELECT event_date, title FROM project_timeline WHERE project_id = ? ORDER BY event_date DESC LIMIT 1",
                        (row["project_id"],),
                    ).fetchone()
                    return {
                        "matched_token": tok,
                        "project_id": row["project_id"],
                        "project_name": row["project_name_cn"] or row["project_name"],
                        "investor_name": row["investor_name"] or "",
                        "province": row["province"] or "",
                        "industrial_park": row["industrial_park"] or "",
                        "previous_stage": prev_stage,
                        "previous_rank": prev_rank,
                        "candidate_rank": cand_rank,
                        "is_progression": cand_rank > prev_rank,
                        "is_regression": cand_rank < prev_rank and cand_rank > 0,
                        "last_event_date": last_ev["event_date"] if last_ev else "",
                        "last_event_title": last_ev["title"] if last_ev else "",
                    }
        return None

    def record_briefing_delivery(
        self,
        curated_items: List[Any],
        briefing_date: str,
    ) -> int:
        """将已确认交付的简报条目写入已报去重表（V2 本地库）。"""
        now_iso = datetime.now(timezone.utc).isoformat()
        inserted = 0
        with self._connect() as conn:
            for item in curated_items:
                urls = getattr(item, "verified_urls", None) or []
                primary_url = urls[0] if urls else ""
                title = getattr(item, "title_zh", "") or ""
                col = getattr(item, "column", "macro_policy")
                if not title or not primary_url:
                    continue
                fp = _fingerprint(primary_url, title)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO reported_briefing_items
                    (fingerprint, url, title, category, briefing_date, reported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (fp, primary_url, title, col, briefing_date, now_iso),
                )
                inserted += 1
            conn.commit()
        return inserted

    def record_project_milestones(
        self,
        curated_items: List[Any],
        vault: Dict[str, Any],
        briefing_date: str,
        source_names: Optional[Dict[str, str]] = None,
    ) -> Dict[str, int]:
        """将通过门禁的项目/园区/重资产/环评动态增量写回 V2/data/projects.db（跳过 macro_policy）。"""
        asset_columns = {"fdi", "industrial_park", "industry_focus", "legal_approval"}
        now_iso = datetime.now(timezone.utc).isoformat()
        snames = source_names or {}
        projects_created = 0
        projects_updated = 0
        timeline_added = 0

        for item in curated_items:
            col = getattr(item, "column", "macro_policy")
            if col not in asset_columns:
                continue
            ref_ids = getattr(item, "ref_candidate_ids", None) or []
            urls = getattr(item, "verified_urls", None) or []
            primary_url = urls[0] if urls else ""
            title_zh = (getattr(item, "title_zh", "") or "").strip()
            fact_summary = (getattr(item, "fact_summary", "") or "").strip()
            if not title_zh or not primary_url:
                continue

            cand = vault.get(ref_ids[0]) if ref_ids else None
            entity = (getattr(cand, "subject_entity", "") or "").strip() if cand else ""
            geo = (getattr(cand, "geo_location", "") or "").strip() if cand else ""
            sig_type = (getattr(cand, "signal_type", "factory_setup") or "factory_setup") if cand else "factory_setup"
            scale = getattr(cand, "project_scale", None) if cand else None
            src_id = getattr(cand, "source_id", "") if cand else ""
            cand_title = (getattr(cand, "title", "") or title_zh) if cand else title_zh

            stage = signal_to_stage(sig_type, f"{title_zh} {fact_summary} {cand_title}")
            match = self.lookup_historical_context(entity or title_zh, cand_title, geo, stage)

            with self._connect() as conn:
                if match:
                    project_id = match["project_id"]
                    new_stage = stage if match["is_progression"] else (match["previous_stage"] or stage)
                    conn.execute(
                        """
                        UPDATE projects
                        SET current_stage = ?,
                            scale_capacity = COALESCE(NULLIF(scale_capacity, ''), ?),
                            province = COALESCE(NULLIF(province, ''), ?),
                            updated_at = ?
                        WHERE project_id = ?
                        """,
                        (new_stage, scale or "", geo, now_iso, project_id),
                    )
                    projects_updated += 1
                else:
                    seed_key = entity or re.sub(r"\s+", " ", title_zh)[:40]
                    project_id = "PRJ-V2-" + _fingerprint(seed_key, geo)[:12].upper()
                    cur = conn.execute(
                        """
                        INSERT OR IGNORE INTO projects
                        (project_id, project_name, project_name_cn, investor_name, parent_company,
                         origin_country, province, district_commune, industrial_park, sector,
                         scale_capacity, current_stage, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            project_id,
                            cand_title[:200],
                            title_zh[:200],
                            entity[:120],
                            "",
                            "",
                            geo[:80],
                            "",
                            geo[:120] if col == "industrial_park" else "",
                            col,
                            scale or "",
                            stage,
                            now_iso,
                            now_iso,
                        ),
                    )
                    if cur.rowcount > 0:
                        projects_created += 1

                raw_fp = _fingerprint(primary_url, title_zh)
                event_id = "EV-" + raw_fp[:16].upper()
                ev_cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO project_timeline
                    (event_id, project_id, event_date, stage, title, snippet,
                     source_id, source_name, raw_fingerprint, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        project_id,
                        briefing_date,
                        stage,
                        title_zh[:200],
                        fact_summary[:400],
                        src_id,
                        snames.get(src_id, src_id),
                        raw_fp,
                        primary_url,
                    ),
                )
                if ev_cur.rowcount > 0:
                    timeline_added += 1
                conn.commit()

        return {
            "projects_created": projects_created,
            "projects_updated": projects_updated,
            "timeline_events_added": timeline_added,
        }

