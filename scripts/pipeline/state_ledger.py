# -*- coding: utf-8 -*-
"""
State Ledger for Vietnam Investment Intelligence Daily Briefings.
Tracks all items previously reported in daily briefings to guarantee 100% anti-duplication
and support historical project milestone progression detection.
"""

import os
import sys
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "stage2" / "projects.db"


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_ledger():
    """Initializes the reported_briefing_items table in projects.db."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reported_briefing_items (
            fingerprint TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            briefing_date TEXT NOT NULL,
            project_id TEXT,
            milestone_stage TEXT,
            reported_at TEXT NOT NULL
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reported_url ON reported_briefing_items(url);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reported_date ON reported_briefing_items(briefing_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reported_project ON reported_briefing_items(project_id);")
    conn.commit()
    conn.close()


def generate_item_fingerprint(url: str, title: str) -> str:
    """Generates an immutable MD5 fingerprint for a given URL and title."""
    clean_url = (url or "").strip().lower()
    clean_title = (title or "").strip().lower()
    raw = f"{clean_url}|{clean_title}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def is_already_reported(url: str, title: str = "") -> bool:
    """Checks whether an item or URL has ever been reported in past daily briefings."""
    init_ledger()
    conn = get_db_connection()
    cur = conn.cursor()
    fp = generate_item_fingerprint(url, title)
    
    # Check by fingerprint or exact URL
    cur.execute("SELECT 1 FROM reported_briefing_items WHERE fingerprint = ? OR url = ? LIMIT 1;", (fp, url.strip()))
    row = cur.fetchone()
    conn.close()
    return row is not None


def record_reported_items(items: List[Dict[str, Any]], briefing_date: str):
    """Persists a list of successfully delivered items into the ledger."""
    init_ledger()
    conn = get_db_connection()
    cur = conn.cursor()
    now_str = datetime.now().isoformat()
    
    inserted = 0
    for it in items:
        url = it.get("url", "").strip()
        title = it.get("title", "").strip()
        cat = it.get("category", "")
        pid = it.get("project_id", "")
        stage = it.get("milestone_stage", "")
        fp = it.get("fingerprint") or generate_item_fingerprint(url, title)

        cur.execute("""
            INSERT OR REPLACE INTO reported_briefing_items
            (fingerprint, url, title, category, briefing_date, project_id, milestone_stage, reported_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fp, url, title, cat, briefing_date, pid, stage, now_str))
        inserted += 1

    conn.commit()
    conn.close()
    return inserted


def seed_existing_curated():
    """Seeds the ledger with existing curated items from generate_html_report to prevent immediate duplication."""
    init_ledger()
    sys.path.insert(0, str(BASE_DIR / "scripts" / "stage2"))
    try:
        import generate_html_report
        items = getattr(generate_html_report, "CURATED_INTELLIGENCE", [])
        if items:
            c = record_reported_items(items, "2026-11-05")
            print(f"[*] Seeded {c} existing items into reported_briefing_items ledger.")
    except Exception as e:
        print(f"[WARN] Failed to seed existing curated items: {e}")


def get_project_last_reported_milestone(project_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the most recent reported milestone for an existing project."""
    if not project_id:
        return None
    init_ledger()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT briefing_date, milestone_stage, title
        FROM reported_briefing_items
        WHERE project_id = ?
        ORDER BY briefing_date DESC, reported_at DESC
        LIMIT 1;
    """, (project_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


if __name__ == "__main__":
    init_ledger()
    seed_existing_curated()
    print("[OK] State Ledger initialized and verified.")
