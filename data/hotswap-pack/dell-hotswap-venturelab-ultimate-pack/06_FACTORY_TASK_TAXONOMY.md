# VentureLab Task Taxonomy v1

Initial cells.

## Research / market

### `source_extract`
Cheap/free-first.
Objective: obtain structured evidence.
Quality floor: .55
Paid: normally no.

### `source_analysis`
Free-first.
Quality floor: .62

### `research_synthesis`
Free-first if good enough.
Quality floor: .70

### `opportunity_adjudication`
Important.
Quality floor: .76
Prefer independent second-pass verifier.

### `market_audit`
Important independent model-family preferred.
Quality floor: .80

## Ideas / architecture

### `solution_generation`
Diversity-valued.
Quality floor: .65
Exploration allowed.

### `architecture_design`
Quality floor: .78
Paid escalation allowed.

### `specification`
Quality floor: .80

## Coding

### `coding_scaffold`
Free-first.
Quality floor: .65

### `coding_patch`
Quality floor: .76
Test feedback ideal.

### `coding_feature`
Quality floor: .80

### `coding_refactor`
Quality floor: .78

### `debugging`
Quality floor: .78

## Verification

### `test_generation`
Quality floor: .73

### `code_review`
Quality floor: .82
Different model family preferred where practical.

### `certification`
Release gate.
Quality floor: .88
No exploration.

### `security_review`
Release gate.
Quality floor: .90
No exploration.

### `release_finish`
Release gate.
Quality floor: .90

## Cheap auxiliary

### `summarize`
### `classify`
### `extract`
### `compress`
### `title`
### `dedupe`

These should aggressively use free/cheap routes and independent auxiliary model slots.

## These are initial priors

VentureLab outcomes should recalibrate quality floors and difficulty cells.
