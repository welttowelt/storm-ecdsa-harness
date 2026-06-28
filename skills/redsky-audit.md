# Skill: Redsky Audit

Use before paid compute, public claims, submission decisions, or any route that
could drift because it sounds plausible.

## Goal

Try to kill the route before the team spends more. The worker should look for
stale facts, missing evidence labels, illegal diffs, weak validators, bad
economics, unclear ownership, and absent kill gates.

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

When a claim requires private validation, require a redacted handoff that states
the validator, result class, and public-safe evidence label.

## Protocol

1. Refresh the current public truth before using memory.
2. Restate the route and claimed edge.
3. Check whether the evidence label matches the claim.
4. Identify the strongest objection.
5. Identify the fastest falsifier.
6. Check validator, owner, budget, and kill gate.
7. Classify the failure mode if the route is weak.
8. Return proceed, measure, park, kill, or request human review.

## Output

```text
Redsky audit:
- Route or claim:
- Current public truth checked:
- Evidence label:
- Strongest objection:
- Fastest falsifier:
- Failure class:
- Missing gate:
- Decision:
- Required verification:
```

## Completion Gate

Do not allow win language, paid compute, or public claims until the route
survives the required verification and any missing gate is closed.

For repeated Bluesky/Redsky loops, require a machine-readable packet before the
result steers workers:

```bash
python3 scripts/storm-bluesky-redsky-loop-gate.py \
  examples/bluesky-redsky-loop-pass.example.json \
  --require-implemented
```

The loop gate fails on missing Redsky fields, stale public-truth placeholders,
evidence-label mismatch, submit overclaim, ungated compute dispatch, and common
private-state leaks.
