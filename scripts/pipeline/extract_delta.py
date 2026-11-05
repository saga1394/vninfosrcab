# -*- coding: utf-8 -*-
"""
Extract fresh, reachable, and un-reported raw intelligence candidates (Delta Extraction).
Part of the "人机分工宽" architecture:
- Python script handles data plumbing: DB querying, ledger deduplication, concurrent URL pinging.
- Exports clean candidate pool to data/daily/delta_candidates.json for LLM Cognitive Evaluation.
- Zero keyword butchering, zero language-based discarding.
"""

import os
import sys
import json
import sqlite3
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

RAW_DB_PATH = BASE_DIR / "data" / "daily" / "collector.db"
PROJECTS_DB_PATH = BASE_DIR / "data" / "stage2" / "projects.db"
OUTPUT_DELTA_JSON = BASE_DIR / "data" / "daily" / "delta_candidates.json"

from scripts.pipeline.state_ledger import is_already_reported, get_project_last_reported_milestone
from scripts.pipeline.preflight_gate import verify_url_reachable


def match_project_entity(title: str, snippet: str, projects_cache: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Matches text against known projects in projects.db."""
    full_text = f"{title} {snippet}".lower()
    for p in projects_cache:
        p_name = (p["project_name"] or "").lower()
        investor = (p["investor_name"] or "").lower()
        pid = p["project_id"]

        matched = False
        if p_name and len(p_name) > 3 and p_name in full_text:
            matched = True
        elif investor and len(investor) > 3 and investor in full_text:
            matched = True

        if matched:
            last_milestone = get_project_last_reported_milestone(pid)
            return {
                "is_match": True,
                "project_id": pid,
                "project_name": p["project_name"],
                "project_name_cn": p["project_name_cn"],
                "investor_name": p["investor_name"],
                "province": p["province"],
                "current_stage": p["current_stage"],
                "last_reported_milestone": last_milestone
            }

    return {"is_match": False}


def extract_delta_candidates(days: int = 3, max_pool: int = 150) -> List[Dict[str, Any]]:
    """Extracts un-reported candidate records from collector.db across all source tiers and tests URL reachability."""
    if not RAW_DB_PATH.exists():
        print(f"[ERROR] {RAW_DB_PATH} does not exist.")
        return []

    # 1. Load project cache for entity resolution
    projects_cache = []
    if PROJECTS_DB_PATH.exists():
        conn_p = sqlite3.connect(str(PROJECTS_DB_PATH))
        conn_p.row_factory = sqlite3.Row
        cur_p = conn_p.cursor()
        cur_p.execute("SELECT project_id, project_name, project_name_cn, investor_name, current_stage, province FROM projects;")
        projects_cache = [dict(r) for r in cur_p.fetchall()]
        conn_p.close()

    # 2. Query raw items from collector.db
    conn = sqlite3.connect(str(RAW_DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT fingerprint, source_id, source_name, category, tier, province, title, pub_date, snippet, url, fetched_at
        FROM raw_materials
        ORDER BY fetched_at DESC
        LIMIT 400;
    """)
    rows = cur.fetchall()
    conn.close()

    # 3. Filter out past reported items from state ledger
    unreported_items = []
    seen_urls = set()
    for r in rows:
        d = dict(r)
        url = (d.get("url") or "").strip()
        title = (d.get("title") or "").strip()
        if not url or not title:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        if is_already_reported(url, title):
            continue
        unreported_items.append(d)

    print(f"[DELTA] Found {len(unreported_items)} fresh unique unreported candidates in collector.db.")

    # 4. Concurrent URL verification (keep only live 200 links)
    candidates_to_ping = unreported_items[:max_pool]
    url_status_map = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_item = {
            executor.submit(verify_url_reachable, item["url"], 5.0): item
            for item in candidates_to_ping
        }
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                ok, status, _ = future.result()
                url_status_map[item["url"]] = (ok, status)
            except Exception:
                url_status_map[item["url"]] = (False, 0)

    # 5. Assemble final clean delta candidate list
    final_candidates = []
    idx = 1
    for item in candidates_to_ping:
        u = item["url"]
        ok, status = url_status_map.get(u, (False, 0))
        if not ok:
            continue

        proj_match = match_project_entity(item.get("title", ""), item.get("snippet", ""), projects_cache)

        pub_d = str(item.get("pub_date", ""))
        final_candidates.append({
            "candidate_id": idx,
            "source_id": item.get("source_id", ""),
            "source_name": item.get("source_name", ""),
            "title": item.get("title", "").strip(),
            "pub_date": pub_d,
            "snippet": item.get("snippet", "").strip(),
            "url": u,
            "http_status": status,
            "project_match": proj_match,
            "fetched_at": item.get("fetched_at", "")
        })
        idx += 1

    # 6. Save to delta_candidates.json
    OUTPUT_DELTA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DELTA_JSON, "w", encoding="utf-8") as f:
        json.dump(final_candidates, f, ensure_ascii=False, indent=2)

    print(f"[DELTA] Successfully verified and exported {len(final_candidates)} candidates to {OUTPUT_DELTA_JSON}.")
    return final_candidates


if __name__ == "__main__":
    candidates = extract_delta_candidates(days=3, max_pool=120)
    print(f"\n[SUMMARY] Candidate Pool Ready for LLM Cognitive Review ({len(candidates)} items).")
