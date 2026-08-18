# Process Deployment

Small-server default services:
- postgres
- dell
- litellm
- venturelab-manager
- venturelab workers
- hermes gateway
- public API/site if hosted

Use Docker Compose or systemd for permanent daemons, not ad-hoc nohup.

Hermes background processes remain appropriate for bounded agent tasks.

Use a Postgres singleton/application lease so only one manager acts as scheduler leader.
Multiple worker consumers are expected.
