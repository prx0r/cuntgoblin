"""LLMClient behavior against a real local HTTP server (threaded, stdlib).

Covers the spec-style edge cases that matter for AgentSLA availability:
  - HTTP 200 with valid chat payload -> usage + cost parsed
  - 429 / 500 -> retried, count recorded, eventually ok
  - persistent 500 -> error after max_retries
  - 404 (model missing) -> hard error, no retry waste
  - cost field parsed: numeric string vs absent
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.client import LLMClient  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    scripted: list = []
    hits = {"total": 0}

    def do_POST(self):
        self.hits["total"] += 1
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")

        if self.scripted:
            status, payload = self.scripted.pop(0)
        else:
            status, payload = 200, _ok_payload(body.get("model", "m"))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, format: str, *args):  # noqa: A002 — silence HTTP noise
        pass


def _ok_payload(model):
    return {
        "id": "x", "object": "chat.completion", "model": model,
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": "hello"}, "tool_calls": None}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 7, "total_tokens": 27},
        "cost": "0",
    }


@pytest.fixture()
def server():
    handler = _Handler
    handler.scripted = []
    handler.hits["total"] = 0
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd, handler
    httpd.shutdown()


def test_basic_chat_and_usage(server):
    httpd, handler = server
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=1)
    res = client.chat([{"role": "user", "content": "hi"}])
    assert res.status == "ok"
    assert res.content == "hello"
    assert res.prompt_tokens == 20
    assert res.completion_tokens == 7
    assert res.total_tokens == 27
    assert res.provider_cost is None  # cost "0" -> treated as not reported
    client.close()


def test_retry_on_429_then_success(server):
    httpd, handler = server
    handler.scripted = [(429, {"error": "rate limited"}), (200, _ok_payload("m1"))]
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=2)
    res = client.chat([{"role": "user", "content": "hi"}])
    assert res.status == "ok"
    assert res.retries == 1, "429 should be retried once, then succeed"
    client.close()


def test_persistent_500_errors_after_retries(server):
    httpd, handler = server
    handler.scripted = [(500, {}), (500, {}), (500, {})]
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=2)
    res = client.chat([{"role": "user", "content": "hi"}])
    assert res.status == "error"
    assert res.retries == 2
    assert "500" in res.error
    client.close()


def test_404_model_missing_no_retry(server):
    httpd, handler = server
    handler.scripted = [(404, {"error": "model not found"})]
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=5)
    res = client.chat([{"role": "user", "content": "hi"}])
    assert res.status == "error"
    assert res.retries == 0, "hard 404 must not be retried like an outage"
    client.close()


def test_provider_cost_parsed_when_nonzero(server):
    httpd, handler = server
    payload = _ok_payload("m1")
    payload["cost"] = "0.0312"
    handler.scripted = [(200, payload)]
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=0)
    res = client.chat([{"role": "user", "content": "hi"}])
    assert res.provider_cost == pytest.approx(0.0312)
    client.close()


def test_tools_roundtrip(server):
    httpd, handler = server
    payload = _ok_payload("m1")
    payload["choices"][0]["message"] = {
        "role": "assistant", "content": "",
        "tool_calls": [{"id": "call_1", "type": "function",
                        "function": {"name": "submit_patch", "arguments": '{"diff": "x"}'}}],
    }
    handler.scripted = [(200, payload)]
    client = LLMClient(f"http://127.0.0.1:{httpd.server_port}", "k", "m1", max_retries=0)
    res = client.chat([{"role": "user", "content": "go"}], tools=[{"type": "function", "function": {"name": "x"}}])
    assert res.status == "ok"
    assert res.tool_calls and res.tool_calls[0]["function"]["name"] == "submit_patch"
    client.close()