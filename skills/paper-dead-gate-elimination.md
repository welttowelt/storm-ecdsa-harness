# Skill: Paper - Dead Gate Elimination

Use when a lower-Q route edits the operation stream and then wants to keep,
regenerate, audit, or apply a `DROP_DEAD_*` index file.

## Source

- Yanbin Chen, Christian B. Mendl, and Helmut Seidl, "Dead Gate
  Elimination", arXiv:2504.12729.

## Why We Keep It

The paper defines dead gates relative to the outputs that still matter, then
removes them by repeatedly walking the circuit frontier. That matches our
`drop_dead` tooling closely enough to be dangerous: a dead-gate set is not a
portable list of op indexes. It is a proof artifact for one exact op stream,
one exact output-support set, and one exact ordering of live dependencies.

This is the active failure class for Gidney/q1152 work. The adder can pass
selftests and a raw/no-drop route can improve, while a stale `.idx` file still
deletes the wrong operations after the op footprint changes.

## Apply To

- `DROP_DEAD_ROBUST`, `DROP_DEAD_ROBUST_SECOND`, `DROP_DEAD_FILE`,
  `DROP_DEAD_SECOND_FILE`;
- `src/point_add/mod.rs:apply_drop_dead_robust_if_enabled`;
- `src/bin/drop_effect_probe.rs`;
- any Gidney, conditionally-clean, cascade, fold, carry, codec, or allocator
  edit that changes op count, op kind, target IDs, measurement bits, or
  transcript/output support.

## Required Invariant

For every removed operation, prove on the current stream that all of its
outputs are outside the valid output support, or that removing the operation
preserves the valid-output distribution under the exact circuit context.

The proof is invalidated by:

- different source commit or route defaults;
- different nonce-binding stream if the nonce changes op identity;
- changed op count, op order, gate kind, qubit ID, bit ID, register ID, or
  condition bit before any removed index;
- changed valid-output support or residual/eval target set.

## Procedure

1. Start from a raw route:
   `DROP_DEAD_ROBUST_DISABLE=1 DROP_DEAD_ROBUST_SECOND=0`.
2. Confirm the raw route's failure class with full residual/eval before any
   dead-drop analysis. If raw is value-dirty, do not regenerate drops yet.
3. Generate the dead set from the current edited stream only. Include route
   commit, env, emitted op count, gate-kind histogram, and a hash of the
   pre-drop op stream next to the `.idx`.
4. Run `drop_effect_probe` or equivalent attribution against the current
   stream. Any active dropped gate on failing shots blocks the drop set.
5. Apply the regenerated `.idx` files through explicit env paths, not embedded
   fallbacks:
   `DROP_DEAD_FILE=<new.idx> DROP_DEAD_SECOND_FILE=<new2.idx>`.
6. Rebuild and run the full 9024-shot gate. Only `0/0/0` promotes the route to
   nonce hunting or benchmark scoring.

## Gidney q1152 Gate

Use this exact sequence before spending scanner time:

```text
Gate A: Gidney primitive selftest passes.
Gate B: raw/no-drop full route is value/phase/ancilla classified.
Gate C: regenerate .idx from the Gidney stream, not from baseline q1153.
Gate D: apply only regenerated .idx files and run 9024-shot residual/eval.
Gate E: only if D is clean, run island hunt and official benchmark.
```

If Gate B has sparse nonce-dependent failures but zero ancilla garbage, the
dead-drop problem is solved only after Gate D, not after the raw result.

## Local Fit Test

In the current TLM tree, `apply_drop_dead_robust_if_enabled` parses `.idx`
files as raw operation indexes and removes matching enumerated operations. The
embedded defaults are therefore stream-specific. A Gidney suffix that allocates
fewer qubits or measurement bits can shift downstream op indexes, so the old
indexes no longer identify the same proof obligations.

The paper also warns against a naive rule that deletes gates merely because
they write to a dead qubit: controlled gates can still change valid outputs
through their controls. For our route, this means candidate drops must be
validated against controls, conditions, transcript bits, and phase effects, not
just final target liveness.

## Output

```text
Dead gate elimination audit:
- Paper:
- Route/commit/env:
- Pre-drop op count/hash:
- Valid output support:
- Drop source: embedded / regenerated / unknown
- Drop counts:
- Active dropped gates on failing shots:
- Raw no-drop result:
- Regenerated-drop result:
- Decision: accept / regenerate / block / park
```

## Kill Gate

Do not use embedded or stale `.idx` files after any op-stream edit. Do not
start a nonce hunt from a route whose only evidence is raw/no-drop improvement
unless the regenerated dead-drop gate has already passed or the submitted route
will deliberately run with all dead drops disabled and still beat the frontier.
