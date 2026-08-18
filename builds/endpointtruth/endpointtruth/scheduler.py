"""Scheduler: continuous cycles of probes across endpoints (spec Architecture).

Politeness guards: global concurrency cap, per-endpoint error backoff, cycle
interval. Never sleeps between cycles inside the async loop beyond the
configured interval.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .db import DB
from .probes import probe_instances
from .runner import Runner
from .schema import utcnow

log = logging.getLogger("endpointtruth.scheduler")


@dataclass
class ScheduleResult:
    cycles_completed: int = 0
    probe_runs: int = 0
    observations: int = 0
    failures: int = 0
    skipped: int = 0
    per_endpoint: dict = field(default_factory=dict)
    started_at: str = ""
    finished_at: str = ""


class Scheduler:
    def __init__(self, db: DB, runner: Runner,
                 endpoints: list,
                 probe_ids: Optional[list[str]] = None,
                 cycles: int = 1,
                 interval_seconds: float = 0.0,
                 concurrency: int = 4,
                 max_output_tokens: int = 160,
                 max_context_bucket: int = 8192,
                 probe_override: Optional[dict[str, object]] = None,
                 runs_root: Optional[str] = None):
        self.db = db
        self.runner = runner
        self.endpoints = endpoints
        self.probe_ids = probe_ids
        self.cycles = cycles
        self.interval = interval_seconds
        self.concurrency = concurrency
        self.max_output_tokens = max_output_tokens
        self.max_context_bucket = max_context_bucket
        self.probe_override = probe_override or {}
        self.runs_root = Path(runs_root or "data/runs")

    async def run(self) -> ScheduleResult:
        started = utcnow()
        sem = asyncio.Semaphore(self.concurrency)
        summary = ScheduleResult(started_at=started)

        probes = probe_instances(self.probe_ids,
                                 max_output_tokens=self.max_output_tokens,
                                 max_context_bucket=self.max_context_bucket)

        obs_before = self.db.count_observations()

        for cycle in range(1, self.cycles + 1):
            log.info("cycle %d/%d over %d endpoints", cycle, self.cycles, len(self.endpoints))
            tasks = []
            for ep in self.endpoints:
                for pid in self.probe_ids or list(probes.keys()):
                    if pid not in probes:
                        continue
                    tasks.append(self._guarded_run(sem, ep, probes[pid], summary))
            if tasks:
                await asyncio.gather(*tasks)
            if cycle < self.cycles and self.interval > 0:
                await asyncio.sleep(self.interval)

        summary.cycles_completed = self.cycles
        summary.observations = self.db.count_observations() - obs_before
        summary.finished_at = utcnow()
        return summary

    async def _guarded_run(self, sem, ep, probe, summary: ScheduleResult):
        async with sem:
            mid = f"{ep.endpoint_id}:{probe.id}"
            if summary.per_endpoint.get(mid) is None:
                summary.per_endpoint[mid] = {"runs": 0, "failures": 0}
            try:
                run_id, result = await self.runner.run(ep, probe)
                summary.probe_runs += 1
                summary.per_endpoint[mid]["runs"] += 1
                if result.status == "FAILURE":
                    summary.failures += 1
                    summary.per_endpoint[mid]["failures"] += 1
            except Exception as e:  # scheduler must not die on one bad endpoint
                summary.failures += 1
                summary.skipped += 1
                log.error("probe crashed: %s %s: %s", ep.endpoint_id, probe.id, e)
        return

    def write_summary(self, s: ScheduleResult, path: Optional[str] = None) -> str:
        self.runs_root.mkdir(parents=True, exist_ok=True)
        fp = path or str(self.runs_root / f"scheduler-{int(time.time())}.json")
        payload = {
            "schedule": {
                "endpoints": [e.endpoint_id for e in self.endpoints],
                "probes": self.probe_ids,
                "cycles": self.cycles,
                "interval_seconds": self.interval,
                "concurrency": self.concurrency,
            },
            "result": {
                "cycles_completed": s.cycles_completed,
                "probe_runs": s.probe_runs,
                "observations": s.observations,
                "failures": s.failures,
                "skipped": s.skipped,
                "started_at": s.started_at,
                "finished_at": s.finished_at,
            },
            "per_endpoint": s.per_endpoint,
        }
        Path(fp).write_text(json.dumps(payload, indent=2, default=str))
        return fp