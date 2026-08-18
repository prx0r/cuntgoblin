# Research & Evidence Pipeline

## Canonical evidence object

```json
{
  "evidence_id":"ev_...",
  "claim_id":"claim_...",
  "source_type":"github|paper|official_doc|pricing|company|forum|other",
  "source_uri":"...",
  "retrieved_at":"...",
  "published_at":"...",
  "content_hash":"...",
  "directness":0.0,
  "authority":0.0,
  "freshness":0.0,
  "independence_family":"...",
  "supports":true,
  "confidence":0.0
}
```

## Loop

```text
question
→ claims
→ query plan
→ source adapters in parallel
→ normalize/dedupe
→ link claim/evidence
→ verify coverage/conflicts
→ decision-sensitive gap?
    yes → bounded replan
    no → evidence bundle
```

Use the existing value-of-information function to research the unknown most likely to change BUILD/RESEARCH/REJECT.

## Competitor search protocol

For “does it exist?” require successful searches across multiple relevant source families. A failed source produces UNKNOWN, never zero competitors.

## Separate finding from confidence

```text
competition_gap = 0.80
competition_gap_confidence = 0.42
```

Low confidence triggers research, not optimism.

## Similarity dimensions

Compare:
- customer,
- job-to-be-done,
- input/output,
- delivery,
- automation level,
- integration surface,
- pricing,
- OSS/commercial,
- adoption evidence.

Do not use keywords alone.
