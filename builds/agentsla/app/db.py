"""app/db.py — SQLite schema + connection for the AgentSLA substrate.

Implements the ten tables from specs/agentsla/architecture.md:

    tasks, task_versions, architectures, architecture_versions, runs,
    run_components, model_calls, tool_calls, evaluations, cost_events

Raw measurements are never overwritten: model_calls/tool_calls/cost_events are
append-only. `runs` is the only table that receives a final status update when
a run completes (status + success + aggregate metrics), mirroring the spec's
"Never overwrite raw probe measurements" rule.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id        TEXT PRIMARY KEY,
    task_class     TEXT NOT NULL,           -- coding.patch | coding.debug | research.answer
    title          TEXT NOT NULL,
    description    TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_versions (
    task_version_id   TEXT PRIMARY KEY,
    task_id           TEXT NOT NULL REFERENCES tasks(task_id),
    version           INTEGER NOT NULL,
    content_json      TEXT NOT NULL,        -- task seed spec (paths, rubric, seeds)
    environment_hash  TEXT NOT NULL,        -- sha256 of the task directory contents
    created_at        TEXT NOT NULL,
    UNIQUE (task_id, version)
);

CREATE TABLE IF NOT EXISTS architectures (
    architecture_id   TEXT PRIMARY KEY,     -- single_agent | worker_verifier | ...
    name              TEXT NOT NULL,
    description       TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS architecture_versions (
    architecture_version_id TEXT PRIMARY KEY,
    architecture_id         TEXT NOT NULL REFERENCES architectures(architecture_id),
    version                 INTEGER NOT NULL,
    config_json             TEXT NOT NULL,  -- component graph: roles, models, max rounds
    created_at              TEXT NOT NULL,
    UNIQUE (architecture_id, version)
);

CREATE TABLE IF NOT EXISTS runs (
    run_id                TEXT PRIMARY KEY,
    benchmark_id          TEXT NOT NULL,
    architecture_version_id TEXT NOT NULL REFERENCES architecture_versions(architecture_version_id),
    task_version_id       TEXT NOT NULL REFERENCES task_versions(task_version_id),
    attempt               INTEGER NOT NULL,     -- repetition index within the cell
    git_sha               TEXT NOT NULL DEFAULT '',
    environment_hash      TEXT NOT NULL DEFAULT '',
    model_ids             TEXT NOT NULL DEFAULT '[]',   -- json list
    provider_endpoint_ids TEXT NOT NULL DEFAULT '[]',   -- json list
    random_seed           INTEGER,
    started_at            TEXT,
    completed_at          TEXT,
    status                TEXT NOT NULL DEFAULT 'running',  -- running|success|failure|error
    success               INTEGER,              -- NULL until graded
    failure_reason        TEXT,
    cost_usd              REAL,
    duration_seconds      REAL,
    input_tokens          INTEGER,
    output_tokens         INTEGER,
    tool_calls            INTEGER,
    retries               INTEGER,
    model_calls           INTEGER
);

CREATE TABLE IF NOT EXISTS run_components (
    run_component_id  TEXT PRIMARY KEY,
    run_id            TEXT NOT NULL REFERENCES runs(run_id),
    role              TEXT NOT NULL,          -- worker|verifier|planner|judge|critic
    component_index   INTEGER NOT NULL,
    model_id          TEXT NOT NULL DEFAULT '',
    started_at        TEXT,
    completed_at      TEXT,
    status            TEXT NOT NULL DEFAULT 'running',
    detail_json       TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS model_calls (
    model_call_id        TEXT PRIMARY KEY,
    run_id               TEXT NOT NULL REFERENCES runs(run_id),
    run_component_id     TEXT NOT NULL REFERENCES run_components(run_component_id),
    seq                  INTEGER NOT NULL,
    model_id             TEXT NOT NULL,
    provider_endpoint_id TEXT NOT NULL DEFAULT '',
    prompt_tokens        INTEGER NOT NULL DEFAULT 0,
    completion_tokens    INTEGER NOT NULL DEFAULT 0,
    reasoning_tokens     INTEGER NOT NULL DEFAULT 0,
    total_tokens         INTEGER NOT NULL DEFAULT 0,
    duration_ms          INTEGER NOT NULL DEFAULT 0,
    status               TEXT NOT NULL,        -- ok|error|retried
    retries              INTEGER NOT NULL DEFAULT 0,
    error                TEXT,
    requested_at         TEXT,
    completed_at         TEXT,
    raw_usage_json       TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tool_calls (
    tool_call_id   TEXT PRIMARY KEY,
    run_id         TEXT NOT NULL REFERENCES runs(run_id),
    model_call_id  TEXT NOT NULL REFERENCES model_calls(model_call_id),
    seq            INTEGER NOT NULL,
    tool_name      TEXT NOT NULL,
    arguments_json TEXT NOT NULL DEFAULT '{}',
    result_state   TEXT NOT NULL,          -- ok|error
    result_summary TEXT NOT NULL DEFAULT '',
    duration_ms    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id TEXT PRIMARY KEY,
    run_id        TEXT NOT NULL REFERENCES runs(run_id),
    evaluator     TEXT NOT NULL,           -- graders/pytest-v1 | graders/diffscope-v1 | graders/kb-v1
    passed        INTEGER NOT NULL,
    score         REAL,
    detail_json   TEXT NOT NULL DEFAULT '{}',
    evaluated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_events (
    cost_event_id        TEXT PRIMARY KEY,
    run_id               TEXT NOT NULL REFERENCES runs(run_id),
    model_call_id        TEXT REFERENCES model_calls(model_call_id),
    kind                 TEXT NOT NULL,     -- inference|retry
    basis                TEXT NOT NULL,     -- price_table_estimate|provider_reported
    model_id             TEXT NOT NULL,
    input_tokens         INTEGER NOT NULL DEFAULT 0,
    output_tokens        INTEGER NOT NULL DEFAULT 0,
    unit_price_input     REAL,
    unit_price_output    REAL,
    amount_usd           REAL NOT NULL,
    recorded_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_cell ON runs(architecture_version_id, task_version_id);
CREATE INDEX IF NOT EXISTS idx_model_calls_run ON model_calls(run_id);
CREATE INDEX IF NOT EXISTS idx_cost_events_run ON cost_events(run_id);
CREATE INDEX IF NOT EXISTS idx_evals_run ON evaluations(run_id);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open (creating schema if needed) and return a SQLite connection.

    FastAPI/uvicorn in threaded mode wants check_same_thread=False; the CLI
    uses a single thread so it does not matter.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def table_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r["name"] for r in rows]