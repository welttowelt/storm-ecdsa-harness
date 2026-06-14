# Route Packet Example

## Identity

- Route ID: demo-route-current-target-first
- Source/base: public benchmark fixture
- Current frontier: refreshed public current target
- Expected edge: unknown until cheap falsifier passes
- Evidence label: Source fact plus Inference

## Claim

- What should improve: reduce wasted compute by refusing routes without a predicate
- Why it might work: many failed searches are missing a kill condition
- What would make it false: a route has a strong validator but the process blocks it

## Validation

- Cheap check: confirm the route names the global metric it intends to improve
- Full validator: official local benchmark validation, if a real candidate exists
- Official validation: required before any public win claim
- Dirty classes to track: local-only improvement, relocated peak, failed cleanup

## Compute

- Compute needed: none for this demo packet
- Predicate: dispatch only when the route predicts a measurable clean class
- Owner: ResearchLead_Worker
- Budget: zero paid compute for demo
- Stop condition: stop if validator or kill gate is missing

## Safety

- Public-credit policy: cite sources before sharing results
- Redaction concerns: keep private routes and logs outside this repo
- Submit gate: fresh frontier recheck, official local validation, score win, legal diff, public note
