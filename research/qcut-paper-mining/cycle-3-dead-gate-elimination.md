# qcut-paper-mining - Cycle 3 Dead Gate Elimination

Date: 2026-06-26

## Finding

Chen, Mendl, and Seidl, "Dead Gate Elimination" (arXiv:2504.12729) is directly
useful for the current q1152/q1153 work because it formalizes when a gate can
be removed relative to the subset of outputs that still matter.

The local translation is not "delete more gates". The useful rule is stricter:
every `drop_dead` index file is a proof artifact for one exact operation
stream and one exact valid-output support. After a Gidney, cascade, fold,
carry, codec, or allocator edit, old raw op indexes are stale unless regenerated
from the edited stream.

## Local Mapping

`src/point_add/mod.rs:apply_drop_dead_robust_if_enabled` removes operations by
enumerated op index, using `DROP_DEAD_FILE`, `DROP_DEAD_SECOND_FILE`, or
embedded fallback `.idx` files. That means a primitive replacement that changes
op count, target IDs, measurement bits, or operation order can make the old
drop list remove different gates from the ones that were proved dead.

This maps to the active Gidney q1152 lane: primitive selftests and raw/no-drop
results can be good while stale drops still corrupt the full route.

## Actionable Skill

Added `skills/paper-dead-gate-elimination.md` plus the `.agents` bridge. The
skill requires:

- raw/no-drop classification before any dead-drop diagnosis;
- regeneration of `.idx` files from the current edited stream;
- route commit, env, op count, and op-stream hash next to every drop artifact;
- `drop_effect_probe` or equivalent attribution for active dropped gates;
- full 9024-shot validation after applying regenerated indexes.

## Next Gate

For Gidney q1152:

```text
Gidney stream -> raw/no-drop classify -> regenerate .idx -> drop_effect_probe
-> apply explicit regenerated DROP_DEAD_FILE paths -> 9024 residual/eval.
```

Do not spend scanner lanes on stale embedded `.idx` routes.
