import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/root/venturelab/builds/agentsla")

tmp = Path(tempfile.mkdtemp(prefix="dbg_env_"))
os.environ["AGENTSLA_RUNS_DIR"] = str(tmp)
os.environ["AGENTSLA_DB"] = str(tmp / "db" / "agentsla.db")
import importlib
import app.evidence
import app.runner

app.evidence.RUNS_ROOT = tmp
app.runner.DBPATH = tmp / "db" / "agentsla.db"

from app.db import connect  # noqa: E402
from app.fake import MATHLIB_FIX, make_scripted_client  # noqa: E402
from app.runner import run_cell  # noqa: E402


def test_dbg_env():
    os.environ["AGENTSLA_RUNS_DIR"] = str(tmp)
    conn = connect(tmp / "db" / "agentsla.db")
    client = make_scripted_client("deepseek-v4-flash", MATHLIB_FIX)[0]
    manifest = run_cell(conn, benchmark_id="dbg-env", task_class="coding.patch",
                        architecture_id="single_agent",
                        arch_config={"components": [{"role": "worker", "model": "deepseek-v4-flash", "max_steps": 6}], "max_steps": 6},
                        client=client, attempt=1, base_url="stub://", git_sha="")
    print("success:", manifest["success"], "cost:", manifest["cost_usd"])
    rid = manifest["run_id"]
    envdir = tmp / rid
    print("envdir:", envdir, "exists:", envdir.exists())
    events = [json.loads(l) for l in (envdir / "results.jsonl").read_text().splitlines() if l.strip()]
    print("nevents:", len(events))
    for e in events[:5]:
        print("-", e.get("kind"), list(e.keys())[:6])
    print("any cost:", any("cost" in e for e in events))
    assert True