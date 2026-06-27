# Skill: Support-Bounded Vented Dead-Carry

Use when a route tries to reduce Toffoli or peak pressure by combining two
mechanisms:

- skip carry rows that are source-certified dead; and
- measurement-vent only the remaining live carry rows within a hard headroom cap.

## Source Hook

This pattern is extracted from the promoted `d44cad3` stack:

- `add_cout_vented_skip_dead` in `src/point_add/trailmix_ludicrous/arith.rs`;
- square-reduce add/sub callsites gated by `TLM_SQUARE_VENT_SHIFTED`;
- `TLM_SQUARE_PEAK_CAP` and `TLM_SQUARE_VENT_MARGIN` for headroom control;
- `cuccaro_call_has_structurally_dead_carry(call_index, i)` for the dead-row
  predicate.

## Why We Keep It

The useful move is not "vent more carries". The useful move is preserving the
same value semantics while spending vent ancillae only on rows that remain live
after the dead-carry predicate. This captures both savings:

- dead rows emit no carry work; and
- live rows use HMR plus `cz_if_bit` instead of a reverse CCX when there is
  enough headroom.

## Required Invariant

For every transformed callsite, prove:

- the dead predicate is source-hash-bound and value-exact for that `call_index`;
- the vented row uses the same `a[i]`, `b[i]`, and carry target as the original
  MAJ/UMA pair;
- the HMR bit receives the exact `ta & tb` value needed for phase discharge;
- every vent ancilla is zeroed and freed before any downstream borrower;
- `active_qubits` never exceeds the refreshed target cap; and
- count arithmetic clears the refreshed q-tier threshold.

## Procedure

1. Run a fresh trace with source context and near-peak allocation rows.
2. Identify the carry call family and preserve the same call index used by the
   dead-carry predicate.
3. Prove each skipped row through `scripts/storm-exact-miner.py`; UNKNOWN rows
   do not become skip rows.
4. Compute the headroom budget as `target_cap - live - margin`.
5. Vent only while budget remains; fall back to the original CCX for the rest.
6. Run count first, then route compare/residual, then trusted eval.

## Output

```text
Support-bounded vented dead-carry:
- Source base/hash:
- Call family and call_index:
- Dead predicate source:
- Target cap/margin:
- Live rows vented:
- Dead rows skipped:
- Count delta:
- Residual/eval:
- Decision: route / narrow / park
```

## Kill Gate

Park the route if any of these are true:

- dead-row support is UNKNOWN or source-hash mismatched;
- call-index drift changes the dead predicate;
- vent budget is inferred from stale active counts;
- HMR phase discharge is not proven for the same transformed operands;
- the route needs factor-2 recompute economics; or
- the count edge does not beat the refreshed q-tier threshold.
