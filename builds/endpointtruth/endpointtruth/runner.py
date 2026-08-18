"""Probe runner: execute one probe against one endpoint and persist the full
evidence trail per spec section 0:

    data/runs/<run-id>/
        run.json        # run envelope
        stdout.log      # captured probe logs
        results.jsonl   # one Observation envelope per line
        artifacts/      # raw artifacts content-addressed by sha256

Raw probe measurements are INSERT-only in the DB.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from .db import DB
from .probes import Credentials, Probe, load_credentials
from .schema import ProbeResult, new_id, sha256_bytes, utcnow

log = logging.getLogger("endpointtruth.runner")


class Runner:
    def __init__(self, db: DB, runs_root: Optional[str] = None,
                 creds_override: Optional[Credentials] = None):
        self.db = db
        self.runs_root = Path(runs_root or "data/runs")
        self.creds_override = creds_override

    def run_sync(self, endpoint, probe: Probe) -> tuple[str, ProbeResult]:
        """Synchronous convenience wrapper (used by CLI + scheduler)."""
        return asyncio.run(self.run(endpoint, probe))

    async def run(self, endpoint, probe: Probe) -> tuple[str, ProbeResult]:
        run_id = new_id("run")
        started = utcnow()
        run_dir = self.runs_root / run_id
        artifacts_dir = run_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        creds = self.creds_override or load_credentials(endpoint)
        self.db.insert_probe_run(run_id, endpoint.endpoint_id, probe.id, started,
                                 probe_region=endpoint.region, method_version=probe.version)

        # Capture probe logs into stdout.log
        logger = logging.getLogger(f"probe.{probe.id}")
        handler = logging.FileHandler(run_dir / "stdout.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.handlers = [handler]
        logger.propagate = False
        log_lines: list[str] = []

        try:
            result: ProbeResult = await probe.run(endpoint, creds)
        except Exception as e:  # probe must not escape; record as failure
            result = ProbeResult(status="FAILURE", measurements=[], errors=[str(e)])
            log_lines.append(f"ERROR probe crashed: {e}")
        finally:
            handler.flush()
            handler.close()
            if (run_dir / "stdout.log").exists():
                log_lines = (run_dir / "stdout.log").read_text().splitlines()

        # Store raw artifacts
        artifact_paths: list[str] = []
        for i, art in enumerate(result.raw_artifacts):
            try:
                blob = json.dumps(art, default=str).encode("utf-8")
            except Exception:
                blob = str(art).encode("utf-8")
            sha = sha256_bytes(blob)
            fname = f"artifact-{i:03d}-{sha[:8]}.json"
            (artifacts_dir / fname).write_bytes(blob)
            artifact_paths.append(str(artifacts_dir / fname))
            # attach sha to measurements that reference this artifact
            for m in result.measurements:
                if m.artifact_sha256 is None and i == 0:
                    m.artifact_sha256 = sha

        # Persist observations
        n_obs = 0
        with open(run_dir / "results.jsonl", "w") as fh:
            for obs in result.measurements:
                if obs.artifact_sha256 is None and artifact_paths:
                    obs.artifact_sha256 = sha256_bytes(Path(artifact_paths[0]).read_bytes())
                if obs.source_id == "":
                    obs.source_id = run_id
                if obs.method_id == "":
                    obs.method_id = probe.id
                if obs.method_version == "":
                    obs.method_version = probe.version
                if obs.subject_id == "":
                    obs.subject_id = endpoint.endpoint_id
                fh.write(json.dumps(obs.envelope(), default=str) + "\n")
                self.db.insert_observation(obs, run_id)
                n_obs += 1

        status = result.status
        artifact_id = artifact_paths[0] if artifact_paths else None
        self.db.finish_probe_run(run_id, status, artifact_id=artifact_id)

        run_json = {
            "run_id": run_id,
            "endpoint_id": endpoint.endpoint_id,
            "provider": endpoint.provider_id,
            "model": endpoint.model_id,
            "probe": {"id": probe.id, "version": probe.version},
            "started_at": started,
            "completed_at": utcnow(),
            "status": status,
            "probe_status": result.status,
            "measurement_count": n_obs,
            "errors": result.errors,
            "base_url": creds.base_url,   # URL is not secret; headers/keys never stored
            "region": endpoint.region,
            "artifacts": artifact_paths,
        }
        (run_dir / "run.json").write_text(json.dumps(run_json, indent=2, default=str))
        return run_id, result