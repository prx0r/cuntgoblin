"""app/runner.py — executes task × architecture cells and records everything.

Pipeline (spec): TASK DATASET -> RUN MANIFEST -> ARCHITECTURE -> RUNNER ->
execution trace -> GRADER -> success/failure -> COST ACCOUNTING -> SLA DB.

Architectures implemented:
  single_agent                 one worker with tools
  worker_verifier              worker + advisory LLM verifier (deterministic gate decides)
  planner_worker               planner emits a plan, worker executes
  parallel_candidates_judge    N workers -> deterministic graded selection (no LLM judge)

Every model call, tool call, retry and evaluation lands in the SQLite SLA DB
and in the run's evidence envelope (data/runs/<run_id>). Cost events keep
their basis (price_table_estimate vs provider_reported).

The grading function is ALWAYS the deterministic grader from app/grader.py.
LLM outputs (verifier verdicts, plans) are advisory only — AI proposes, the
gate disposes.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .client import ChatResult, LLMClient, ModelClient
from .cost import record_inference_cost, run_totals
from .dataset import kb_payload, task_spec
from .evidence import RunEnvelope
from .grader import (
    apply_unified_diff,
    extract_diff_block,
    grade_coding,
    grade_research,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def db_path() -> Path:
    """Database path; AGENTSLA_DB env overrides (tests use tmp dirs)."""
    return Path(os.environ.get("AGENTSLA_DB", str(BASE_DIR / "data" / "agentsla.db")))


DB_PATH = db_path()

CODING_CLASSES = {"coding.patch", "coding.debug"}
RESEARCH_CLASS = "research.answer"

_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file inside the task working directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files inside the task working directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_patch",
            "description": "Submit the final unified diff for grading. Call once when done.",
            "parameters": {
                "type": "object",
                "properties": {"diff": {"type": "string"}},
                "required": ["diff"],
            },
        },
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR), capture_output=True, text=True, timeout=5
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:
        return ""


def _short() -> str:
    return uuid.uuid4().hex[:10]


def _apply_(workdir: Path, diff: str) -> tuple[bool, str]:
    return apply_unified_diff(workdir, diff)


# ------------------------------------------------------------ workspace


class TaskWorkspace:
    """A private copy of the task seed files the agent may freely edit."""

    def __init__(self, task_dir: Path):
        self._tmp = tempfile.TemporaryDirectory(prefix="agentsla_ws_")
        self.dir = Path(self._tmp.name)
        shutil.copytree(task_dir, self.dir, dirs_exist_ok=True)

    def read_file(self, rel: str) -> str:
        path = (self.dir / rel).resolve()
        if not str(path).startswith(str(self.dir)):
            return "ERROR: path escapes workspace"
        if not path.exists():
            return f"ERROR: no such file: {rel}"
        return path.read_text(encoding="utf-8", errors="replace")[:6000]

    def list_dir(self, rel: str = ".") -> str:
        path = (self.dir / rel).resolve()
        if not str(path).startswith(str(self.dir)):
            return "ERROR: path escapes workspace"
        if not path.exists():
            return f"ERROR: no such directory: {rel}"
        return "\n".join(sorted(p.name + ("/" if p.is_dir() else "") for p in path.iterdir()))

    def close(self) -> None:
        self._tmp.cleanup()


# ------------------------------------------------------------ recording


class Recording:
    """Accumulates raw rows for one run and flushes them to DB + envelope."""

    def __init__(self, conn, envelope: RunEnvelope):
        self.conn = conn
        self.env = envelope
        self.run_id = envelope.run_id
        self.model_calls = 0
        self.tool_calls = 0
        self.retries = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.last_mc_id = ""

    def model_call(
        self,
        component_id: str,
        seq: int,
        model_id: str,
        endpoint: str,
        result: ChatResult,
    ) -> str:
        mc_id = f"mc_{_short()}"
        self.conn.execute(
            """INSERT INTO model_calls
               (model_call_id, run_id, run_component_id, seq, model_id,
                provider_endpoint_id, prompt_tokens, completion_tokens,
                reasoning_tokens, total_tokens, duration_ms, status, retries,
                error, requested_at, completed_at, raw_usage_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                mc_id, self.run_id, component_id, seq, model_id, endpoint,
                result.prompt_tokens, result.completion_tokens,
                result.reasoning_tokens, result.total_tokens,
                result.duration_ms, result.status, result.retries, result.error,
                _now(), _now(),
                json.dumps(result.raw.get("usage") or {}),
            ),
        )
        self.conn.commit()
        self.model_calls += 1
        self.retries += result.retries
        self.input_tokens += result.prompt_tokens
        self.output_tokens += result.completion_tokens
        row = record_inference_cost(
            self.conn,
            run_id=self.run_id,
            model_call_id=mc_id,
            model_id=model_id,
            input_tokens=result.prompt_tokens,
            output_tokens=result.completion_tokens,
            provider_cost=result.provider_cost,
        )
        self.env.event("model_call", {
            "model_call_id": mc_id,
            "seq": seq,
            "model_id": model_id,
            "status": result.status,
            "retries": result.retries,
            "tokens": {
                "prompt": result.prompt_tokens,
                "completion": result.completion_tokens,
                "total": result.total_tokens,
            },
            "cost_event": row["cost_event_id"],
            "amount_usd": row["amount_usd"],
            "basis": row["basis"],
        })
        self.last_mc_id = mc_id
        return mc_id

    def tool_call(self, model_call_id: str, seq: int, name: str, args: dict, ok: bool, summary: str, ms: int) -> str:
        tc_id = f"tc_{_short()}"
        self.conn.execute(
            """INSERT INTO tool_calls
               (tool_call_id, run_id, model_call_id, seq, tool_name, arguments_json,
                result_state, result_summary, duration_ms)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (tc_id, self.run_id, model_call_id, seq, name, json.dumps(args),
             "ok" if ok else "error", summary[:2000], ms),
        )
        self.conn.commit()
        self.tool_calls += 1
        self.env.event("tool_call", {
            "tool_call_id": tc_id, "tool": name, "ok": ok, "summary": summary[:500],
        })
        return tc_id

    def evaluation(self, evaluator: str, passed: bool, score: float | None, detail: dict) -> str:
        ev_id = f"ev_{_short()}"
        self.conn.execute(
            """INSERT INTO evaluations (evaluation_id, run_id, evaluator, passed, score, detail_json, evaluated_at)
               VALUES (?,?,?,?,?,?,?)""",
            (ev_id, self.run_id, evaluator, 1 if passed else 0, score,
             json.dumps(detail, default=str), _now()),
        )
        self.conn.commit()
        self.env.event("evaluation", {
            "evaluation_id": ev_id, "evaluator": evaluator, "passed": passed, "score": score,
        })
        return ev_id


# ------------------------------------------------------------ components


def _extract_final_patch(text: str, task_class: str) -> str:
    if task_class in CODING_CLASSES:
        diff = extract_diff_block(text)
        return diff or ""
    return text  # research: the answer text itself


# ------------------------------------------------------------ run context


class RunContext:
    def __init__(self, conn, client: ModelClient, envelope: RunEnvelope, task_class: str, seed: int):
        self.conn = conn
        self.client = client
        self.env = envelope
        self.task_class = task_class
        self.seed = seed
        self.rec = Recording(conn, envelope)


# ------------------------------------------------------------ architecture executors


def _make_worker_prompt(task_class: str, task_title: str, task_dir: Path) -> tuple[str, list[dict]]:
    if task_class in CODING_CLASSES:
        readme = (task_dir / "README.md").read_text(encoding="utf-8") if (task_dir / "README.md").exists() else ""
        system = (
            "You are an autonomous coding agent. Inspect the repository in your working "
            "directory, find the bug, and produce a minimal unified diff that fixes it.\n"
            "Rules:\n"
            "1. You may NOT modify anything under tests/ (visible or hidden).\n"
            "2. Use the read_file / list_dir tools to inspect. Finish by calling submit_patch.\n"
            "3. If tool calling is unavailable, end your final message with a fenced ```diff block.\n"
            f"Task: {task_title}\n{readme}"
        )
    else:
        payload = kb_payload(task_dir)
        facts_lines = "\n".join(
            f"[{f['id']}] {f['text']} (refs: {','.join(f.get('refs', []))})" for f in payload["facts"]
        )
        refs_lines = "\n".join(f"[{r['id']}] {r['title']}" for r in payload["references"])
        system = (
            "You answer factual questions using ONLY the knowledge base below. "
            "Rules:\n"
            "1. Answer the question directly in prose.\n"
            "2. End your answer with the fact IDs you used, in a line like: Citations: F01, F05\n"
            "3. NEVER cite an ID that is not in the knowledge base.\n"
            f"QUESTION: {payload['question']}\n\n"
            f"FACTS:\n{facts_lines}\n\nREFERENCES:\n{refs_lines}"
        )
    return system, [{"role": "system", "content": system}]


# ------------------------------------------------------------ run context


def run_worker_component(
    ctx: RunContext,
    component_id: str,
    model_id: str,
    endpoint: str,
    ws: TaskWorkspace,
    task_title: str,
    task_dir: Path,
    max_steps: int,
    extra_messages: list[dict] | None = None,
) -> tuple[str, str]:
    """Execute one worker component; returns (final_text, submitted_patch)."""
    system, messages = _make_worker_prompt(ctx.task_class, task_title, task_dir)
    messages = messages + list(extra_messages or [])
    transcript = list(messages)
    last_text = ""
    for step in range(max_steps):
        result = ctx.client.chat(transcript, tools=_tools_schema, seed=ctx.seed)
        ctx.rec.model_call(component_id, step, model_id, endpoint, result)
        ctx.env.log(f"[worker:{model_id}] step={step} status={result.status} tok={result.total_tokens}")

        if result.status != "ok":
            return result.error, ""

        last_text = result.content or ""
        if result.tool_calls:
            for tc in result.tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name") or ""
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                out = ""
                if name == "submit_patch":
                    diff = args.get("diff") or ""
                    ctx.rec.tool_call(ctx.rec.last_mc_id, ctx.rec.tool_calls, name, args, True, "submitted", 0)
                    return last_text, diff.strip()
                if name == "read_file":
                    out = ws.read_file(args.get("path", ""))
                    ctx.rec.tool_call(ctx.rec.last_mc_id, ctx.rec.tool_calls, name, args, True, out[:300], 0)
                elif name == "list_dir":
                    out = ws.list_dir(args.get("path", "."))
                    ctx.rec.tool_call(ctx.rec.last_mc_id, ctx.rec.tool_calls, name, args, True, out[:300], 0)
                else:
                    ctx.rec.tool_call(ctx.rec.last_mc_id, ctx.rec.tool_calls, name, args, False, "unknown tool", 0)
                transcript.append({
                    "role": "assistant",
                    "content": result.content or "",
                    "tool_calls": [{"id": tc.get("id"), "type": "function", "function": fn}],
                })
                transcript.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "content": out,
                })
        else:
            # Text fallback: worker declares it is done in prose, or the diff
            # is already in the text, or (research) the answer is complete.
            if (
                step == max_steps - 1
                or "submit" in (last_text.lower())
                or "```diff" in last_text
                or ctx.task_class == RESEARCH_CLASS
            ):
                return last_text, _extract_final_patch(last_text, ctx.task_class)
    return last_text, _extract_final_patch(last_text, ctx.task_class)


# ------------------------------------------------------------ architecture executors


def run_verifier(
    ctx: RunContext,
    component_id: str,
    model_id: str,
    endpoint: str,
    task_class: str,
    proposal: str,
) -> tuple[bool, str]:
    """Advisory verifier. Returns (approve, feedback). NEVER the final grader."""
    if task_class in CODING_CLASSES:
        prompt = (
            "You verify a proposed code fix. The submission is a unified diff.\n"
            "Check that it: (1) is a well-formed unified diff, (2) changes only "
            "source files (never tests/), (3) plausibly fixes the described bug "
            "without breaking edge cases (empty input, negatives, floats).\n"
            "Reply either APPROVED or REVISIONS with 2-3 concrete points.\n\n"
            f"TASK: {task_class}\n\nDIFF:\n{proposal[:4000]}"
        )
    else:
        prompt = (
            "You verify a research answer. Check citations syntax (F## IDs) and "
            "that the answer addresses the question. Reply APPROVED or REVISIONS "
            "with concrete points.\n\nANSWER:\n{proposal[:4000]}".format(proposal=proposal)
        )
    result = ctx.client.chat(
        [{"role": "system", "content": prompt}],
        temperature=0.0, seed=ctx.seed, max_tokens=600,
    )
    ctx.rec.model_call(component_id, 0, model_id, endpoint, result)
    ctx.env.log(f"[verifier:{model_id}] status={result.status}")
    verdict = (result.content or "").strip().upper()
    approve = verdict.startswith("APPROVED") or result.status != "ok"
    return approve, result.content or ""


def run_planner(
    ctx: RunContext,
    component_id: str,
    model_id: str,
    endpoint: str,
    task_class: str,
    task_title: str,
    task_dir: Path,
) -> str:
    """Planner emits a step plan (text). Advisory only."""
    system, _ = _make_worker_prompt(task_class, task_title, task_dir)
    prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Before doing anything, produce a short numbered "
         "step-by-step plan (3-6 steps) for solving this task. End with 'PLAN COMPLETE'."},
    ]
    result = ctx.client.chat(prompt, temperature=0.0, seed=ctx.seed, max_tokens=400)
    ctx.rec.model_call(component_id, 0, model_id, endpoint, result)
    ctx.env.log(f"[planner:{model_id}] status={result.status}")
    return result.content or ""


def _finalize_run(
    ctx: RunContext,
    run_row_id: str,
    arch_ver_id: str,
    task_ver_id: str,
    benchmark_id: str,
    task_dir: Path,
    eval_results: list,
    failure_reason: str | None,
    started: float,
    git_sha: str,
    seed: int,
) -> dict:
    totals = run_totals(ctx.conn, ctx.env.run_id)
    tool_count = ctx.conn.execute(
        "SELECT COUNT(*) AS c FROM tool_calls WHERE run_id=?", (ctx.env.run_id,)
    ).fetchone()["c"]
    mc_count = ctx.conn.execute(
        "SELECT COUNT(*) AS c FROM model_calls WHERE run_id=?", (ctx.env.run_id,)
    ).fetchone()["c"]
    retry_count = ctx.conn.execute(
        "SELECT COALESCE(SUM(retries),0) AS c FROM model_calls WHERE run_id=?", (ctx.env.run_id,)
    ).fetchone()["c"]
    success = all(r.passed for r in eval_results) and eval_results and failure_reason is None
    duration = time.monotonic() - started

    ctx.conn.execute(
        """UPDATE runs SET status=?, success=?, failure_reason=?, cost_usd=?,
           duration_seconds=?, input_tokens=?, output_tokens=?, tool_calls=?,
           retries=?, model_calls=?, completed_at=? WHERE run_id=?""",
        (
            "success" if success and failure_reason is None else "failure",
            1 if success else 0,
            failure_reason,
            totals["cost_usd"],
            duration,
            totals["input_tokens"],
            totals["output_tokens"],
            int(tool_count),
            int(retry_count),
            int(mc_count),
            _now(),
            ctx.env.run_id,
        ),
    )
    ctx.conn.commit()

    manifest = {
        "benchmark_id": benchmark_id,
        "architecture_version_id": arch_ver_id,
        "task_version_id": task_ver_id,
        "attempt": _attempt_from_run_id(ctx.env.run_id),
        "git_sha": git_sha,
        "environment_hash": task_spec(ctx.task_class)["environment_hash"],
        "random_seed": seed,
        "status": "success" if success else "failure",
        "success": success,
        "failure_reason": failure_reason,
        "cost_usd": totals["cost_usd"],
        "cost_basis": "price_table_estimate" if totals["table_based_events"] > 0 else "provider_reported",
        "duration_seconds": round(duration, 3),
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
        "tool_calls": int(tool_count),
        "retries": int(retry_count),
        "model_calls": int(mc_count),
        "evaluations": [
            {"evaluator": e.evaluator, "passed": bool(e.passed), "score": e.score} for e in eval_results
        ],
    }
    ctx.env.write_run_json(manifest)
    return manifest


def _attempt_from_run_id(run_id: str) -> int:
    try:
        return int(run_id.rsplit("-a", 1)[1])
    except (IndexError, ValueError):
        return 1


def run_cell(
    conn,
    *,
    benchmark_id: str,
    task_class: str,
    architecture_id: str,
    arch_config: dict,
    client: ModelClient,
    attempt: int = 1,
    base_url: str = "",
    git_sha: str = "",
) -> dict:
    """Run one full cell: one task × one architecture × one attempt.

    Returns the run manifest dict (also recorded in DB + envelope)."""
    spec = task_spec(task_class)
    task_dir = spec["dir"]

    # -- DB rows ---------------------------------------------------------
    conn.execute(
        "INSERT OR IGNORE INTO tasks (task_id, task_class, title, description, created_at) VALUES (?,?,?,?,?)",
        (spec["task_id"], task_class, spec["title"], spec["description"], _now()),
    )
    task_ver_id = f"{spec['task_id']}-v1"
    conn.execute(
        "INSERT OR IGNORE INTO task_versions (task_version_id, task_id, version, content_json, environment_hash, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (task_ver_id, spec["task_id"], 1, json.dumps(spec, default=str), spec["environment_hash"], _now()),
    )
    conn.execute(
        "INSERT OR IGNORE INTO architectures (architecture_id, name, description) VALUES (?,?,?)",
        (architecture_id, architecture_id, arch_config.get("description", "")),
    )
    arch_ver_id = f"{architecture_id}-v1"
    conn.execute(
        "INSERT OR IGNORE INTO architecture_versions (architecture_version_id, architecture_id, version, config_json, created_at) "
        "VALUES (?,?,?,?,?)",
        (arch_ver_id, architecture_id, 1, json.dumps(arch_config, default=str), _now()),
    )

    seed = int(_seed_from(benchmark_id, task_class, architecture_id, str(attempt)))
    run_id = f"{benchmark_id}-{task_class.replace('.', '_')}-{architecture_id}-a{attempt}"
    conn.execute(
        """INSERT INTO runs (run_id, benchmark_id, architecture_version_id, task_version_id, attempt,
           git_sha, environment_hash, model_ids, provider_endpoint_ids, random_seed, started_at,
           status) VALUES (?,?,?,?,?,?,?,?,?,?,'running')""",
        (
            run_id, benchmark_id, arch_ver_id, task_ver_id, attempt, git_sha,
            spec["environment_hash"], json.dumps([_model_of(client)]),
            json.dumps([base_url]), seed, _now(),
        ),
    )
    conn.commit()

    envelope = RunEnvelope(run_id)
    ctx = RunContext(conn, client, envelope, task_class, seed)
    envelope.log(f"cell start task={task_class} arch={architecture_id} attempt={attempt}")
    started = time.monotonic()
    failure_reason: str | None = None

    ws = TaskWorkspace(task_dir)
    eval_results = []
    try:
        # components
        comp_rows: list[tuple[str, str, int]] = []  # (id, role, index)
        components = arch_config.get("components", [])
        # default config if unspecified
        if not components:
            components = [{"role": "worker", "model": _model_of(client), "max_steps": 6}]
        for idx, comp in enumerate(components):
            comp_id = f"rc_{_short()}"
            conn.execute(
                """INSERT INTO run_components (run_component_id, run_id, role, component_index, model_id,
                   started_at, status) VALUES (?,?,?,?,?,?,'running')""",
                (comp_id, run_id, comp.get("role", "worker"), idx, comp.get("model", _model_of(client)), _now()),
            )
            comp_rows.append((comp_id, comp.get("role", "worker"), idx))
        conn.commit()

        roles = {role for _, role, _ in comp_rows}
        role_model = {c["role"]: c.get("model", _model_of(client)) for c in components}
        endpoint = base_url or "openai-compatible"

        if architecture_id == "single_agent":
            comp_id = comp_rows[0][0]
            _, patch = run_worker_component(
                ctx, comp_id, role_model.get("worker", _model_of(client)), endpoint, ws,
                spec["title"], task_dir, arch_config.get("max_steps", 6),
            )
            if ctx.task_class in CODING_CLASSES:
                if not patch:
                    failure_reason = "no_patch_submitted"
                else:
                    try:
                        eval_results = grade_coding(task_dir, patch)
                    except Exception as exc:  # noqa: BLE001 — grader robustness boundary
                        failure_reason = f"grader_error: {exc}"
                envelope.artifact("final.patch", patch)
            else:
                eval_results = grade_research(patch, task_dir)
                envelope.artifact("final.answer.txt", patch)

        elif architecture_id == "worker_verifier":
            comp_ids = {role: cid for cid, role, _ in comp_rows}
            worker_id = comp_ids.get("worker", comp_rows[0][0])
            verifier_id = comp_ids.get("verifier", comp_rows[-1][0])
            final_text, patch = run_worker_component(
                ctx, worker_id, role_model.get("worker", _model_of(client)), endpoint, ws,
                spec["title"], task_dir, arch_config.get("max_steps", 6),
            )
            # verifier loop (advisory)
            approved = False
            feedback = ""
            for round_no in range(arch_config.get("max_rounds", 2)):
                if not patch:
                    break
                approved, feedback = run_verifier(
                    ctx, verifier_id, role_model.get("verifier", role_model.get("worker", _model_of(client))),
                    endpoint, ctx.task_class, patch,
                )
                envelope.event("verifier_round", {"round": round_no, "approved": approved, "feedback": feedback[:500]})
                if approved:
                    break
                # revision: ask worker to revise
                sys_prompt, messages = _make_worker_prompt(ctx.task_class, spec["title"], task_dir)
                messages = messages + [
                    {"role": "user", "content": "Previous submission was sent for revisions with this feedback:\n"
                     f"{feedback[:1500]}\n\nPlease revise the diff. End with your fenced ```diff block."},
                ]
                _, patch = run_worker_component(
                    ctx, worker_id, role_model.get("worker", _model_of(client)), endpoint, ws,
                    spec["title"], task_dir, arch_config.get("max_steps", 3), extra_messages=messages,
                )
            if ctx.task_class in CODING_CLASSES:
                if not patch:
                    failure_reason = "no_patch_submitted"
                else:
                    try:
                        eval_results = grade_coding(task_dir, patch)
                    except Exception as exc:  # noqa: BLE001
                        failure_reason = f"grader_error: {exc}"
                envelope.artifact("final.patch", patch)
            else:
                eval_results = grade_research(patch, task_dir)
                envelope.artifact("final.answer.txt", patch)

        elif architecture_id == "planner_worker":
            comp_ids = {role: cid for cid, role, _ in comp_rows}
            planner_id = comp_ids.get("planner", comp_rows[0][0])
            worker_id = comp_ids.get("worker", comp_rows[-1][0])
            plan = run_planner(
                ctx, planner_id, role_model.get("planner", _model_of(client)), endpoint,
                ctx.task_class, spec["title"], task_dir,
            )
            envelope.event("plan", {"plan": (plan or "")[:2000]})
            sys_prompt, messages = _make_worker_prompt(ctx.task_class, spec["title"], task_dir)
            messages = messages + [
                {"role": "user", "content": "Follow this plan:\n" + (plan or "no plan")[:2000] +
                 "\n\nWhen done, submit the patch (or the answer)."},
            ]
            _, patch = run_worker_component(
                ctx, worker_id, role_model.get("worker", _model_of(client)), endpoint, ws,
                spec["title"], task_dir, arch_config.get("max_steps", 6), extra_messages=messages,
            )
            if ctx.task_class in CODING_CLASSES:
                if not patch:
                    failure_reason = "no_patch_submitted"
                else:
                    try:
                        eval_results = grade_coding(task_dir, patch)
                    except Exception as exc:  # noqa: BLE001
                        failure_reason = f"grader_error: {exc}"
                envelope.artifact("final.patch", patch)
            else:
                eval_results = grade_research(patch, task_dir)
                envelope.artifact("final.answer.txt", patch)

        elif architecture_id == "parallel_candidates_judge":
            comp_ids = {role: cid for cid, role, _ in comp_rows}
            n_candidates = arch_config.get("n_candidates", 3)
            candidates: list[tuple[str, list]] = []  # (patch, eval_results)
            for ci in range(n_candidates):
                worker_id = comp_ids.get(f"worker_{ci}") or comp_ids.get("worker", comp_rows[0][0])
                _, patch = run_worker_component(
                    ctx, worker_id, role_model.get(f"worker_{ci}", role_model.get("worker", _model_of(client))),
                    endpoint, ws, spec["title"], task_dir, arch_config.get("max_steps", 6),
                )
                if ctx.task_class in CODING_CLASSES:
                    if patch:
                        try:
                            evals = grade_coding(task_dir, patch)
                        except Exception as exc:  # noqa: BLE001
                            evals = []
                    else:
                        evals = []
                else:
                    evals = grade_research(patch, task_dir) if patch else []
                candidates.append((patch, evals))
                envelope.event("candidate", {"index": ci, "patch_len": len(patch),
                                             "passed": [e.passed for e in evals]})
            # deterministic judge: pick candidate passing all checks; else best score
            best = None
            for patch, evals in candidates:
                if evals and all(e.passed for e in evals):
                    best = (patch, evals)
                    break
            if best is None:
                best = max(candidates, key=lambda c: (sum(1 for e in c[1] if e.passed), len(c[1])))
            patch, eval_results = best
            if ctx.task_class in CODING_CLASSES:
                if not patch:
                    failure_reason = "no_patch_submitted"
                envelope.artifact("final.patch", patch)
                envelope.artifact("candidates.json", [
                    {"index": i, "passed": [e.passed for e in ev], "evaluators": [e.evaluator for e in ev]}
                    for i, (p, ev) in enumerate(candidates)
                ])
            else:
                envelope.artifact("final.answer.txt", patch)
        else:
            failure_reason = f"unknown_architecture:{architecture_id}"
    except Exception as exc:  # noqa: BLE001 — run must always finalize
        failure_reason = f"runner_error: {exc.__class__.__name__}: {str(exc)[:300]}"
        ctx.env.log(f"RUNNER ERROR {exc!r}")
    finally:
        ws.close()

    for ev in eval_results:
        ctx.rec.evaluation(ev.evaluator, ev.passed, ev.score, ev.detail)
        ctx.env.log(f"[grader:{ev.evaluator}] passed={ev.passed} score={ev.score}")

    manifest = _finalize_run(
        ctx, run_id, arch_ver_id, task_ver_id, benchmark_id, task_dir, eval_results,
        failure_reason, started, git_sha, seed,
    )
    return manifest


def _seed_from(*parts: str) -> int:
    import hashlib

    raw = "|".join(str(p) for p in parts)
    return int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16)


def _model_of(client: ModelClient) -> str:
    return getattr(client, "model", "unknown")