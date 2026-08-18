"""Probe registry."""

from __future__ import annotations

from typing import Optional

import httpx

from ..schema import Endpoint, ProbeResult
from .base import Credentials, Probe, load_credentials
from .contextsmoke import ContextSmokeProbe
from .discovery import DiscoveryProbe
from .jsonmode import JSONModeProbe
from .reachability import ReachabilityProbe
from .throughput import ThroughputProbe
from .toolsprobe import ToolsProbe
from .ttft import TTFTProbe

PROBES: dict[str, type[Probe]] = {
    ReachabilityProbe.id: ReachabilityProbe,
    TTFTProbe.id: TTFTProbe,
    ThroughputProbe.id: ThroughputProbe,
    JSONModeProbe.id: JSONModeProbe,
    ToolsProbe.id: ToolsProbe,
    ContextSmokeProbe.id: ContextSmokeProbe,
    DiscoveryProbe.id: DiscoveryProbe,
}

# Inference probe types (excludes catalog discovery)
INFERENCE_PROBES = [
    ReachabilityProbe.id,
    TTFTProbe.id,
    ThroughputProbe.id,
    JSONModeProbe.id,
    ToolsProbe.id,
    ContextSmokeProbe.id,
]


def get_probe(probe_id: str, client: Optional[httpx.AsyncClient] = None) -> Probe:
    cls = PROBES.get(probe_id)
    if cls is None:
        raise KeyError(f"unknown probe: {probe_id}")
    return cls(client=client)


def probe_instances(probe_ids: Optional[list[str]] = None,
                    client: Optional[httpx.AsyncClient] = None,
                    max_output_tokens: int = 160,
                    max_context_bucket: int = 8192,
                    ) -> dict[str, Probe]:
    ids = probe_ids or INFERENCE_PROBES
    out: dict[str, Probe] = {}
    for pid in ids:
        p = get_probe(pid, client=client)
        if hasattr(p, "max_output_tokens"):
            p.max_output_tokens = max_output_tokens
        if hasattr(p, "max_bucket"):
            p.max_bucket = max_context_bucket
        out[pid] = p
    return out


__all__ = [
    "PROBES", "INFERENCE_PROBES", "get_probe", "probe_instances",
    "Credentials", "load_credentials", "Probe", "ProbeResult", "Endpoint",
]