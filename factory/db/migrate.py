"""DB migration — creates/migrates the SQLite schema.

Usage:
    from factory.db.migrate import migrate
    migrate("data/venturelab.db")
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def migrate(db_path: str = "data/venturelab.db") -> None:
    """Apply schema to the database. Idempotent (CREATE IF NOT EXISTS)."""
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(p))
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        schema = _SCHEMA_PATH.read_text()
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def current_version(db_path: str = "data/venturelab.db") -> int | None:
    """Return the latest applied schema version, or None if no version table."""
    p = Path(db_path)
    if not p.exists():
        return None
    conn = sqlite3.connect(str(p))
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
        if cur.fetchone() is None:
            return None
        row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        return row[0] if row and row[0] is not None else None
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()
