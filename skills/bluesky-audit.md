# Skill: Bluesky Audit

Use when a route, product idea, research direction, or public note may have
upside but needs a sharper path before it receives serious time or compute.

## Goal

Find the best bounded way the idea could work. The worker should be optimistic,
but every suggestion must remain falsifiable.

## Public Boundary

Do not request or expose:

- private endpoints,
- account details,
- keys or tokens,
- raw logs,
- unreleased nonces,
- live candidate diffs,
- private mailbox history,
- submit authority.

If the route needs private state, request a narrow handoff and explain what
public or local evidence justifies it.

## Protocol

1. Restate the route or idea in one sentence.
2. Name the best case if the idea is real.
3. Identify the missing measurement that would unlock confidence.
4. Propose one bounded experiment that can run cheaply.
5. Propose one creative alternative that preserves the upside.
6. Name the hidden assumption that could make the optimistic case wrong.
7. Define a stop condition so optimism does not become drift.

## Output

```text
Bluesky audit:
- Route or idea:
- Best case:
- Missing measurement:
- Smallest useful experiment:
- Bounded alternative:
- Hidden assumption:
- Stop condition:
- Decision:
```

## Completion Gate

Bluesky does not approve compute or publication by itself. A route still needs a
validator, owner, budget, kill gate, and evidence label before it can advance.

For multi-pass process hardening, pair Bluesky with Redsky and emit a
machine-readable packet through:

```bash
python3 scripts/storm-bluesky-redsky-loop-gate.py \
  examples/bluesky-redsky-loop-pass.example.json \
  --require-implemented
```

That gate checks loop count, required fields, evidence labels, implementation
status, verification text, and public-boundary leakage. It still does not
authorize compute or submit.
