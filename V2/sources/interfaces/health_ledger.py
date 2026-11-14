"""
V2/sources/interfaces/health_ledger.py
----------------------------------------
基于 SQLite 的 V2 信源全生命周期健康状态账本 (补丁 4)。
与 V1 彻底隔离，独立持久化在 V2/data/state_ledger.db。
自动追踪各信源连续成功/失败次数，并实现 active <-> degraded 自动流转判定。
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Any, Optional

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_LEDGER_DB = os.path.join(V2_ROOT, "data", "state_ledger.db")


class SourceHealthLedger:
    def __init__(self, db_path: str = DEFAULT_LEDGER_DB):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS source_health (
                    source_id TEXT PRIMARY KEY,
                    consecutive_failures INTEGER NOT NULL DEFAULT 0,
                    last_success_at TEXT,
                    last_failure_at TEXT,
                    current_status TEXT NOT NULL DEFAULT 'active',
                    error_msg TEXT DEFAULT '',
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def ensure_source(self, source_id: str, initial_status: str = "active") -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO source_health
                (source_id, consecutive_failures, current_status, updated_at)
                VALUES (?, 0, ?, ?)
                """,
                (source_id, initial_status.lower(), now),
            )
            conn.commit()

    def record_success(self, source_id: str) -> str:
        """记录成功抓取：失败计数清零，恢复 active 状态（除非已 retired/low_freq）。"""
        now = datetime.now(timezone.utc).isoformat()
        self.ensure_source(source_id)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT current_status FROM source_health WHERE source_id = ?",
                (source_id,),
            ).fetchone()
            curr = row["current_status"] if row else "active"
            new_status = curr if curr in ("retired", "low_freq") else "active"

            conn.execute(
                """
                UPDATE source_health
                SET consecutive_failures = 0,
                    last_success_at = ?,
                    current_status = ?,
                    error_msg = '',
                    updated_at = ?
                WHERE source_id = ?
                """,
                (now, new_status, now, source_id),
            )
            conn.commit()
            return new_status

    def record_failure(self, source_id: str, error_msg: str, degrade_threshold: int = 2) -> str:
        """记录单次抓取失败：连续失败次数 >= 阈值时自动降级为 degraded。"""
        now = datetime.now(timezone.utc).isoformat()
        self.ensure_source(source_id)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT consecutive_failures, current_status FROM source_health WHERE source_id = ?",
                (source_id,),
            ).fetchone()
            fails = (row["consecutive_failures"] if row else 0) + 1
            curr = row["current_status"] if row else "active"

            if curr == "retired":
                new_status = "retired"
            elif fails >= degrade_threshold:
                new_status = "degraded"
            else:
                new_status = curr

            conn.execute(
                """
                UPDATE source_health
                SET consecutive_failures = ?,
                    last_failure_at = ?,
                    current_status = ?,
                    error_msg = ?,
                    updated_at = ?
                WHERE source_id = ?
                """,
                (fails, now, new_status, str(error_msg)[:500], now, source_id),
            )
            conn.commit()
            return new_status

    def set_status(self, source_id: str, status: str, reason: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.ensure_source(source_id)
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE source_health
                SET current_status = ?,
                    error_msg = ?,
                    updated_at = ?
                WHERE source_id = ?
                """,
                (status.lower(), reason, now, source_id),
            )
            conn.commit()

    def get_health(self, source_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM source_health WHERE source_id = ?",
                (source_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM source_health").fetchall()
            return {r["source_id"]: dict(r) for r in rows}
