"""tools-v1: give one trivial deterministic tool `add(a,b)`; test whether the
correct tool call occurs (required scenario: 'tool capability advertised but
fails').
"""

from __future__ import annotations

import json
import time

from ..schema import Endpoint, Observation, ProbeResult, State, new_id
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms)

ADD_TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Add two integers and return the sum.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    },
}

TOOL_PROMPT = "What is 214 + 39? Use the add tool to compute it."


class ToolsProbe(Probe):
    id = "tools-v1"
    version = "1.0.0"

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        artifacts: list[dict] = []
        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.tool_success",
                value_number=None, unit="flag", state=State.NOT_OBSERVED.value,
                value_text="no credentials configured", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            return result

        http = await self._http()
        t0 = time.monotonic()
        req_body = make_chat_request(endpoint, [{"role": "user", "content": TOOL_PROMPT}],
                                     max_tokens=128, tools=[ADD_TOOL])
        try:
            resp = await http.post(f"{creds.base_url}/chat/completions",
                                   headers=creds.auth_headers(), json=req_body)
        except Exception as e:
            err = http_error_kind(e)
            result.status = "FAILURE"
            result.errors.append(err)
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.tool_success",
                value_number=None, unit="flag", state=State.UNAVAILABLE.value,
                value_text=err, source_id=new_id("probe"), method_id=self.id,
                method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        parse_ms = measure_elapsed_ms(t0)
        artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                          "headers": dict(resp.headers)})
        if resp.status_code != 200:
            artifacts.append({"kind": "body", "text": resp.text[:2000]})
            text_lower = resp.text.lower()
            if resp.status_code == 400 and ("tool" in text_lower or "function" in text_lower):
                state = State.NOT_APPLICABLE.value
                value_text = "tool calling not supported"
                result.errors.append("tools not supported (400)")
            else:
                state = classify_http_error(resp.status_code)
                value_text = f"http {resp.status_code}"
                result.errors.append(f"http {resp.status_code}")
            result.status = "FAILURE"
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.tool_success",
                value_number=None, unit="flag", state=state,
                value_text=value_text, source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        payload = resp.json()
        artifacts.append({"kind": "chat_payload", "payload": payload})
        msg = (payload.get("choices") or [{}])[0].get("message", {}) or {}
        tool_calls = msg.get("tool_calls") or []
        called = len(tool_calls) > 0
        correct = False
        args_note = "no_tool_call"
        if called:
            fn = tool_calls[0].get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments") or "{}")
                args_note = f"{name}({args.get('a')},{args.get('b')})"
                correct = (name == "add" and args.get("a") == 214
                           and args.get("b") == 39)
            except Exception:
                args_note = "unparseable_arguments"
                correct = False
        result.raw_artifacts = artifacts
        result.measurements.extend([
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.tool_success",
                        value_number=1.0 if correct else 0.0, unit="flag",
                        state=State.KNOWN.value, value_text=args_note,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.tool_called",
                        value_number=1.0 if called else 0.0, unit="flag",
                        state=State.KNOWN.value, value_text=args_note,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.tool_parse_ms",
                        value_number=parse_ms, unit="ms", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.http_status",
                        value_number=float(resp.status_code), unit="status",
                        state=State.KNOWN.value, source_id=new_id("probe"),
                        method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="probe.success",
                        value_number=1.0, unit="flag", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
        ])
        return result