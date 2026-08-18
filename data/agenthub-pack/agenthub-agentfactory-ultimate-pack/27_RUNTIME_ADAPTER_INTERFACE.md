# Runtime Adapter Interface

AgentHub must not become Hermes-only forever.

```python
class RuntimeAdapter:
    detect(repo) -> Detection
    doctor(build, host) -> DoctorReport
    compile(build, task, model_plan) -> RuntimePlan
    install(build, host) -> Installation
    start(installation, task) -> Run
    status(run) -> RunStatus
    stop(run) -> None
    resume(run) -> Run
    collect(run) -> RunArtifacts
    expose_a2a(installation) -> AgentEndpoint
```

Adapters later:
- Hermes
- LangGraph
- Letta
- A2A-composed
- custom Docker

AgentHub benchmark schema remains runtime-agnostic.
