"""EndpointTruth — continuously determine what an actual LLM serving endpoint can do right now.

MVP per specs/endpointtruth/architecture.md (VentureLab PRODUCT 1).

Truth ladder (per Patala doctrine / VentureLab anti-cheat):
  SOURCE (live endpoint) -> RAW ARTIFACTS -> OBSERVATIONS (immutable rows)
  -> MEASUREMENTS -> WINDOW AGGREGATOR -> CURRENT STATE -> API / MCP.

Nothing in this package ever fabricates reality: every Observation carries a
state enum (KNOWN / UNKNOWN / ABSENT / NOT_OBSERVED / NOT_APPLICABLE / STALE /
CONFLICTED / UNAVAILABLE / RATE_LIMITED), a method id + version, a source id,
an evidence artifact sha256 and a confidence. Aggregations and resolutions are
derived projections over raw observations and never overwrite them.
"""

__version__ = "0.1.0"