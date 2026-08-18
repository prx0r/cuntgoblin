# Sandbox / Security

Architecture search executes generated code/configurations.

Mandatory:
- filesystem sandbox
- network allowlist
- CPU/RAM/time limits
- no host secrets
- ephemeral benchmark credentials
- container/process cleanup by exact ID/PID
- artifact size limits
- command audit log

Generated architecture may not:
- alter benchmark gold
- alter evaluator
- read other candidate outputs
- access hidden result files
- mutate host AgentHub DB directly

Evolution happens in candidate workspace.
Promotion copies only approved artifacts.
