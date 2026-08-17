"""app/fake.py — scripted LLM client for offline pipeline tests and demos.

NEVER produces real observations. Its purpose is to verify the harness
(recording, grading, cost accounting, evidence envelope) deterministically
without a network. Real benchmark numbers come only from app/client.LLMClient.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Protocol

from .client import ChatResult  # noqa: F401  (re-exported for tests)


class ModelClient(Protocol):
    """Duck-typed model client: what the runner actually requires."""
    model: str

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=None, seed=None) -> ChatResult: ...

    def close(self) -> None: ...


class FakeClient:
    """Responds according to a scripted callable: fn(messages) -> ChatResult."""

    def __init__(self, model: str = "fake-model", responder: Callable | None = None):
        self.model = model
        self.calls = 0
        self.last_messages: list[dict] = []
        self._responder = responder or (lambda msgs: self._default(msgs))

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=None, seed=None):
        self.calls += 1
        self.last_messages = messages
        return self._responder(messages)

    def close(self):
        pass

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _default(messages) -> ChatResult:
        text = messages[-1]["content"] if messages else ""
        return ChatResult(content=f"stub answer to: {text[:80]}", status="ok",
                          prompt_tokens=11, completion_tokens=7, total_tokens=18)


def make_scripted_client(model: str, patch_text: str = ""):
    """Returns (client, script) where script is a list of responder functions.

    responder[i] maps messages -> ChatResult. If patch_text is given, the
    FIRST worker turn responds with a submit_patch tool call; verifier turns
    respond APPROVED; planner turns respond a plan.
    """
    phase = {"n": 0}

    def worker(messages):
        phase["n"] += 1
        if patch_text:
            return ChatResult(
                content="Submitting the fix.",
                status="ok",
                tool_calls=[
                    {
                        "id": "call_stub_1",
                        "type": "function",
                        "function": {"name": "submit_patch", "arguments": json.dumps({"diff": patch_text})},
                    }
                ],
                prompt_tokens=120, completion_tokens=40, total_tokens=160,
            )
        return ChatResult(content="Here is the answer.\n```diff\n--- a/x\n+++ b/x\n-1\n+2\n```", status="ok",
                          prompt_tokens=100, completion_tokens=30, total_tokens=130)

    def verifier(messages):
        return ChatResult(content="APPROVED", status="ok",
                          prompt_tokens=50, completion_tokens=10, total_tokens=60)

    def planner(messages):
        return ChatResult(content="1. read files\n2. find bug\n3. submit patch\nPLAN COMPLETE", status="ok",
                          prompt_tokens=40, completion_tokens=15, total_tokens=55)

    return FakeClient(model, responder=worker), {"worker": worker, "verifier": verifier, "planner": planner}


# Known-good patch texts for offline pipeline demos (correct fixes).
#
# IMPORTANT: generated with difflib.unified_diff from the ACTUAL task files so
# hunk headers and context lines are always valid for `patch -p1`.

import difflib  # noqa: E402

_TASKS = Path(__file__).resolve().parent.parent / "tasks"


def _unified(task_rel: str, file_rel: str, transform) -> str:
    """Build a unified diff between a task file and its fixed version.

    diff headers use `a/{file_rel}` / `b/{file_rel}` so `patch -p1` inside the
    COPIED task dir (workdir == task root) resolves to workdir/{file_rel}.
    """
    src = (_TASKS / task_rel / file_rel).read_text(encoding="utf-8")
    fixed = transform(src)
    diff = difflib.unified_diff(
        src.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile=f"a/{file_rel}",
        tofile=f"b/{file_rel}",
    )
    return "".join(diff)


def _mathlib_fixed(src: str) -> str:
    return src.replace(
        "return ordered[mid - 1] + ordered[mid] / 2.0  # ← wrong: missing /2 on the sum",
        "return (ordered[mid - 1] + ordered[mid]) / 2.0",
    )


def _parselog_fixed(src: str) -> str:
    """Insert the trailing-fragment handling BEFORE the regex match."""
    old_block = """    m = _LINE_RE.match(stripped)
    if m is None:
        return None
    # BUG: trailing fragment handled too late (the regex already failed for
    # "bytes=512 skip=0" because of the $ anchor) AND the meaning is inverted:
    # a skip=0 fragment makes the line disappear even though it means
    # "do NOT skip".
    if "skip=" in stripped:
        trailing = stripped.split("skip=", 1)[1]
        if trailing == "0":
            return None  # ← wrong: skip=0 means "do NOT skip"
    return LogRecord("""
    new_block = """    m_trail = re.search(r"\sskip=([01])\s*$", stripped)
    if m_trail is not None:
        if m_trail.group(1) == "1":
            return None  # skip=1 lines are excluded
        stripped = re.sub(r"\sskip=[01]\s*$", "", stripped.strip())
    m = _LINE_RE.match(stripped)
    if m is None:
        return None
    return LogRecord("""
    if old_block not in src:
        raise AssertionError("expected buggy parse_log block not found")
    return src.replace(old_block, new_block)


MATHLIB_FIX = _unified("coding_patch/mathlib", "src/mathlib.py", _mathlib_fixed)
PARSE_LOG_FIX = _unified("coding_debug/parse_log", "src/parse_log.py", _parselog_fixed)

RESEARCH_PERFECT = (
    "Alpha was founded in 1998, which is earlier than Beta (2005). "
    "Alpha was founded in 1998. Gamma Inc is headquartered in Nairobi, "
    "which is the capital of Kenya.\nCitations: F01, F05"
)