"""context-smoke-v1: test buckets [8K, 32K, 64K, 128K] until failure
(spec section 'Probes'). For the MVP only the smallest enabled bucket is used
per cycle; buckets escalate per configuration.

The test sends filler context up to the bucket size with a deterministic
marker near the end, then asks the model to repeat the marker. Correct answer
=> bucket passes.
"""

from __future__ import annotations

import time

from ..schema import Endpoint, Observation, ProbeResult, State, new_id
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms)

BUCKETS = [8192, 32768, 65536, 131072]
MARKER = "7391"
FILLER_SENTENCE = ("The quick brown fox of equatorial cartography measures "
                   "latitude with a brass sextant and records every heading. ")


def build_context(n_tokens_approx: int, marker: str = MARKER) -> str:
    """Deterministic filler text approximating n_tokens (chars/4 heuristic)."""
    target_chars = max(64, n_tokens_approx * 4)
    rep = FILLER_SENTENCE * (target_chars // len(FILLER_SENTENCE) + 1)
    rep = rep[: target_chars - 16]
    return rep + f" Remember the secret marker number: {marker}."


class ContextSmokeProbe(Probe):
    id = "context-smoke-v1"
    version = "1.0.0"

    def __init__(self, client=None, max_bucket: int = 8192):
        super().__init__(client)
        self.max_bucket = max_bucket

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        artifacts: list[dict] = []
        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.context_ok",
                value_number=None, unit="flag", state=State.NOT_OBSERVED.value,
                value_text="no credentials configured", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            return result

        http = await self._http()
        bucket = None
        for b in BUCKETS:
            if b <= self.max_bucket:
                bucket = b
        if bucket is None:
            result.status = "FAILURE"
            result.errors.append("no bucket within max_bucket")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.context_ok",
                value_number=None, unit="flag", state=State.NOT_APPLICABLE.value,
                value_text=f"max_bucket={self.max_bucket} below smallest bucket",
                source_id=new_id("probe"), method_id=self.id, method_version=self.version))
            return result

        context = build_context(bucket)
        # Approximate token accounting (chars/4) for honest reporting.
        approx_tokens = len(context) // 4
        t0 = time.monotonic()
        req_body = make_chat_request(
            endpoint,
            [{"role": "system", "content": "You are a memory test. "
                                           "Reply with the marker number only."},
             {"role": "user", "content": context}],
            max_tokens=96)
        try:
            resp = await http.post(f"{creds.base_url}/chat/completions",
                                   headers=creds.auth_headers(), json=req_body)
        except Exception as e:
            err = http_error_kind(e)
            result.status = "FAILURE"
            result.errors.append(err)
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.context_ok",
                value_number=None, unit="flag", state=State.UNAVAILABLE.value,
                value_text=err, source_id=new_id("probe"), method_id=self.id,
                method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        elapsed = measure_elapsed_ms(t0)
        artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                          "bucket_tokens": bucket, "approx_tokens": approx_tokens})
        if resp.status_code != 200:
            artifacts.append({"kind": "body", "text": resp.text[:2000]})
            kind = classify_http_error(resp.status_code)
            result.status = "FAILURE"
            result.errors.append(f"http {resp.status_code}")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.context_ok",
                value_number=0.0, unit="flag", state=kind,
                value_text=f"http {resp.status_code}", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        payload = resp.json()
        artifacts.append({"kind": "chat_payload", "payload": payload, "bucket": bucket})
        msg = (payload.get("choices") or [{}])[0].get("message", {}) or {}
        content = msg.get("content") or ""
        # Some gateways put the answer in reasoning fields (e.g.
        # deepseek family via opencode-go returns `reasoning` with
        # finish_reason=length and empty content).
        reasoning = (msg.get("reasoning") or "") + (msg.get("reasoning_content") or "")
        all_text = content + reasoning
        ok = MARKER in all_text
        result.raw_artifacts = artifacts
        result.measurements.extend([
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.context_ok",
                        value_number=1.0 if ok else 0.0, unit="flag", state=State.KNOWN.value,
                        value_text=f"bucket={bucket}", source_id=new_id("probe"),
                        method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.context_bucket",
                        value_number=float(bucket), unit="tokens", state=State.KNOWN.value,
                        value_text="ok" if ok else "failed", source_id=new_id("probe"),
                        method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.context_test_tokens",
                        value_number=float(approx_tokens), unit="tokens", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.context_elapsed_ms",
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