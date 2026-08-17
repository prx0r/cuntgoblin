"""app/dataset.py — task dataset registry (spec: TASK DATASET -> RUNNER).

Three supported workloads:

    coding.patch     agent produces a unified diff that fixes a buggy lib
    coding.debug     agent finds the root cause and patches a buggy parser
    research.answer  agent answers from a LOCAL knowledge base with citations

The dataset is fully local and deterministic: graders run in-process/subprocess
and never depend on network or an LLM. environment_hash = sha256 over every
file in the task directory (content-addressed reproducibility).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"


def environment_hash(task_dir: Path) -> str:
    """sha256 over (relative path, content) of every file in task_dir."""
    h = hashlib.sha256()
    for p in sorted(task_dir.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(task_dir).as_posix().encode("utf-8"))
            h.update(b"\x00")
            h.update(p.read_bytes())
            h.update(b"\x00")
    return h.hexdigest()


TASK_CLASSES = {
    "coding.patch": {
        "task_id": "mathlib-median-fix",
        "title": "Fix median bug in mathlib",
        "dir": TASKS_ROOT / "coding_patch" / "mathlib",
        "description": "Produce a minimal unified diff fixing the median function without touching tests.",
    },
    "coding.debug": {
        "task_id": "parse-log-skip-bug",
        "title": "Fix skip=0 handling in parse_log",
        "dir": TASKS_ROOT / "coding_debug" / "parse_log",
        "description": "Find the root cause of dropped skip=0 log lines and patch parse_log.py.",
    },
    "research.answer": {
        "task_id": "kb-founding-facts",
        "title": "Answer founding/capital questions from local KB with citations",
        "dir": TASKS_ROOT / "research_answer" / "kb",
        "description": "Answer from the local fact KB and cite fact IDs.",
    },
}


def task_spec(task_class: str) -> dict:
    if task_class not in TASK_CLASSES:
        raise KeyError(f"unknown task class: {task_class!r}; known: {sorted(TASK_CLASSES)}")
    spec = dict(TASK_CLASSES[task_class])
    spec["environment_hash"] = environment_hash(spec["dir"])
    spec["task_class"] = task_class
    return spec


def kb_payload(kb_dir: Path) -> dict:
    """The knowledge base + question as a prompt payload for research tasks."""
    facts = json.loads((kb_dir / "facts.json").read_text(encoding="utf-8"))
    return {
        "question": facts["question"],
        "facts": facts["facts"],
        "references": json.loads((kb_dir / "references.json").read_text(encoding="utf-8"))["references"],
    }