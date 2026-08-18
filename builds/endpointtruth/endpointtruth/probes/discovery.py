"""discovery-v1: fetch a provider's public model catalog (e.g. OpenRouter
/api/v1/models) and record what the provider ADVERTISES. This is real data
about reality (the catalog API), collected without a credential.

Inference capability for catalog-discovered endpoints is recorded honestly as
NOT_OBSERVED until a live probe with credentials succeeds.

Discovered endpoint definitions are returned in `result.meta['endpoints']` —
the caller (CLI/runner) registers them into the endpoints table.
"""

from __future__ import annotations

import time

from ..schema import (Endpoint, Observation, ProbeResult, State, new_id, utcnow)
from .base import Probe, classify_http_error, http_error_kind, load_credentials


class DiscoveryProbe(Probe):
    id = "discovery-v1"
    version = "1.0.0"

    async def run(self, endpoint: Endpoint, creds=None) -> ProbeResult:
        creds = creds or load_credentials(endpoint)
        result = ProbeResult()
        artifacts: list[dict] = []
        t0 = time.monotonic()
        http = await self._http()
        models_url = f"{creds.base_url}/models" if creds.base_url else endpoint.base_url.rstrip("/") + "/models"
        try:
            resp = await http.get(models_url, headers=creds.auth_headers())
        except Exception as e:
            result.status = "FAILURE"
            result.errors.append(http_error_kind(e))
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="catalog.reachable",
                value_number=0.0, unit="flag", state=State.UNAVAILABLE.value,
                value_text=http_error_kind(e), source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        artifacts.append({"kind": "http_response", "status_code": resp.status_code,
                          "elapsed_ms": round((time.monotonic() - t0) * 1000, 2)})
        if resp.status_code != 200:
            artifacts.append({"kind": "body", "text": resp.text[:2000]})
            result.status = "FAILURE"
            result.errors.append(f"http {resp.status_code}")
            result.measurements.append(Observation(
                subject_id=endpoint.endpoint_id, predicate="catalog.reachable",
                value_number=0.0, unit="flag", state=classify_http_error(resp.status_code),
                value_text=f"http {resp.status_code}", source_id=new_id("probe"),
                method_id=self.id, method_version=self.version))
            result.raw_artifacts = artifacts
            return result

        payload = resp.json()
        artifacts.append({"kind": "catalog_payload", "payload": payload})
        data = payload.get("data") or []
        now = utcnow()
        result.measurements.extend([
            Observation(subject_id=endpoint.endpoint_id, predicate="catalog.reachable",
                        value_number=1.0, unit="flag", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            Observation(subject_id=endpoint.endpoint_id, predicate="catalog.models_count",
                        value_number=float(len(data)), unit="models", state=State.KNOWN.value,
                        source_id=new_id("probe"), method_id=self.id, method_version=self.version),
        ])

        discovered: list[dict] = []
        for m in data:
            mid = m.get("id", "")
            if not mid:
                continue
            pricing_raw = m.get("pricing") or {}
            pricing = {}
            p_prompt = _f(pricing_raw.get("prompt"))
            p_comp = _f(pricing_raw.get("completion"))
            if p_prompt is not None:
                pricing["prompt_per_1k"] = p_prompt
            if p_comp is not None:
                pricing["completion_per_1k"] = p_comp
            pricing["currency"] = "USD"
            params = set(m.get("supported_parameters") or [])
            tools = "tools" in params or "function_calling" in params
            json_ok = "response_format" in params or "json_schema" in params
            ctx = m.get("context_length") or m.get("max_context_length") or m.get("max_context")
            try:
                ctx = int(ctx) if ctx else None
            except (TypeError, ValueError):
                ctx = None
            top_provider = m.get("top_provider", {})
            deployment_variant = "top_provider"
            if isinstance(top_provider, dict) and top_provider.get("id"):
                deployment_variant = f"primary:{top_provider.get('id')}"
            ep = {
                "endpoint_id": f"openrouter:{mid}",
                "provider_id": "openrouter",
                "model_id": mid,
                "provider_model_name": mid,
                "base_url": "https://openrouter.ai/api/v1",
                "region": "any",
                "deployment_variant": deployment_variant,
                "quantization_state": "unknown",
                "advertised_context_tokens": ctx,
                "tools_advertised": tools,
                "json_advertised": json_ok,
                "pricing": pricing,
                "api_key_env": "OPENROUTER_API_KEY",   # absent on this box -> NOT_OBSERVED inference
                "discovered_at": now,
            }
            discovered.append(ep)
            result.measurements.extend([
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.context_advertised",
                            value_number=float(ctx) if ctx else None,
                            unit="tokens" if ctx else "", state=State.KNOWN.value if ctx else State.UNKNOWN.value,
                            value_text=str(ctx) if ctx else "not advertised",
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.price_per_1k_prompt",
                            value_number=p_prompt, unit="usd" if p_prompt is not None else "",
                            state=State.KNOWN.value if p_prompt is not None else State.UNKNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.price_per_1k_completion",
                            value_number=p_comp, unit="usd" if p_comp is not None else "",
                            state=State.KNOWN.value if p_comp is not None else State.UNKNOWN.value,
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.tools_advertised",
                            value_number=1.0 if tools else 0.0, unit="flag",
                            state=State.KNOWN.value, source_id=new_id("probe"),
                            method_id=self.id, method_version=self.version),
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.json_advertised",
                            value_number=1.0 if json_ok else 0.0, unit="flag",
                            state=State.KNOWN.value, source_id=new_id("probe"),
                            method_id=self.id, method_version=self.version),
                # Honest: catalog does not prove inference. No credential on
                # this box -> live capability is NOT_OBSERVED until probed.
                Observation(subject_id=f"openrouter:{mid}", predicate="endpoint.inference_available",
                            value_number=None, unit="", state=State.NOT_OBSERVED.value,
                            value_text="no credential configured for inference probe",
                            source_id=new_id("probe"), method_id=self.id, method_version=self.version),
            ])
        result.raw_artifacts = artifacts
        result.meta["endpoints"] = discovered
        return result


def _f(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None