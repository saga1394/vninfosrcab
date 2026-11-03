# -*- coding: utf-8 -*-
"""
Delta Exporter for Stage 2 Cognitive Layer.
Extracts unanalyzed raw records from collector.db that have not yet been
processed into projects.db (dimensional_signals or project_timeline).
"""

import os
import sys
import json
import sqlite3

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAW_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily", "collector.db"))
STAGE2_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "stage2", "projects.db"))
DELTA_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily", "pending_delta.json"))

def init_stage2_schema():
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dim_code ON dimensional_signals(dimension_code);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dim_fp ON dimensional_signals(raw_fingerprint);")
    conn.commit()
    conn.close()

def export_delta(limit: int = 30):
    init_stage2_schema()
    
    # 1. Get all fingerprints already processed in dimensional_signals
    conn_s2 = sqlite3.connect(STAGE2_DB_PATH)
    cur_s2 = conn_s2.cursor()
    cur_s2.execute("SELECT raw_fingerprint FROM dimensional_signals;")
    processed_fps = set(row[0] for row in cur_s2.fetchall())
    conn_s2.close()

    # 2. Query raw_materials for unprocessed records
    conn_raw = sqlite3.connect(RAW_DB_PATH)
    cur_raw = conn_raw.cursor()
    cur_raw.execute("""
    SELECT fingerprint, source_id, source_name, category, tier, province, dimension_hints, title, pub_date, snippet, url
    FROM raw_materials
    ORDER BY pub_date DESC, fetched_at DESC;
    """)
    rows = cur_raw.fetchall()
    conn_raw.close()

    unprocessed = []
    for r in rows:
        fp = r[0]
        if fp not in processed_fps:
            unprocessed.append({
                "fingerprint": r[0],
                "source_id": r[1],
                "source_name": r[2],
                "category": r[3],
                "tier": r[4],
                "province": r[5],
                "dimension_hints": json.loads(r[6]) if r[6] else [],
                "title": r[7],
                "pub_date": r[8],
                "snippet": r[9],
                "url": r[10]
            })

    # Pick top batch (or all up to limit)
    batch = unprocessed[:limit]
    with open(DELTA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

    print(f"📦 [Delta Exporter] Total raw records: {len(rows)} | Already classified: {len(processed_fps)} | Pending: {len(unprocessed)}")
    print(f"   Exported {len(batch)} pending items to {DELTA_JSON_PATH}")
    return batch

if __name__ == "__main__":
    export_delta()
