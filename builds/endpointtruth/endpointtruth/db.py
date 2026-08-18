"""SQLite persistence layer.

Tables per spec (section 'Database'): endpoints, probe_runs,
probe_measurements, endpoint_windows.

Invariant: raw probe measurements are INSERT-only, never updated or deleted.
endpoint_windows is a derived projection and may be recomputed.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable, Optional

from .schema import Endpoint, Observation, utcnow

SCHEMA = """
CREATE TABLE IF NOT EXISTS endpoints (
    endpoint_id            TEXT PRIMARY KEY,
    provider_id            TEXT NOT NULL,
    model_id               TEXT NOT NULL,
    provider_model_name    TEXT NOT NULL,
    base_url               TEXT NOT NULL,
    region                 TEXT NOT NULL DEFAULT '',
    deployment_variant     TEXT NOT NULL DEFAULT '',
    quantization_state     TEXT NOT NULL DEFAULT 'unknown',
    advertised_context_tokens INTEGER,
    tools_advertised       INTEGER NOT NULL DEFAULT 0,
    json_advertised        INTEGER NOT NULL DEFAULT 0,
    pricing_json           TEXT,
    api_key_env            TEXT,
    base_url_env           TEXT,
    discovered_at          TEXT NOT NULL,
    retired_at             TEXT
);
CREATE INDEX IF NOT EXISTS idx_endpoints_provider ON endpoints(provider_id);
CREATE INDEX IF NOT EXISTS idx_endpoints_model ON endpoints(model_id);

CREATE TABLE IF NOT EXISTS probe_runs (
    probe_run_id   TEXT PRIMARY KEY,
    endpoint_id    TEXT NOT NULL REFERENCES endpoints(endpoint_id),
    probe_type     TEXT NOT NULL,
    started_at     TEXT NOT NULL,
    completed_at   TEXT,
    probe_region   TEXT NOT NULL DEFAULT '',
    method_version TEXT NOT NULL DEFAULT '',
    status         TEXT NOT NULL,          -- RUNNING | SUCCESS | FAILURE
    artifact_id    TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_endpoint ON probe_runs(endpoint_id);
CREATE INDEX IF NOT EXISTS idx_runs_started ON probe_runs(started_at);

CREATE TABLE IF NOT EXISTS probe_measurements (
    measurement_id   TEXT PRIMARY KEY,
    probe_run_id     TEXT NOT NULL REFERENCES probe_runs(probe_run_id),
    metric           TEXT NOT NULL,
    value_numeric    REAL,
    value_text       TEXT,
    unit             TEXT NOT NULL DEFAULT '',
    state            TEXT NOT NULL,
    observed_at      TEXT NOT NULL,
    valid_until      TEXT,
    subject_id       TEXT NOT NULL,
    predicate        TEXT NOT NULL,
    confidence       REAL,
    method_id        TEXT,
    method_version   TEXT,
    artifact_sha256  TEXT,
    evidence_selector TEXT,
    source_type      TEXT,
    source_id        TEXT
);
CREATE INDEX IF NOT EXISTS idx_meas_endpoint_time ON probe_measurements(subject_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_meas_metric ON probe_measurements(metric, state);

CREATE TABLE IF NOT EXISTS endpoint_windows (
    endpoint_id     TEXT NOT NULL,
    window_start    TEXT NOT NULL,
    window_end      TEXT NOT NULL,
    samples         INTEGER NOT NULL DEFAULT 0,
    success_rate    REAL,
    reachable_rate  REAL,
    ttft_p50        REAL,
    ttft_p90        REAL,
    ttft_p95        REAL,
    tps_p50         REAL,
    tps_p90         REAL,
    tps_p95         REAL,
    tool_success_rate REAL,
    json_success_rate REAL,
    latest_observed_at TEXT,
    PRIMARY KEY (endpoint_id, window_start, window_end)
);
"""


class DB:
    def __init__(self, path: str):
        self.path = path
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    @contextmanager
    def tx(self):
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # ---- endpoints ----
    def upsert_endpoint(self, ep: Endpoint) -> None:
        with self.tx() as c:
            c.execute(
                """INSERT INTO endpoints (endpoint_id, provider_id, model_id, provider_model_name,
                       base_url, region, deployment_variant, quantization_state,
                       advertised_context_tokens, tools_advertised, json_advertised,
                       pricing_json, api_key_env, base_url_env, discovered_at, retired_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(endpoint_id) DO UPDATE SET
                       provider_model_name=excluded.provider_model_name,
                       base_url=excluded.base_url,
                       advertised_context_tokens=excluded.advertised_context_tokens,
                       tools_advertised=excluded.tools_advertised,
                       json_advertised=excluded.json_advertised,
                       pricing_json=excluded.pricing_json
                """,
                (ep.endpoint_id, ep.provider_id, ep.model_id, ep.provider_model_name,
                 ep.base_url, ep.region, ep.deployment_variant, ep.quantization_state,
                 ep.advertised_context_tokens, int(ep.tools_advertised), int(ep.json_advertised),
                 _pricing_json(ep.pricing), ep.api_key_env, ep.base_url_env, ep.discovered_at,
                 ep.retired_at),
            )

    def get_endpoint(self, endpoint_id: str) -> Optional[Endpoint]:
        row = self.conn.execute(
            "SELECT * FROM endpoints WHERE endpoint_id=?", (endpoint_id,)).fetchone()
        return _row_to_endpoint(row) if row else None

    def list_endpoints(self, provider: Optional[str] = None,
                       model: Optional[str] = None,
                       include_retired: bool = False) -> list[Endpoint]:
        q = "SELECT * FROM endpoints WHERE 1=1"
        args: list = []
        if provider:
            q += " AND provider_id=?"
            args.append(provider)
        if model:
            q += " AND model_id=?"
            args.append(model)
        if not include_retired:
            q += " AND retired_at IS NULL"
        q += " ORDER BY provider_id, model_id"
        rows = self.conn.execute(q, args).fetchall()
        return [_row_to_endpoint(r) for r in rows]

    def count_endpoints(self) -> int:
        return self.conn.execute("SELECT COUNT(*) c FROM endpoints").fetchone()["c"]

    # ---- probe runs ----
    def insert_probe_run(self, run_id: str, endpoint_id: str, probe_type: str,
                         started_at: str, probe_region: str = "",
                         method_version: str = "") -> None:
        with self.tx() as c:
            c.execute(
                """INSERT INTO probe_runs (probe_run_id, endpoint_id, probe_type, started_at,
                       probe_region, method_version, status)
                   VALUES (?,?,?,?,?,?,'RUNNING')""",
                (run_id, endpoint_id, probe_type, started_at, probe_region, method_version))

    def finish_probe_run(self, run_id: str, status: str, artifact_id: Optional[str] = None) -> None:
        with self.tx() as c:
            c.execute(
                "UPDATE probe_runs SET status=?, completed_at=?, artifact_id=? WHERE probe_run_id=?",
                (status, utcnow(), artifact_id, run_id))

    def get_probe_run(self, run_id: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM probe_runs WHERE probe_run_id=?", (run_id,)).fetchone()

    def count_probe_runs(self) -> int:
        return self.conn.execute("SELECT COUNT(*) c FROM probe_runs").fetchone()["c"]

    # ---- observations ----
    def insert_observation(self, obs: Observation, probe_run_id: str) -> str:
        import uuid as _uuid
        mid = f"obs-{_uuid.uuid4().hex[:12]}"
        with self.tx() as c:
            c.execute(
                """INSERT INTO probe_measurements (measurement_id, probe_run_id, metric, value_numeric,
                       value_text, unit, state, observed_at, valid_until, subject_id, predicate,
                       confidence, method_id, method_version, artifact_sha256, evidence_selector,
                       source_type, source_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (mid, probe_run_id, obs.predicate.removeprefix("endpoint."),
                 obs.value_number, obs.value_text, obs.unit, obs.state, obs.observed_at,
                 obs.valid_until, obs.subject_id, obs.predicate, obs.confidence,
                 obs.method_id, obs.method_version, obs.artifact_sha256, obs.evidence_selector,
                 obs.source_type, obs.source_id))
        return mid

    def insert_observation_row(self, probe_run_id: str, metric: str,
                               value_numeric: Optional[float] = None,
                               value_text: Optional[str] = None, unit: str = "",
                               state: str = "UNKNOWN", subject_id: str = "",
                               predicate: Optional[str] = None, confidence: float = 0.98,
                               method_id: str = "", method_version: str = "",
                               artifact_sha256: Optional[str] = None,
                               evidence_selector: str = "$", source_type: str = "probe",
                               source_id: str = "", observed_at: Optional[str] = None,
                               valid_until: Optional[str] = None) -> str:
        obs = Observation(
            subject_id=subject_id or "?",
            predicate=predicate or f"endpoint.{metric}",
            value_number=value_numeric, value_text=value_text, unit=unit, state=state,
            observed_at=observed_at or utcnow(), valid_until=valid_until,
            source_type=source_type, source_id=source_id,
            method_id=method_id, method_version=method_version,
            confidence=confidence, artifact_sha256=artifact_sha256,
            evidence_selector=evidence_selector,
        )
        return self.insert_observation(obs, probe_run_id)

    def count_observations(self) -> int:
        return self.conn.execute("SELECT COUNT(*) c FROM probe_measurements").fetchone()["c"]

    def measurements_for_endpoint(self, endpoint_id: str, metric: Optional[str] = None,
                                  limit: int = 500) -> list[sqlite3.Row]:
        q = "SELECT * FROM probe_measurements WHERE subject_id=?"
        args: list = [endpoint_id]
        if metric:
            # metric column stores the bare metric name (endpoint. prefix stripped
            # at insert); match both forms for compatibility.
            q += " AND (metric=? OR metric=?)"
            args.extend([metric, metric.removeprefix("endpoint.")])
        q += " ORDER BY observed_at DESC LIMIT ?"
        args.append(limit)
        return self.conn.execute(q, args).fetchall()

    def history_for_endpoint(self, endpoint_id: str, metric: Optional[str] = None,
                             limit: int = 1000) -> list[sqlite3.Row]:
        return self.measurements_for_endpoint(endpoint_id, metric, limit)

    def evidence_lookup(self, artifact_sha256: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM probe_measurements WHERE artifact_sha256=? LIMIT 1",
            (artifact_sha256,)).fetchone()

    def metrics_for_window(self, endpoint_id: str, window_start: str, window_end: str) -> dict[str, list[float]]:
        """Raw KNOWN numeric values for aggregating (and boolean flags)."""
        rows = self.conn.execute(
            """SELECT metric, value_numeric, state FROM probe_measurements
               WHERE subject_id=? AND observed_at>=? AND observed_at<? AND value_numeric IS NOT NULL
               ORDER BY observed_at""",
            (endpoint_id, window_start, window_end)).fetchall()
        out: dict[str, list[float]] = {}
        for r in rows:
            out.setdefault(r["metric"], []).append(float(r["value_numeric"]))
        return out

    def probe_success_flags(self, endpoint_id: str, window_start: str, window_end: str) -> list[float]:
        rows = self.conn.execute(
            """SELECT value_numeric FROM probe_measurements
               WHERE subject_id=? AND predicate='probe.success' AND observed_at>=? AND observed_at<?
                   AND value_numeric IS NOT NULL""",
            (endpoint_id, window_start, window_end)).fetchall()
        return [float(r["value_numeric"]) for r in rows]

    def metric_flag_values(self, endpoint_id: str, metric: str,
                           window_start: str, window_end: str) -> list[float]:
        rows = self.conn.execute(
            """SELECT value_numeric FROM probe_measurements
               WHERE subject_id=? AND predicate=? AND observed_at>=? AND observed_at<?
                   AND value_numeric IS NOT NULL""",
            (endpoint_id, f"endpoint.{metric}", window_start, window_end)).fetchall()
        return [float(r["value_numeric"]) for r in rows]

    def flag_values_for_predicate(self, endpoint_id: str, predicate: str,
                                  window_start: str, window_end: str) -> list[float]:
        rows = self.conn.execute(
            """SELECT value_numeric FROM probe_measurements
               WHERE subject_id=? AND predicate=? AND observed_at>=? AND observed_at<?
                   AND value_numeric IS NOT NULL""",
            (endpoint_id, predicate, window_start, window_end)).fetchall()
        return [float(r["value_numeric"]) for r in rows]

    # ---- windows ----
    def upsert_window(self, row: dict) -> None:
        with self.tx() as c:
            c.execute(
                """INSERT INTO endpoint_windows (endpoint_id, window_start, window_end, samples,
                       success_rate, reachable_rate, ttft_p50, ttft_p90, ttft_p95,
                       tps_p50, tps_p90, tps_p95, tool_success_rate, json_success_rate,
                       latest_observed_at)
                   VALUES (:endpoint_id, :window_start, :window_end, :samples,
                       :success_rate, :reachable_rate, :ttft_p50, :ttft_p90, :ttft_p95,
                       :tps_p50, :tps_p90, :tps_p95, :tool_success_rate, :json_success_rate,
                       :latest_observed_at)
                   ON CONFLICT(endpoint_id, window_start, window_end) DO UPDATE SET
                       samples=excluded.samples, success_rate=excluded.success_rate,
                       reachable_rate=excluded.reachable_rate,
                       ttft_p50=excluded.ttft_p50, ttft_p90=excluded.ttft_p90, ttft_p95=excluded.ttft_p95,
                       tps_p50=excluded.tps_p50, tps_p90=excluded.tps_p90, tps_p95=excluded.tps_p95,
                       tool_success_rate=excluded.tool_success_rate,
                       json_success_rate=excluded.json_success_rate,
                       latest_observed_at=excluded.latest_observed_at""",
                row)

    def latest_windows(self, endpoint_ids: Optional[Iterable[str]] = None) -> dict[str, sqlite3.Row]:
        """For each endpoint, the most recent window row."""
        rows = self.conn.execute(
            """SELECT w.* FROM endpoint_windows w
               JOIN (SELECT endpoint_id, MAX(window_end) AS me FROM endpoint_windows GROUP BY endpoint_id) m
                 ON w.endpoint_id=m.endpoint_id AND w.window_end=m.me
               ORDER BY w.endpoint_id""").fetchall()
        by = {r["endpoint_id"]: r for r in rows}
        if endpoint_ids:
            return {eid: by[eid] for eid in endpoint_ids if eid in by}
        return by

    def windows_for_endpoint(self, endpoint_id: str, limit: int = 100) -> list[sqlite3.Row]:
        return self.conn.execute(
            """SELECT * FROM endpoint_windows WHERE endpoint_id=?
               ORDER BY window_end DESC LIMIT ?""", (endpoint_id, limit)).fetchall()


def _pricing_json(pricing: dict) -> Optional[str]:
    import json
    return json.dumps(pricing) if pricing else None


def _row_to_endpoint(row: sqlite3.Row) -> Endpoint:
    import json
    pricing = {}
    if row["pricing_json"]:
        try:
            pricing = json.loads(row["pricing_json"])
        except Exception:
            pricing = {}
    return Endpoint(
        endpoint_id=row["endpoint_id"], provider_id=row["provider_id"],
        model_id=row["model_id"], provider_model_name=row["provider_model_name"],
        base_url=row["base_url"], region=row["region"],
        deployment_variant=row["deployment_variant"],
        quantization_state=row["quantization_state"],
        advertised_context_tokens=row["advertised_context_tokens"],
        tools_advertised=bool(row["tools_advertised"]), json_advertised=bool(row["json_advertised"]),
        pricing=pricing, api_key_env=row["api_key_env"], base_url_env=row["base_url_env"],
        retired_at=row["retired_at"], discovered_at=row["discovered_at"],
    )