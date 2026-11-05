# -*- coding: utf-8 -*-
"""
Cognitive Curation Engine for Vietnam Industrial & Investment Intelligence.
Architectural Contract:
- Data Plumbing: Handled via scripts/pipeline/extract_delta.py (DB queries, 200 pinging, ledger check).
- Cognitive Curation: Performed by the LLM Agent (translation, 5-category taxonomy, [事实]/[看点] synthesis).
- Interface: curation_engine.py reads and validates data/daily/curated_today.json, or coordinates delta extraction.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

CURATED_JSON_PATH = BASE_DIR / "data" / "daily" / "curated_today.json"
DELTA_JSON_PATH = BASE_DIR / "data" / "daily" / "delta_candidates.json"

from scripts.pipeline.state_ledger import is_already_reported, generate_item_fingerprint
from scripts.pipeline.extract_delta import extract_delta_candidates


VALID_CATEGORIES = ["FDI", "INDUSTRIAL_PARKS", "SECTORS", "APPROVALS", "MACRO_MARKET"]


def load_curated_intelligence() -> List[Dict[str, Any]]:
    """Loads and validates the LLM-curated briefing items from data/daily/curated_today.json."""
    if not CURATED_JSON_PATH.exists():
        print(f"[WARN] {CURATED_JSON_PATH} does not exist yet. Please run LLM curation on delta_candidates.json.")
        return []

    try:
        with open(CURATED_JSON_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to parse {CURATED_JSON_PATH}: {e}")
        return []

    # Validate items
    valid_items = []
    for it in items:
        cat = it.get("category")
        title = it.get("title", "").strip()
        url = it.get("url", "").strip()
        if not cat or cat not in VALID_CATEGORIES:
            print(f"[WARN] Invalid category '{cat}' for item: {title}")
            continue
        if not title or not url:
            continue

        # Ensure fingerprint
        if not it.get("fingerprint"):
            it["fingerprint"] = generate_item_fingerprint(url, title)

        valid_items.append(it)

    return valid_items


def curate_daily_intelligence(max_items: int = 20) -> List[Dict[str, Any]]:
    """
    Primary interface for the daily pipeline.
    Loads today's LLM-curated intelligence from data/daily/curated_today.json.
    If curated_today.json is empty or missing, ensures delta candidates are extracted.
    """
    items = load_curated_intelligence()
    if items:
        print(f"[CURATION] Loaded {len(items)} LLM-curated intelligence items from {CURATED_JSON_PATH}.")
        return items[:max_items]

    # If no curated items exist, trigger delta extraction to prepare for LLM review
    print("[CURATION] No existing curated_today.json found. Extracting candidate delta...")
    candidates = extract_delta_candidates(days=3, max_pool=120)
    print(f"[CURATION] Exported {len(candidates)} candidates to {DELTA_JSON_PATH} for LLM cognitive processing.")
    return []


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Vietnam Intelligence Curation Engine")
    parser.add_argument("--export-delta", action="store_true", help="Extract fresh candidate delta to delta_candidates.json")
    parser.add_argument("--validate", action="store_true", help="Validate curated_today.json")
    args = parser.parse_args()

    if args.export_delta:
        cands = extract_delta_candidates(days=3, max_pool=120)
        print(f"Extracted {len(cands)} candidates.")
    else:
        curated = curate_daily_intelligence()
        print(f"Curated items loaded: {len(curated)}")
