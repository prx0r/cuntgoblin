"""reachability-v1: very small inference request (spec section 'Probes').

Also verifies the model actually served matches the advertised model id
(required scenario: 'endpoint switches model alias' -> CONFLICTED state).
"""

from __future__ import annotations

from typing import Optional

import httpx

from ..schema import Endpoint, Observation, ProbeResult, State, new_id, sha256_bytes, utcnow
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms)

PING = "Reply with exactly the single word: pong"


class ReachabilityProbe(Probe):
    id = "reachability-v1"
    version = "1.0.0"

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        t0 = __import__("time").monotonic()
        artifacts: list[dict] = []

        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.reachable",
                value_number=0.0, unit="flag", state=State.NOT_OBSERVED.value,
                source_id=new_id("probe"), method_id=self.id, method_version=self.version,
                confidence=0.95, value_text="no credentials configured"))
            return result

        http = await self._http()
        req_body = make_chat_request(endpoint, [{"role": "user", "content": PING}],
                                     max_tokens=2)
        try:
            resp = await http.post(f"{creds.base_url}/chat/completions",
                                   headers=creds.auth_headers(), json=req_body)
            latency = measure_elapsed_ms(t0)
            artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                              "headers": dict(resp.headers), "body": resp.text[:2000]})
            if resp.status_code != 200:
                kind = classify_http_error(resp.status_code)
                result.status = "FAILURE"
                result.errors.append(f"http {resp.status_code}")
                result.measurements.append(Observation(
                    subject_id=endpoint.endpoint_id, predicate="endpoint.reachable",
                    value_number=0.0, unit="flag", state=kind,
                    value_text=f"http {resp.status_code}",
                    source_id=new_id("probe"), method_id=self.id, method_version=self.version))
                result.raw_artifacts = artifacts
                return result
            payload = resp.json()
            served = str(payload.get("model", "") or "")
            result.raw_artifacts = artifacts + [{"kind": "chat_payload", "payload": payload}]
            result.measurements.extend([
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.reachable",
                            value_number=1.0, unit="flag", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.http_status",
                            value_number=float(resp.status_code), unit="status",
                            state=State.KNOWN.value, source_id=new_id("probe"),
                            method_id=self.id, method_version=self.version),
                Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.reach_latency_ms",
                            value_number=latency, unit="ms", state=State.KNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            ])
            if served:
                alias_ok = (served == endpoint.provider_model_name
                            or served.endswith(endpoint.provider_model_name)
                            or endpoint.provider_model_name.endswith(served))
                result.measurements.append(Observation(
                    subject_id=endpoint.endpoint_id, predicate="endpoint.model_served",
                    value_text=served,
                    state=State.KNOWN.value if alias_ok else State.CONFLICTED.value,
                    source_id=new_id("probe"), method_id=self.id, method_version=self.version,
                    value_number=1.0 if alias_ok else 0.0, unit="flag"))
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="probe.success",
                value_number=1.0, unit="flag", state=State.KNOWN.value,
                source_id=new_id("probe"), method_id=self.id, method_version=self.version))
            return result
        except Exception as e:
            err = http_error_kind(e)
            result.status = "FAILURE"
            result.errors.append(err)
            result.raw_artifacts = artifacts
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.reachable",
                value_number=0.0, unit="flag", state=State.UNAVAILABLE.value,
                value_text=err, source_id=new_id("probe"), method_id=self.id,
                method_version=self.version))
            return result