"""app/evidence.py — the run envelope (spec section 0, universal substrate).

Every run writes:

    data/runs/<run-id>/
      run.json        final run manifest (all fields, content-addressed)
      stdout.log      append-only human-readable event log
      results.jsonl   append-only machine events (one JSON per event)
      artifacts/      final patch, eval details, transcript.json

run.json carries `sha256` = hash of its own canonical content, proving the
manifest was written by the recorder rather than hand-edited.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

RUNS_ROOT = Path(os.environ.get(
    "AGENTSLA_RUNS_DIR",
    str(Path(__file__).resolve().parent.parent / "data" / "runs"),
))


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def sha256(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


class RunEnvelope:
    """Write-once-many-append artifact directory for one run."""

    def __init__(self, run_id: str, run_dir: Path | None = None):
        self.run_id = run_id
        self.dir = run_dir or (RUNS_ROOT / run_id)
        self.artifacts = self.dir / "artifacts"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(exist_ok=True)

    # -- writes -----------------------------------------------------------

    def write_run_json(self, manifest: dict) -> dict:
        manifest["run_id"] = self.run_id
        manifest["written_at"] = utcnow()
        manifest["sha256"] = sha256(manifest)
        (self.dir / "run.json").write_text(
            canonical_json(manifest) + "\n", encoding="utf-8"
        )
        return manifest

    def log(self, message: str) -> None:
        line = f"{utcnow()} {message}\n"
        with open(self.dir / "stdout.log", "a", encoding="utf-8") as fh:
            fh.write(line)

    def event(self, kind: str, payload: dict) -> None:
        record = {"kind": kind, "ts": utcnow(), **payload}
        with open(self.dir / "results.jsonl", "a", encoding="utf-8") as fh:
            fh.write(canonical_json(record) + "\n")

    def artifact(self, name: str, content: str | dict | list) -> Path:
        path = self.artifacts / name
        if isinstance(content, (dict, list)):
            path.write_text(canonical_json(content) + "\n", encoding="utf-8")
        else:
            path.write_text(str(content), encoding="utf-8")
        return path

    # -- reads ------------------------------------------------------------

    def read_run_json(self) -> dict:
        raw = (self.dir / "run.json").read_text(encoding="utf-8")
        return json.loads(raw)

    def read_events(self) -> list[dict]:
        if not (self.dir / "results.jsonl").exists():
            return []
        return [
            json.loads(line)
            for line in (self.dir / "results.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @staticmethod
    def list_runs(root: Path | None = None) -> list[str]:
        base = root or RUNS_ROOT
        if not base.exists():
            return []
        return sorted(
            d.name for d in base.iterdir()
            if d.is_dir() and (d / "run.json").exists()
        )