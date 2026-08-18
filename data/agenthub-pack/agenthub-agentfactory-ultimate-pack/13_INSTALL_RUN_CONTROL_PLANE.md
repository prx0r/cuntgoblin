# Install / Run / Control Plane

## Operations

```text
doctor_system
install_system
start_system
stop_system
resume_system
system_status
system_logs
benchmark_system
fork_system
compare_systems
```

## Doctor

Checks:
- runtime installed
- OS/architecture
- CPU/RAM/GPU
- Docker if needed
- required tools
- secrets references
- model policy satisfiable through HotSwap
- ports
- storage
- dirty/stale manifest
- committed virtualenv/cache artifacts
- hard-coded paths
- unsupported runtime commands

## Install

Never execute arbitrary README commands blindly.

Use manifest-declared operations in sandbox/controlled environment.

## Build pinning

Install from pinned SHA/container digest.

"main" is not a benchmark identity.

## Resume

Persistent architectures must declare:
- resumable state
- checkpoint location
- replay behavior
- idempotence expectations
