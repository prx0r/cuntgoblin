"""json-v1: request a deterministic JSON schema; validate parser success.

Records json_success=1 if the response parses AND matches the required field;
json_success=0 (KNOWN) if the endpoint responds 200 but the content is not
valid/deterministic JSON.
"""

from __future__ import annotations

import json
import time

from ..schema import Endpoint, Observation, ProbeResult, State, new_id
from .base import (Probe, classify_http_error, http_error_kind, load_credentials,
                   make_chat_request, measure_elapsed_ms)

JSON_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": "integer"}},
    "required": ["answer"],
    "additionalProperties": False,
}

JSON_PROMPT = ('Return a JSON object with a single field "answer" whose integer '
               "value is 42. Nothing else.")


class JSONModeProbe(Probe):
    id = "json-v1"
    version = "1.0.0"

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        artifacts: list[dict] = []
        if not creds.usable:
            result.status = "FAILURE"
            result.errors.append("no credentials")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.json_success",
                value_number=None, unit="flag", state=State.NOT_OBSERVED.value,
                value_text="no credentials configured", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            return result

        http = await self._http()
        t0 = time.monotonic()
        # Prefer json_schema; servers that reject it fall back to json_object.
        formats = [{"type": "json_schema", "json_schema": {
            "name": "answer_schema", "strict": True, "schema": JSON_SCHEMA}},
            {"type": "json_object"}]
        last_kind = None
        for fmt in formats:
            last_kind = fmt["type"]
            req_body = make_chat_request(endpoint,
                                         [{"role": "user", "content": JSON_PROMPT}],
                                         max_tokens=64, response_format=fmt)
            try:
                resp = await http.post(f"{creds.base_url}/chat/completions",
                                       headers=creds.auth_headers(), json=req_body)
            except Exception as e:
                err = http_error_kind(e)
                result.status = "FAILURE"
                result.errors.append(err)
                result.measurements.append(Observation(
                    subject_id=endpoint.endpoint_id, predicate="endpoint.json_success",
                    value_number=None, unit="flag", state=State.UNAVAILABLE.value,
                    value_text=err, source_id=new_id("probe"), method_id=self.id,
                    method_version=self.version))
                result.raw_artifacts = artifacts
                return result
            artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                              "format": fmt["type"]})
            if resp.status_code == 400 and "json" in resp.text.lower():
                # Schema unsupported by this server -> try next format
                artifacts.append({"kind": "body", "text": resp.text[:2000]})
                continue
            break
        else:
            # All JSON formats rejected
            result.status = "FAILURE"
            result.errors.append("json mode not supported by endpoint")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.json_success",
                value_number=None, unit="flag", state=State.NOT_APPLICABLE.value,
                value_text="json mode not supported", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        parse_ms = measure_elapsed_ms(t0)
        if resp.status_code != 200:
            kind = classify_http_error(resp.status_code)
            result.status = "FAILURE"
            result.errors.append(f"http {resp.status_code}")
            artifacts.append({"kind": "body", "text": resp.text[:2000]})
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="endpoint.json_success",
                value_number=None, unit="flag", state=kind,
                value_text=f"http {resp.status_code}", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        payload = resp.json()
        artifacts.append({"kind": "chat_payload", "payload": payload, "format_used": last_kind})
        content = (payload.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        try:
            parsed = json.loads(content)
            ok = isinstance(parsed, dict) and parsed.get("answer") == 42
        except Exception:
            parsed = None
            ok = False
        state = State.KNOWN.value
        result.raw_artifacts = artifacts
        result.measurements.extend([
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.json_success",
                        value_number=1.0 if ok else 0.0, unit="flag", state=state,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.json_parse_ms",
                        value_number=parse_ms, unit="ms", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="endpoint.json_valid",
                        value_number=1.0 if ok else 0.0, unit="flag", state=state,
                        value_text="valid" if ok else
                        ("not_json" if parsed is None else "wrong_value"),
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