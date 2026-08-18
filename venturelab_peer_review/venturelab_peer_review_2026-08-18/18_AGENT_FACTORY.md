# Agent Factory

## Goal

Given a recurring job, create the smallest architecture that passes a task-specific eval inside a cost/reliability envelope.

```text
job spec
→ capability requirements
→ AgentHub resolver
→ REUSE / FORK / SYNTHESIZE
→ architecture
→ HotSwap model slots
→ Hermes profiles/skills/tools
→ frozen eval
→ adversarial eval
→ package/deploy
→ outcomes
```

## Outputs

- architecture descriptor,
- Hermes profile,
- skills,
- tool allowlist,
- secret/environment manifest,
- eval suite,
- certificate,
- deployment config.

The product is **not a prompt**. It is a tested architecture + tool/skill/model policy + reproducible evaluation.

Feed live outcomes back into AgentHub fit values over time.
