# GitHub / Deployment Release Saga

External systems cannot share one transaction.

```text
CERTIFIED
-> push/tag
-> verify remote SHA
-> CI PASS
-> create release artifact
-> deploy
-> production smoke
-> register public release
-> RELEASED
```

If deployment fails after push, state stays `GITHUB_PUBLISHED`.
The manager retries/reconciles deployment; it does not lie about release state.

Release identity includes:
- release ID
- source SHA
- certificate digest
- OCI digest
- schema versions
- Merkle checkpoint

Release tags/certificates are immutable.
