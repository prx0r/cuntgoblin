# Security and Skill Trust

## Worker isolation

Build in Hermes scratch/worktree/container-style environments with narrow tools and secrets.

## Secrets

Pass only the capability needed for a job. Do not inject entire `.env` files into prompts/traces.

## Skills are executable procedures

Track:
- source,
- hash/version,
- tool permissions,
- required secrets,
- eval score,
- promotion state.

```text
CANDIDATE → EVAL_PASSED → PINNED
                   └→ REJECTED
```

Auto-edited skills must be diffed/scanned/evaluated before promotion.

## Prompt injection

README/web/source text is untrusted data. Research evidence never gets instruction authority.

## Publication

Initially require explicit approval for:
- deployments,
- DNS/domain changes,
- commerce publication,
- paid resources,
- irreversible third-party writes.
