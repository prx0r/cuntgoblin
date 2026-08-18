# Security / Authority Boundaries

Generated code and external repos run in sandbox before promotion.

Secrets:
- store actual values in LiteLLM/secret environment;
- manifests carry opaque refs only;
- never log API keys/auth headers.

Network:
use an allowlist/restricted profile for benchmark/generated-code workers where practical.

External durable actions use commit-time validation.

Policy-controlled human gates remain available for:
- material paid spend;
- provider account setup/manual verification;
- production secret changes;
- domain purchases;
- enterprise outbound;
- legal/compliance-sensitive publication.

The autonomous system can prepare an action packet without silently crossing its authority.
