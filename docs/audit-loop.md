# Audit Loop

The Storm harness uses critique before compute. A route should survive a
small audit loop before it receives worker time, paid CPU/GPU time, or public
claims.

## Core RCI / Tony Loop

Use this shape for docs, prompts, route packets, and candidate decisions:

```text
Inspect -> identify concrete problems -> cite evidence -> explain effect -> propose smallest fix -> gate -> implement -> verify
```

The point is to avoid role-only prompting. A worker should not just say "I am an
expert." It should state the criteria that could kill the route and the evidence
that would let it proceed.

## Audit Roles

### RCI / Tony Audit

Use for critique-before-rewrite or critique-before-build.

Standalone skill card: `skills/tony-rci-audit.md`.

Required output:

- Problem
- Evidence
- Effect
- Source or implementation check
- Smallest useful fix
- Gate

### Anton Audit

Use for claim safety, public framing, credits, and reader path.

Best for:

- public notes,
- README language,
- attribution,
- safety/disclosure framing,
- overclaim detection.

### Bluesky Audit

Use for constructive search before killing a route.

Standalone skill card: `skills/bluesky-audit.md`.

Best for:

- "what would make this work?"
- "what missing measurement would unlock it?"
- "what bounded alternative keeps upside?"
- "what is the smallest useful experiment?"

Bluesky output should be optimistic but falsifiable.

### Redsky Audit

Use for adversarial frontier work.

Standalone skill card: `skills/redsky-audit.md`.

Best for:

- stale frontier checks,
- legality checks,
- evidence-label checks,
- validator and kill-gate checks,
- search-economics checks,
- submit-gate checks.

Redsky output should try to kill the route before paid compute.

## Standard Route Review

For a real route:

1. Research lead writes a route packet.
2. Bluesky proposes the best bounded path if the idea is real.
3. Redsky tries to kill it.
4. RCI/Tony turns the critique into smallest useful fixes.
5. Cheap validation runs before paid compute.
6. Compute request is written only if the route has owner, validator, predicate,
   budget, and kill gate.
7. Scanner hits remain `Prefilter`.
8. Public note is written only after official validation or as a clearly labeled
   non-winning research note.

## Minimum Gate Before Paid Compute

No paid compute unless the packet answers:

- What exact metric should move?
- What evidence label do we have now?
- What validator will confirm or reject it?
- What dirty class or failure mode do we expect?
- What stop condition prevents endless search?
- What public/private boundary applies?

If any answer is missing, park the route and fix the packet first.

## Minimum Gate Before Public Claim

No public claim unless the note states:

- evidence label,
- validation state,
- source/base,
- caveats,
- credits,
- what is not proven.

Do not call `Prefilter`, paper score, or partial validation a win.
