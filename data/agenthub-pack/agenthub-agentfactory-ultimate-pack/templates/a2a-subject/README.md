# A2A Subject Adapter Template

Wrap one AgentHub ArchitectureBuild as an A2A-compatible subject agent.

Requirements:
- expose AgentCard
- map A2A task/context IDs to isolated runtime state
- stream status updates where useful
- return artifacts
- fresh/reset state for benchmark runs

Do not embed benchmark-specific shortcuts in the subject adapter.
