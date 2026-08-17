"""app/fake.py — scripted LLM client for offline pipeline tests and demos.

NEVER produces real observations. Its purpose is to verify the harness
(recording, grading, cost accounting, evidence envelope) deterministically
without a network. Real benchmark numbers come only from app/client.LLMClient.
"""
from __future__ import annotations

import json
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

MATHLIB_FIX = """--- a/src/mathlib.py
+++ b/src/mathlib.py
@@ -17,7 +17,7 @@
-    return ordered[mid - 1] + ordered[mid] / 2.0  # ← wrong: missing /2 on the sum
+    return (ordered[mid - 1] + ordered[mid]) / 2.0
"""

PARSE_LOG_FIX = """--- a/src/parse_log.py
+++ b/src/parse_log.py
@@ -38,10 +38,10 @@
-    if "skip=" in stripped:
-        trailing = stripped.split("skip=", 1)[1]
-        if trailing == "0":
-            return None  # ← wrong: skip=0 means "do NOT skip"
+    if "skip=" in stripped:
+        trailing = stripped.split("skip=", 1)[1]
+        if trailing == "1":
+            return None  # only skip=1 lines are dropped
"""

RESEARCH_PERFECT = (
    "Alpha was founded in 1998, which is earlier than Beta (2005). "
    "Alpha was founded in 1998. Gamma Inc is headquartered in Nairobi, "
    "which is the capital of Kenya.\nCitations: F01, F05"
)