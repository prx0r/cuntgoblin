# AgentHub REST + MCP

## Public/read

```text
GET /v1/systems
GET /v1/systems/{id}
GET /v1/systems/{id}/builds
GET /v1/builds/{id}
GET /v1/builds/{id}/benchmarks
GET /v1/patterns
GET /v1/leaderboards/{suite}
POST /v1/resolve
POST /v1/compare
```

## Operational

```text
POST /v1/install
POST /v1/doctor
POST /v1/runs
POST /v1/runs/{id}/actions
POST /v1/benchmark
POST /v1/forks
```

## Factory / architecture research

```text
POST /v1/architecture/need
POST /v1/architecture/synthesize
POST /v1/architecture/search
POST /v1/architecture/promote
```

## MCP tools

- `search_agent_systems`
- `inspect_agent_system`
- `resolve_agent_system`
- `compare_agent_systems`
- `doctor_agent_system`
- `install_agent_system`
- `run_agent_system`
- `benchmark_agent_system`
- `fork_agent_system`
- `get_architecture_lineage`
- `extract_architecture_patterns`
- `synthesize_architecture`
- `architecture_search`
