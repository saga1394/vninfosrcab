# -*- coding: utf-8 -*-
"""
Signal Persistence Module for Stage 2 Dimensional Intelligence.
Writes structured cognitive layer outputs to projects.db (dimensional_signals).
Enforces 100% evidence closure (raw_fingerprint, source_id, url).
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STAGE2_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "stage2", "projects.db"))

DIMENSION_MAP = {
    "D1": "企业动向与实体变动",
    "D2": "项目实体工程进展",
    "D3": "产业供应链与配套生态",
    "D4": "经营与政策营商环境",
    "D5": "宏观大盘与空间规划",
    "NOISE": "行政公告/招聘过滤"
}

def save_signals(signals: list) -> int:
    os.makedirs(os.path.dirname(STAGE2_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(STAGE2_DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dimensional_signals (
        signal_id TEXT PRIMARY KEY,
        dimension_code TEXT NOT NULL,
        dimension_name TEXT NOT NULL,
        title TEXT NOT NULL,
        summary_insight TEXT NOT NULL,
        entity_name TEXT,
        province TEXT,
        severity_level TEXT,
        pub_date TEXT,
        source_id TEXT NOT NULL,
        source_name TEXT NOT NULL,
        raw_fingerprint TEXT NOT NULL,
        url TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    inserted = 0
    now_str = datetime.now().isoformat()
    for sig in signals:
        d_code = sig.get("dimension_code", "D2")
        d_name = DIMENSION_MAP.get(d_code, "综合动向")
        s_id = sig.get("signal_id") or f"SIG-{d_code}-{sig.get('raw_fingerprint', '')[:8]}"

        cur.execute("""
        INSERT OR REPLACE INTO dimensional_signals (
            signal_id, dimension_code, dimension_name, title, summary_insight,
            entity_name, province, severity_level, pub_date, source_id,
            source_name, raw_fingerprint, url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s_id,
            d_code,
            d_name,
            sig["title"],
            sig.get("summary_insight", ""),
            sig.get("entity_name"),
            sig.get("province"),
            sig.get("severity_level", "MEDIUM"),
            sig.get("pub_date"),
            sig["source_id"],
            sig["source_name"],
            sig["raw_fingerprint"],
            sig["url"],
            now_str
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ [Signal Persistence] Successfully committed {inserted} dimensional signals into {STAGE2_DB_PATH}")
    return inserted

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
            save_signals(data)
