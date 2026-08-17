# Acceptance Criteria — Market Intelligence v1

## MI-1 Observation substrate
PASS when:
- >=5 Oracle adapters emit valid observations
- all artifacts hashed
- connector failure semantics tested

## MI-2 Signal engine
PASS when:
- robust velocity/burst/persistence work on real historical data
- no raw cross-source metric arithmetic

## MI-3 Topic radar
PASS when:
- produces ranked Watch/Research topics
- every topic includes evidence IDs
- manual audit finds no fabricated source facts

## MI-4 Opportunity miners
PASS when:
- >=4 miners implemented
- one cross-oracle miner implemented
- Opportunity != Solution tests pass

## MI-5 Unignorant adapter
PASS when:
- at least 5 high-value Unignorant data families can become MarketObservations
- original upstream source identity preserved

## MI-6 Factory Resolver
PASS when:
- existing/extend/genesis decisions pass boundary tests

## MI-7 Factory Genesis
PASS when:
- a candidate factory can be proposed from a real opportunity cluster
- hard gates demonstrably prevent frivolous factories

## MI-8 External-agent test
Give a fresh Hermes agent:

> Find one evidence-backed growth-market opportunity using at least two independent
> source families, explain the problem, generate three solution hypotheses, choose
> the cheapest falsification experiment, and decide which factory should own it.

PASS only if all evidence can be followed.

## MI-9 Historical replay
Backtest topic/opportunity logic on earlier windows.

Goal:
- determine whether high-scoring signals preceded durable adoption/opportunity;
- calibrate thresholds.

Do not claim predictive validity before this exists.
