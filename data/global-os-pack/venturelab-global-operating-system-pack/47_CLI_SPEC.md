# `venturelab` CLI

## System

```text
venturelab doctor [--deep]
venturelab up
venturelab down
venturelab status
venturelab go [--dry-run]
venturelab pause
venturelab resume
```

## Queue

```text
venturelab queue list
venturelab queue inspect <job>
venturelab queue retry <job>
venturelab queue cancel <job>
venturelab queue deadletter
```

## Workflows / schedules

```text
venturelab workflow list
venturelab workflow run <id> --input file.json
venturelab workflow inspect <run>
venturelab workflow cancel <run>

venturelab schedule list
venturelab schedule enable <id>
venturelab schedule disable <id>
venturelab schedule trigger <id>
```

## Integrity

```text
venturelab artifact verify <id>
venturelab ledger checkpoint
venturelab ledger verify
venturelab ledger proof <event-id>
```

## Economics

```text
venturelab budget status
venturelab routes status
venturelab routes explain <task>
venturelab accounts opportunities
```

## Factory / AgentHub

```text
venturelab factory list
venturelab factory run <id> --opportunity <id>
venturelab agents search ...
venturelab agents benchmark <build>
venturelab agents lineage <build>
venturelab agents synthesize --need need.json
```
