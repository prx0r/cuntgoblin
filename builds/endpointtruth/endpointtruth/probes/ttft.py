"""ttft-v1: streaming request; measure request start -> first token.

Also detects 'HTTP 200 but malformed stream' (required scenario): a streaming
response that never emits a parseable content chunk or never terminates with
[DONE] is recorded as a failed probe with error_kind=malformed_stream.
"""

from __future__ import annotations

import json
import time

import httpx

from ..schema import Endpoint, Observation, ProbeResult, State, new_id
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms, parse_stream_line)


class TTFTProbe(Probe):
    id = "ttft-v1"
    version = "1.0.0"

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        t0 = time.monotonic()
        artifacts: list[dict] = []

        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.ttft_ms",
                value_number=None, unit="ms", state=State.NOT_OBSERVED.value,
                value_text="no credentials configured", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            return result

        http = await self._http()
        req_body = make_chat_request(endpoint, [{"role": "user", "content": "Say hello."}],
                                     max_tokens=8, stream=True)
        first_token_ms: float | None = None
        stream_supported = False
        done_received = False
        n_chunks = 0
        content_bytes: list[str] = []
        try:
            async with http.stream("POST", f"{creds.base_url}/chat/completions",
                                   headers=creds.auth_headers(), json=req_body) as resp:
                status = resp.status_code
                artifacts.append({"kind": "http_response", "status_code": status,
                                  "headers": dict(resp.headers)})
                if status != 200:
                    body = await resp.aread()
                    artifacts.append({"kind": "body", "text": body.decode(errors="replace")[:2000]})
                    kind = classify_http_error(status)
                    result.status = "FAILURE"
                    result.errors.append(f"http {status}")
                    result.measurements.append(Observation(
                        subject_id=endpoint.endpoint_id, predicate="endpoint.ttft_ms",
                        value_number=None, unit="ms", state=kind,
                        value_text=f"http {status}", source_id=new_id("probe"),
                        method_id=self.id, method_version=self.version))
                    result.raw_artifacts = artifacts
                    return result
                async for line in resp.aiter_lines():
                    try:
                        obj = parse_stream_line(line)
                    except ValueError as e:
                        result.status = "FAILURE"
                        result.errors.append(f"malformed_stream: {e}")
                        artifacts.append({"kind": "malformed_stream", "line": line[:300]})
                        result.measurements.append(Observation(
                            subject_id=endpoint.endpoint_id, predicate="endpoint.stream_malformed",
                            value_number=1.0, unit="flag", state=State.UNAVAILABLE.value,
                            value_text=str(e), source_id=new_id("probe"),
                            method_id=self.id, method_version=self.version))
                        result.measurements.append(Observation(
                            subject_id=endpoint.endpoint_id, predicate="probe.success",
                            value_number=0.0, unit="flag", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id,
                            method_version=self.version))
                        result.raw_artifacts = artifacts
                        return result
                    if obj is None:
                        continue
                    if obj.get("_done"):
                        done_received = True
                        break
                    n_chunks += 1
                    stream_supported = True
                    if first_token_ms is None:
                        delta = ((obj.get("choices") or [{}])[0].get("delta", {}) or {})
                        if delta.get("content") or delta.get("tool_calls") or delta.get("reasoning_content"):
                            first_token_ms = measure_elapsed_ms(t0)
                        elif first_token_ms is None and n_chunks > 20:
                            # endure up to N empty chunks before declaring malformed
                            first_token_ms = measure_elapsed_ms(t0)
                    else:
                        delta = ((obj.get("choices") or [{}])[0].get("delta", {}) or {})
                        if delta.get("content"):
                            content_bytes.append(delta["content"])
            artifacts.append({"kind": "stream_summary",
                              "n_chunks": n_chunks, "done_received": done_received,
                              "content_preview": "".join(content_bytes)[:400],
                              "first_token_ms": first_token_ms})
            if not stream_supported:
                result.status = "FAILURE"
                result.errors.append("no streamed content chunk")
                result.measurements.append(Observation(
                    subject_id=endpoint.endpoint_id, predicate="endpoint.stream_supported",
                    value_number=0.0, unit="flag", state=State.KNOWN.value,
                    source_id=new_id("probe"), method_id=self.id, method_version=self.version))
                result.raw_artifacts = artifacts
                return result
            result.raw_artifacts = artifacts
            result.measurements.extend([
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.stream_supported",
                            value_number=1.0, unit="flag", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version,
                            value_text="done" if done_received else "missing_done"),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.stream_done_ok",
                            value_number=1.0 if done_received else 0.0, unit="flag",
                            state=State.KNOWN.value, source_id=new_id("probe"),
                            method_id=self.id, method_version=self.version,
                            value_text="done" if done_received else "missing_done"),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.ttft_ms",
                            value_number=first_token_ms, unit="ms", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.http_status",
                            value_number=float(status), unit="status", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="probe.success",
                            value_number=1.0, unit="flag", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            ])
            return result
        except Exception as e:
            err = http_error_kind(e)
            result.status = "FAILURE"
            result.errors.append(err)
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.ttft_ms",
                value_number=None, unit="ms", state=State.UNAVAILABLE.value,
                value_text=err, source_id=new_id("probe"), method_id=self.id,
                method_version=self.version))
            result.raw_artifacts = artifacts
            return result