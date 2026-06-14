# Operator Card Example

## Worker

- Name: PressureTest_Worker
- Role: critique route before compute
- Allowed work: source reading, invariant checks, cheap local validation design
- Not allowed: paid compute dispatch, submit decisions, private endpoint access

## Inputs

- Current target: public frontier refreshed by the lead
- Active route: demo-route-current-target-first
- Evidence label: Source fact plus Inference
- Source: public benchmark plus sanitized route packet

## Task

- Decision needed: should this route receive paid compute?
- Exact next action: identify the cheapest falsifier and one bounded alternative
- Validator: official local validation must be named before compute
- Kill gate: reject if no predicate distinguishes expected clean cases from dirty cases

## Output Required

- ACK or correction: ACK with objections, or correction with cited reason
- Falsifiable decision: proceed only if the route has a validator and stop condition
- Best objection: the route may only move a local metric while global score relocates
- One bounded alternative: instrument the binding phase first
- Confidence: medium until a cheap validation run exists
- Read receipt requested from: ResearchLead_Worker
