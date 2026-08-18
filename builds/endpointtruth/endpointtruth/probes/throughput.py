"""throughput-v1: generate a controlled number of output tokens; measure
output tokens / wall time (tokens_per_second).
"""

from __future__ import annotations

import time

from ..schema import Endpoint, Observation, ProbeResult, State, new_id
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms)

PROMPT = ("Write a long factual paragraph about the history of cartography. "
          "Do not stop until the paragraph is complete. Keep going with more "
          "sentences until you reach the end of the response.")


class ThroughputProbe(Probe):
    id = "throughput-v1"
    version = "1.0.0"

    def __init__(self, client=None, max_output_tokens: int = 160):
        super().__init__(client)
        self.max_output_tokens = max_output_tokens

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        t0 = time.monotonic()
        artifacts: list[dict] = []

        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.output_tps",
                value_number=None, unit="tokens_per_second", state=State.NOT_OBSERVED.value,
                value_text="no credentials configured", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            return result

        http = await self._http()
        req_body = make_chat_request(endpoint, [{"role": "user", "content": PROMPT}],
                                     max_tokens=self.max_output_tokens)
        try:
            resp = await http.post(f"{creds.base_url}/chat/completions",
                                   headers=creds.auth_headers(), json=req_body)
            elapsed = measure_elapsed_ms(t0)
            artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                              "headers": dict(resp.headers)})
            if resp.status_code != 200:
                artifacts.append({"kind": "body", "text": resp.text[:2000]})
                kind = classify_http_error(resp.status_code)
                result.status = "FAILURE"
                result.errors.append(f"http {resp.status_code}")
                result.measurements.append(Observation(
                    subject_id=endpoint.endpoint_id, predicate="endpoint.output_tps",
                    value_number=None, unit="tokens_per_second", state=kind,
                    value_text=f"http {resp.status_code}", source_id=new_id("probe"),
                    method_id=self.id, method_version=self.version))
                result.raw_artifacts = artifacts
                return result
            payload = resp.json()
            artifacts.append({"kind": "chat_payload", "payload": payload})
            try:
                usage = payload.get("usage", {}) or {}
                out_tokens = int(usage.get("completion_tokens") or 0)
            except Exception:
                out_tokens = 0
            content = (payload.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            # Best-effort token count fallback (usage missing in some servers)
            if out_tokens == 0:
                out_tokens = max(1, len(content) // 4)
            tps = round(out_tokens / (elapsed / 1000.0), 3) if elapsed > 0 else 0.0
            result.raw_artifacts = artifacts
            result.measurements.extend([
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.output_tps",
                            value_number=tps, unit="tokens_per_second", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.output_tokens",
                            value_number=float(out_tokens), unit="tokens", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.elapsed_ms",
                            value_number=elapsed, unit="ms", state=State.KNOWN.value,
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
        except Exception as e:
            err = http_error_kind(e)
            result.status = "FAILURE"
            result.errors.append(err)
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.output_tps",
                value_number=None, unit="tokens_per_second", state=State.UNAVAILABLE.value,
                value_text=err, source_id=new_id("probe"), method_id=self.id,
                method_version=self.version))
            result.raw_artifacts = artifacts
            return result