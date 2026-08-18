# AgentBeats + A2A Integration

AgentBeats already solves an important piece:
open, reproducible judge-agent / subject-agent assessment using A2A and MCP.

AgentHub should interoperate instead of replacing it.

## Purple adapter

Any AgentHub Build can expose an A2A server:

```text
ArchitectureBuild
  ↓ runtime adapter
AgentHub A2A wrapper
  ↓
A2A AgentCard
```

## Green adapter

External AgentBeats benchmark:
- register/resolve benchmark image or endpoint
- run AgentHub subject build
- ingest returned assessment artifact
- preserve benchmark version and container digest

## Local mode

AgentHub can run:
- green benchmark container
- purple architecture container
- clean network/filesystem namespace
- A2A exchange
- artifact collection

## Publish compatibility

Store:
- AgentBeats agent ID when published
- leaderboard result reference
- external assessment evidence

## Why this matters

AgentHub adds:
- architecture decomposition
- build lineage
- architecture search
- cross-framework resolution

AgentBeats remains a strong external assessment substrate.
