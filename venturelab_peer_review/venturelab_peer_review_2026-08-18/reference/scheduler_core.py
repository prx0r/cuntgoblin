from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

def now():
    return datetime.now(timezone.utc)

class SQLiteJobQueue:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def conn(self):
        c = sqlite3.connect(self.db_path, isolation_level=None)
        c.row_factory = sqlite3.Row
        try:
            c.execute("PRAGMA foreign_keys=ON")
            c.execute("PRAGMA busy_timeout=5000")
            yield c
        finally:
            c.close()

    def claim_next(self, worker_id: str, lease_seconds: int = 300):
        t = now()
        until = t + timedelta(seconds=lease_seconds)
        ts, us = t.isoformat(), until.isoformat()

        with self.conn() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute(
                """
                UPDATE jobs
                SET state='READY', lease_owner=NULL, lease_until=NULL,
                    updated_at=?
                WHERE state IN ('LEASED','RUNNING')
                  AND lease_until IS NOT NULL
                  AND lease_until < ?
                """,
                (ts, ts),
            )
            row = c.execute(
                """
                SELECT j.*
                FROM jobs j
                WHERE j.state='READY'
                  AND NOT EXISTS (
                    SELECT 1
                    FROM job_dependencies d
                    JOIN jobs parent ON parent.id=d.depends_on_job_id
                    WHERE d.job_id=j.id AND parent.state!='SUCCEEDED'
                  )
                ORDER BY j.priority DESC, j.created_at
                LIMIT 1
                """
            ).fetchone()
            if row is None:
                c.execute("COMMIT")
                return None

            changed = c.execute(
                """
                UPDATE jobs
                SET state='LEASED', lease_owner=?, lease_until=?, updated_at=?
                WHERE id=? AND state='READY'
                """,
                (worker_id, us, ts, row["id"]),
            ).rowcount
            if changed != 1:
                c.execute("ROLLBACK")
                return None
            c.execute("COMMIT")
            return dict(row) | {
                "state": "LEASED",
                "lease_owner": worker_id,
                "lease_until": us,
            }
