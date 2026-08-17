Completed a much larger research pass and turned it into an expanded living database.

[Download the expanded deep-dive workbook](sandbox:/mnt/data/agent_reality_ventures_deepdive_2026.xlsx)

It now contains the original benchmark plus **Landscape_DB, Standards_Protocols, Research_Papers, OSS_Expanded, Buyers_Monetization, Deep_Benchmark, five individual venture dossiers, a 12-month roadmap, and an Open_Questions research backlog**.

## The biggest thing the research changed

I think the opportunity is broader than “humans are the moat.”

The emerging scarce resource is **verifiable agency**:

```text
INTELLIGENCE
becomes cheap
     ↓
agents become capable
     ↓
agents receive authority
     ↓
agents spend / delegate / act
     ↓
something happens outside the model
     ↓
WE NEED TO KNOW:

Who authorized it?
Who actually performed it?
What happened?
What evidence exists?
Was it within policy?
Was the outcome accepted?
Can we trust that actor next time?
```

Several independent ecosystems are converging on different portions of precisely this stack.

Google's AP2 deals with cryptographically represented authorization for agent payments; FIDO has now created workstreams around agent authentication, user intent, and trusted delegation; ERC-8004 provides portable identity/reputation/validation registries; and an IETF SCITT draft published this summer defines signed, tamper-evident **AI-agent action receipts**. ([Google Cloud][1])

That convergence makes me significantly more confident that **receipts / proof / authorization are infrastructure categories rather than speculative product ideas.**

---

# 1. Work Receipts now looks strongest

### Refined score: **9.2/10**

The really compelling evidence is ERC-8004's current weakness.

ERC-8004 already validates that agents require portable identity, reputation and validation. But the first large empirical analysis found its deployed reputation layer currently performs poorly as a trust signal: feedback was rarely grounded in verifiable interactions, values were not directly comparable, and coordinated Sybil behavior was extremely common. ([arXiv][2])

That's almost a product specification for you.

Don't build:

```text
Agent Reputation API

Agent X = 4.83 / 5
```

Build:

```text
Agent X

CAPABILITY: legal_translation

qualifying jobs           183
accepted                  174
disputed                    4
failed                      5

receiver-attested          91%
independently verified     37%
median completion          7m 14s
median cost                $0.081

confidence                 HIGH
```

And every number links to underlying receipts.

## The key primitive

```json
{
  "principal": "...",
  "delegate": "...",
  "executor": "...",

  "task": "...",
  "capability": "...",

  "requested_outcome": {},
  "observed_outcome": {},

  "evidence": [],
  "attestations": [],

  "cost": {},
  "duration": {},

  "verification": {},
  "acceptance": {},

  "signatures": []
}
```

This isn't merely reputation.

It's a **history of economic agency**.

---

# 2. Receiver-attested receipts are especially interesting

I found a research direction called **Sello**, or Receiver-Attested Confidential Receipts.

The insight is excellent:

Agent A saying:

> I successfully did X.

is weak evidence.

But the service receiving the action saying:

> I observed Agent A perform X.

is much stronger.

The paper proposes cryptographically signed receipts from the receiver of the action rather than relying on the agent's own execution logs. ([arXiv][3])

Example:

```text
ResearchAgent:
"I uploaded foo.pdf to Dropbox."

                    weak

Dropbox:
"I received SHA256:abc...
from delegated agent X
at 18:42 UTC."

                    strong
```

Or physically:

```text
worker:
"I delivered package."

                    ↓

receiver:
"I received parcel #142."

                    ↓

courier GPS proof

                    ↓

photo evidence

                    ↓

delivery receipt
```

This gives you a hierarchy:

```text
self assertion
     <
counterparty assertion
     <
authenticated counterparty assertion
     <
evidence-backed assertion
     <
independently verified evidence
```

That hierarchy itself could become part of your scoring infrastructure.

---

# 3. Reality proof is a real existing business

### Score: **8.9/10**

This isn't waiting for the agent economy.

Companies already pay for determining whether something occurred in physical reality.

Truepic sells authenticated visual inspection infrastructure across areas including insurance, lending, warranties, recalls and asset verification. ([Truepic][4])

Premise operates a global human-generated field-intelligence network. ([Premise][5])

Gigwalk sends distributed workers into locations for retail audits and real-time field reports. ([Gigwalk][6])

Field Agent similarly pays people to capture in-store observations, photos and other information. ([Google Play][7])

This means there is already money attached to:

```text
"What is actually happening THERE, NOW?"
```

The agentic opportunity is making that **programmable**.

---

# The interesting gap isn't verified photographs

Truepic already exists.

C2PA already exists.

Digimarc is bringing C2PA-derived provenance/audit tooling into AI workflows. ([Help Net Security][8])

Your abstraction should instead be:

```http
POST /proof-requirements
```

Input:

```json
{
  "claim": "The Coca-Cola display is installed correctly",
  "location": "...",
  "freshness": "<2 hours"
}
```

Result:

```json
{
  "requirements": [
    "current capture",
    "GPS within 30m",
    "wide contextual shot",
    "close-up display shot",
    "required product visible",
    "random challenge satisfied"
  ]
}
```

Then:

```http
POST /verify
```

returns whether the **task claim** is supported.

That's materially different from:

> Is JPEG X genuine?

---

# 4. Proof schemas themselves may be valuable data

Imagine accumulating:

```text
TASK                              PROOF

store is open
→ facade
→ signage
→ timestamp
→ location

parcel delivered
→ parcel identifier
→ destination
→ recipient
→ timestamp

product stocked
→ product identity
→ shelf context
→ price label
→ location
→ freshness

machine repaired
→ machine identifier
→ before evidence
→ after evidence
→ operational test

billboard installed
→ location
→ wide shot
→ content matching
→ installation state
```

Then add:

```text
common fraud techniques
verification confidence
proof failures
necessary evidence
unnecessary evidence
optimal number of observers
dispute frequency
```

You end up with an extremely unusual dataset:

> **What constitutes credible evidence that a real-world action happened?**

I think that's much harder to commoditize than an MCP wrapper.

---

# 5. RealityRouter remains massive, but later

### Score: **8.1/10**

The thesis itself is being validated very quickly.

RentAHuman explicitly offers MCP and REST interfaces through which AI agents can search humans, create tasks and manage hiring. ([RentAHuman][9])

More importantly, an empirical study of 303 marketplace bounties found **32.7% originated through programmatic API/MCP channels** rather than purely human-driven use. ([arXiv][10])

MeatLayer is independently building toward nearly the exact abstraction:

```text
AI creates task
↓
budget/escrow
↓
worker claims it
↓
physical execution
↓
proof
↓
verification
↓
payment
```

and describes the long-term ambition as infrastructure that AI systems call when they need something performed or verified in physical reality. ([TechRadar][11])

Traditional markets are simultaneously becoming more API-accessible. Taskrabbit's Home Services API can programmatically estimate jobs, query availability, reserve appointments and manage physical-service bookings. ([Taskrabbit Developer Hub][12])

So the supply graph is appearing.

---

# But don't build another RentAHuman

Instead:

```text
                    RealityRouter
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
         API           HUMAN             SENSOR
                                       / DATASET
          │               │                │
          ▼               ▼                ▼
      web service     RentAHuman        satellite
                      Taskrabbit         camera
                      Premise            IoT
                      Gigwalk
                      Field Agent
          │               │
          └───────┬───────┘
                  ▼
               OUTCOME
                  │
                  ▼
                PROOF
```

The agent shouldn't care who executes it.

It asks:

```http
POST /outcomes
```

> Determine whether product X is stocked at location Y with 95% confidence within three hours for <$8.

Router might respond:

```text
OPTION A
Premise-like field worker
$5.80
45 min expected
confidence .98

OPTION B
call store
$0.20
4 min
confidence .75

OPTION C
merchant inventory API
$0.004
2 sec
freshness uncertain

OPTION D
two independent workers
$10.60
confidence .998
over budget
```

That is a very powerful eventual product.

---

# 6. The dataset behind RealityRouter may be more valuable than routing

Every task teaches:

```text
TASK
× COUNTRY
× CITY
× PROVIDER
× EXECUTOR TYPE
× TIME
× COST
× LATENCY
× SUCCESS RATE
× PROOF QUALITY
× FRAUD RATE
× DISPUTE RATE
```

Eventually:

```http
POST /estimate
```

can answer:

> How much does it normally cost to have someone verify retail inventory in Bangkok within two hours?

or:

> Is a human, API, phone call or field-data provider normally cheapest for this outcome?

That's **physical-world execution intelligence**.

There's basically an Artificial Analysis analogue hiding inside this idea:

```text
Artificial Analysis:
models → cost/speed/quality

Reality intelligence:
execution method → cost/speed/reliability
```

---

# 7. Human escalation is real, but generic HITL is weak

### Score: **7.9/10**

HumanLayer already demonstrated developer interest in framework-agnostic human approval/input, although its old implementation has since been deprecated/repositioned. ([GitHub][13])

Platforms such as StackAI now describe HITL approval as a normal production-agent control pattern. ([StackAI][14])

That means:

```text
"approve this tool call in Slack"
```

probably isn't a company anymore.

It's a feature.

## But the Alibaba result exposes the better product

A 2026 randomized field study of Alibaba customer-service operations found human intervention performance depends materially on:

```text
WHY the AI failed
WHEN the human intervened
HOW MUCH effort the human provided
```

and early intervention was particularly important. ([arXiv][15])

Therefore:

> Human escalation is itself a routing/intelligence problem.

Much more interesting.

---

# Human inference API

Instead of:

```http
ask_human()
```

make:

```http
POST /infer
```

```json
{
  "task": "...",

  "required_capabilities": [
    "native_japanese",
    "contract_law"
  ],

  "target_latency_seconds": 180,

  "confidence_required": 0.95,

  "max_cost": 4
}
```

Your system decides:

```text
one expert
vs
two ordinary workers
vs
three-vote consensus
vs
specialist marketplace
vs
existing staff
```

Result:

```json
{
  "result": "...",

  "confidence": 0.97,

  "executors": 2,

  "agreement": 1.0,

  "cost": 1.81,

  "latency_seconds": 94,

  "receipts": [...]
}
```

Then humans literally become an **inference backend**.

That fits your infrastructure thesis beautifully.

---

# 8. This can produce human benchmarks too

Suppose you accumulate:

```text
humans
× capabilities
× tasks
× accuracy
× latency
× cost
```

Now agents can decide between:

```text
GPT-6
Claude
specialized API
random crowd
expert human
local person
```

with the same optimizer.

Eventually:

```http
POST /resolve
```

doesn't care whether an answer came from silicon or biology.

It just optimizes:

```text
expected utility =
success probability
× outcome value
- cost
- latency penalty
- risk
```

That's a much deeper form of a router.

---

# 9. Authority is unquestionably huge

### Score: **8.6/10**

But there is serious competition.

WorkOS now explicitly frames agent delegation as an authorization problem where the resulting permission should be an intersection of the user's permissions and the narrower authority delegated to the agent. ([WorkOS][16])

Entrust similarly argues agent authority must be auditable, minimally scoped, revocable and tied to a principal. ([Entrust][17])

Google AP2 uses mandates to represent authorization around agent-initiated payments. ([Google Cloud][1])

FIDO has launched dedicated work around trusted agent interactions. ([FIDO Alliance][18])

And Arcade has reportedly raised $60 million specifically around secure authorization for enterprise agents. ([The Wall Street Journal][19])

So:

## Don't build another Auth0.

And don't build:

> “OAuth for agents.”

Too crowded.

---

# 10. Build the **decision point**

This endpoint is still compelling:

```http
POST /authorize
```

Input:

```json
{
  "principal": "tom",

  "actor": "shopping-agent",

  "delegation_chain": [
    "tom",
    "personal-agent",
    "shopping-agent"
  ],

  "action": {
    "type": "purchase",
    "merchant": "...",
    "amount": 37
  },

  "context": {
    "project": "trip",
    "country": "KH"
  }
}
```

Output:

```json
{
  "decision": "ALLOW_WITH_CONDITIONS",

  "reasons": [
    "within_total_budget",
    "merchant_allowed",
    "purchase_category_allowed"
  ],

  "conditions": [
    "receipt_required",
    "refund_supported"
  ],

  "remaining_budget": 63,

  "subdelegation_allowed": false
}
```

Underneath it:

```text
Auth0 / WorkOS / DID
      ↓
identity

AP2
      ↓
mandate

OpenFGA / OPA / Cedar
      ↓
policy

YOUR LAYER
      ↓
agent-aware decision context
      ↓
ALLOW
DENY
ASK
CONSTRAIN
```

OpenFGA already gives you a mature open-source fine-grained authorization engine, so much of the foundational machinery doesn't need reinventing. ([OpenFGA][20])

Your IP would be the **agent-action model and policy intelligence**.

---

# 11. Trajectory-aware policy may be a niche

This is subtle but important.

Ordinary authorization asks:

```text
Can Tom read invoice X?
```

Agent authorization increasingly needs:

```text
Given:

Tom's mandate
+
Agent's previous 17 actions
+
$61 already spent
+
recipient changed twice
+
current action is irreversible
+
current model confidence
+
requested outcome

should action 18 execute?
```

Research on runtime agent governance argues that the **execution path itself** needs to become an input to policy decisions rather than relying only on static permissions. ([arXiv][21])

That gives a much more differentiated API:

```http
POST /evaluate-next-action
```

Potential outputs:

```text
ALLOW
DENY
CONSTRAIN
REQUIRE_PROOF
REQUIRE_HUMAN
REQUIRE_STRONGER_AUTH
```

Now this product naturally touches your other four ventures.

---

# 12. The five ventures therefore collapse into one loop

This is the strongest architecture I've found:

```text
                 ┌──────────────┐
                 │  PRINCIPAL   │
                 └──────┬───────┘
                        │
                      AUTH
                        │
                        ▼
                  ┌──────────┐
                  │ MANDATE  │
                  └────┬─────┘
                       │
                       ▼
                    AGENT
                       │
                 needs outcome
                       │
                       ▼
               ┌───────────────┐
               │ REALITY ROUTER│
               └───────┬───────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
    SOFTWARE          HUMAN            ROBOT
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                     WORK
                       │
                       ▼
                   EVIDENCE
                       │
                       ▼
                 VERIFICATION
                       │
                       ▼
                    RECEIPT
                       │
                       ▼
                  REPUTATION
                       │
                       ▼
               BETTER NEXT ROUTE
```

Everything compounds.

---

# 13. And there is a natural data flywheel

At first:

```text
agent asks
↓
you route
↓
someone performs work
```

Eventually:

```text
agent asks

↓ your data predicts

who can do it
how much it'll cost
how long it'll take
how likely they are to succeed
what proof is necessary
how risky it is
whether they're authorized
whether the result should be trusted
```

Every completed task improves all of these.

That is a **real data moat**.

---

# 14. A particularly important new concept: Proof → Reputation, not Reputation → Trust

Most marketplaces effectively do:

```text
ratings
↓
reputation
↓
trust
```

I think autonomous markets will need:

```text
action
↓
evidence
↓
receipt
↓
verification
↓
historical performance
↓
capability-specific reputation
↓
trust decision
```

The ERC-8004 empirical results are a very strong demonstration of why freely generated ratings aren't enough. ([arXiv][2])

This is probably the intellectual center of the business.

---

# 15. Reputation should also be capability-specific

One universal reputation number is bad.

A worker might be:

```text
translation       .97
physical audits   .94
web research      .89
electronics       insufficient evidence
legal review      insufficient evidence
```

Likewise an agent:

```text
Python coding          .98
DevOps                 .91
financial procurement  .51
customer email         .95
```

You could expose:

```http
GET /reputation/:actor/:capability
```

and return:

```json
{
  "score": 0.941,
  "confidence": 0.88,

  "qualifying_receipts": 281,

  "evidence_mix": {
    "receiver_attested": 218,
    "independent_verified": 41,
    "self_reported": 22
  },

  "recency": 0.93
}
```

That is genuinely useful machine intelligence.

---

# 16. Economic stake can become another signal

One issue with fake reputation is that completely free feedback can be manufactured cheaply.

A receipt can contain:

```text
economic value
counterparty
escrow
settlement
refund
dispute
```

You don't want to blindly equate high-dollar work with quality.

But this gives anti-Sybil signals unavailable to star ratings:

```text
unique counterparties
economic diversity
task diversity
settlement history
independent evidence
account age
repeated reciprocal relationships
repeated identical work
```

The current ERC-8004 study explicitly highlights the need for stronger defenses around manipulation and grounded interactions. ([arXiv][2])

That's another potential paid API:

```http
GET /trust-risk/:actor
```

---

# 17. Work receipts don't need blockchain by default

This is important.

I would use:

```text
canonical JSON
hashes
signatures
append-only storage
Merkle/transparency mechanisms
selective disclosure
```

and make anchoring optional:

```text
SCITT
EAS
ERC-8004
other ledger
```

You want:

> cryptographically verifiable

not:

> everything must be a cryptocurrency transaction.

The new SCITT action-receipt work is attractive precisely because it is focused on signed, verifiable records rather than turning every action into an on-chain event. ([IETF Datatracker][22])

---

# 18. The physical-site receipt draft is an especially strong signal

There is even an emerging IETF draft applying SCITT-style receipts to **physical-site engagement**.

That overlaps unusually closely with:

```text
human performs task
↓
physical-world evidence
↓
signed receipt
↓
auditable history
```

It is still draft standards work—not an endorsed Internet Standard—but its existence suggests others independently see the same missing primitive. ([IETF Datatracker][23])

This one should be watched closely.

---

# 19. Another major opportunity: safety infrastructure for agent→human work

The RentAHuman empirical study found categories including:

```text
identity impersonation
credential abuse
reconnaissance
authentication circumvention
social manipulation
```

within posted tasks, and its authors were able to flag a meaningful portion using relatively simple screening rules. ([arXiv][10])

That suggests:

```http
POST /screen-task
```

before any RealityRouter execution.

Return:

```json
{
  "risk": "REVIEW",

  "categories": [
    "identity_sensitive",
    "credential_request"
  ],

  "physical_risk": "low",

  "privacy_risk": "high",

  "required_controls": [
    "human_review"
  ]
}
```

This fits KNOW + ACT + PROVE perfectly.

---

# 20. Verification itself can be routed

Interesting recursive idea:

Agent requests:

> prove X.

You determine best verifier.

```text
deterministic check
        ↓
CV model
        ↓
independent LLM
        ↓
human reviewer
        ↓
expert reviewer
        ↓
second physical observer
```

So:

```http
POST /verify
```

becomes another router.

Example:

```text
Claim:
"Shop sells product X."

CV detects product        .92
OCR detects price tag     .98
GPS confirms shop         .999
capture freshness         .97

combined:
.89

required:
.95

→ ask independent human

human says YES            .98

final confidence          .975
```

That's very agent-native.

---

# 21. The ultimate primitive might be `POST /outcome`

The five products eventually become:

```http
POST /outcome
```

Request:

```json
{
  "goal": "Determine whether ACME store currently stocks item X",

  "constraints": {
    "deadline": "3h",
    "budget": 7,
    "confidence": 0.97
  },

  "authority": {
    "mandate": "..."
  }
}
```

Your platform performs:

```text
1 determine permissions
2 determine execution options
3 estimate options
4 select executor
5 execute
6 collect evidence
7 verify
8 issue receipt
9 settle payment
10 update reputation
```

Response:

```json
{
  "status": "verified",

  "outcome": {
    "stocked": true,
    "price": 1.25
  },

  "confidence": 0.982,

  "cost": 4.31,

  "executor": "...",

  "evidence": [...],

  "receipt": "...",

  "authorization": "..."
}
```

That would be a genuinely ambitious infrastructure company.

---

# What I would build **now**

The research made the sequencing much clearer:

```text
PHASE 1
ProofSpec
EvidenceBundle
VerificationResult
ExecutionReceipt

            ↓

PHASE 2
Receipt index
Actor history
Capability history
Disputes

            ↓

PHASE 3
Evidence-grounded reputation

            ↓

PHASE 4
Human inference / escalation

            ↓

PHASE 5
Authority / mandate adapters

            ↓

PHASE 6
RealityRouter
```

**PROVE first.**

Not ACT first.

The marketplace already has competitors and severe cold-start problems.

Proof/receipts can serve *all* marketplaces.

---

# Your first API could genuinely be tiny

Something like:

```text
proofwork.dev
```

### Schemas

```text
TaskSpec
ProofSpec
EvidenceBundle
Verification
Receipt
Attestation
Actor
Capability
Dispute
```

### API

```http
POST /proof/spec
POST /proof/verify

POST /receipts
GET  /receipts/:id
POST /receipts/:id/verify

GET /actors/:id
GET /actors/:id/history
GET /actors/:id/reputation

POST /tasks/screen
```

### MCP

```text
generate_proof_requirements
verify_evidence
issue_receipt
verify_receipt
lookup_actor_history
lookup_capability_reputation
screen_real_world_task
```

That's an MVP you could actually ship.

---

## What is now in the workbook

The expanded workbook includes roughly:

* **38 competitive/adjacent entities** across all five ideas
* **18 major standards/protocols**
* **15 research papers** with direct product implications
* **19 open-source repositories/building blocks**
* buyer/WTP and pricing-unit mappings
* refined venture benchmark
* an individual dossier for every venture
* anti-moat / incumbent threats
* OSS integration paths
* major unsolved research questions
* a staged **12-month build sequence**
* specific defensibility strategy for each product

[Download the research database](sandbox:/mnt/data/agent_reality_ventures_deepdive_2026.xlsx)

The highest-conviction thesis after this pass is therefore:

> **Don't build “a marketplace where AI hires people.” Build the neutral evidence, receipt, reputation and routing infrastructure through which an autonomous system can safely trust work performed outside itself.**

If that layer wins, it doesn't matter whether tomorrow's executor is **a person, another agent, an API, a courier, a sensor or eventually a robot**. The same primitives—**mandate → work → evidence → verification → receipt → reputation**—still apply. ([IETF Datatracker][22])

* [wired.com](https://www.wired.com/story/ai-agent-rentahuman-bots-hire-humans?utm_source=chatgpt.com)
* [TechRadar](https://www.techradar.com/pro/were-the-layer-that-ai-needs-to-get-things-done-in-the-real-world-meatlayer-is-building-a-marketplace-where-ai-hires-humans-to-do-jobs?utm_source=chatgpt.com)
* [The Wall Street Journal](https://www.wsj.com/cio-journal/arcade-dev-raises-60-million-to-secure-ai-agents-5d07eff4?utm_source=chatgpt.com)

[1]: https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol?utm_source=chatgpt.com "Announcing Agent Payments Protocol (AP2)"
[2]: https://arxiv.org/abs/2606.26028?utm_source=chatgpt.com "Can Trustless Agents Be Trusted? An Empirical Study of the ERC-8004 Decentralized AI Agent Ecosystem"
[3]: https://arxiv.org/html/2606.04193v1?utm_source=chatgpt.com "Receiver-Attested Confidential Receipts for AI Agent Actions"
[4]: https://www.truepic.com/?utm_source=chatgpt.com "Truepic: Visual Risk Intelligence"
[5]: https://premise.com/?utm_source=chatgpt.com "Premise - Data for Every Decision™"
[6]: https://www.gigwalk.com/?utm_source=chatgpt.com "Gigwalk: We've got your brand's back - Gigwalk"
[7]: https://play.google.com/store/apps/details?hl=en&id=net.fieldagent&utm_source=chatgpt.com "Field Agent - Apps on Google Play"
[8]: https://www.helpnetsecurity.com/2026/05/28/digimarc-adds-provenance-audit-and-verification-controls-for-ai-agent-workflows/?utm_source=chatgpt.com "Digimarc adds provenance, audit, and verification controls ..."
[9]: https://rentahuman.ai/?utm_source=chatgpt.com "RentAHuman: Hire humans for any task."
[10]: https://arxiv.org/abs/2602.19514?utm_source=chatgpt.com "Security Risks of AI Agents Hiring Humans: An Empirical Marketplace Study"
[11]: https://www.techradar.com/pro/were-the-layer-that-ai-needs-to-get-things-done-in-the-real-world-meatlayer-is-building-a-marketplace-where-ai-hires-humans-to-do-jobs?utm_source=chatgpt.com "\"We're the layer that AI needs to get things done in the real world\": MeatLayer is building a marketplace where AI hires humans to do jobs"
[12]: https://developer.taskrabbit.com/docs/overview-taskrabbit-home-services-api?utm_source=chatgpt.com "Taskrabbit Home Services API - Overview"
[13]: https://github.com/humanlayer/humanlayer?utm_source=chatgpt.com "humanlayer/humanlayer: The best way to get AI coding ..."
[14]: https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation?utm_source=chatgpt.com "Human-in-the-Loop AI Agents: Approval Workflows"
[15]: https://arxiv.org/abs/2605.14830?utm_source=chatgpt.com "Agentic AI and Human-in-the-Loop Interventions: Field Experimental Evidence from Alibaba's Customer Service Operations"
[16]: https://workos.com/blog/delegated-access-ai-agents?utm_source=chatgpt.com "Delegated access for AI agents: The intersection rule explained"
[17]: https://www.entrust.com/blog/2026/05/ai-agent-authorization-delegation-zero-trust?utm_source=chatgpt.com "Why Accountable Delegation is Central to Your Trust Fabric"
[18]: https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/?utm_source=chatgpt.com "FIDO Alliance to Develop Standards for Trusted AI Agent ..."
[19]: https://www.wsj.com/cio-journal/arcade-dev-raises-60-million-to-secure-ai-agents-5d07eff4?utm_source=chatgpt.com "Arcade.dev Raises $60 Million to Secure AI Agents"
[20]: https://openfga.dev/?utm_source=chatgpt.com "OpenFGA: Fine-Grained Authorization"
[21]: https://arxiv.org/abs/2603.16586?utm_source=chatgpt.com "Runtime Governance for AI Agents: Policies on Paths"
[22]: https://datatracker.ietf.org/doc/html/draft-noa-scitt-ai-agent-receipt-01?utm_source=chatgpt.com "draft-noa-scitt-ai-agent-receipt-01"
[23]: https://datatracker.ietf.org/doc/draft-noa-scitt-ai-agent-receipt/?utm_source=chatgpt.com "draft-noa-scitt-ai-agent-receipt-00 - A SCITT Profile for AI- ..."
