# Fanout Survivor Phase Gate

Use this when a q1152 SINGLE_CCX_FANOUT GPU worker prints a survivor or CLEAN
row.

## Gate

Run the mixed GPU/eval logs through:

    python3 scripts/storm-fanout-survivor-phase-gate.py GPU_OR_EVAL_LOG [...]

The gate reports one of:

- ready: at least one survivor has trusted official counts 0/0/0.
- hold: a GPU survivor exists but no phase-aware official eval count exists.
- nack: all official-evaluated survivors are dirty.
- fail: no usable survivor/eval evidence was found.

Only ready can move to a fresh frontier recheck. It is still not a submit
authorization.

## Discipline

- Treat GPU CLEAN as stage-1 survivor, not as clean circuit evidence.
- Trusted eval must check classical mismatch, phase garbage, and ancilla
  garbage.
- A survivor with phase garbage is a prefilter false positive, even if the GPU
  predicate passed.
- If phase_dirty is greater than zero, steer future compute toward official
  fast-exit verification or a phase-aware predicate before widening GPU spend.
- Do not write winner sentinels, alert, or submit from this gate.

## Output Contract

    fanout_survivor_phase_gate=<ready|hold|nack|fail> gpu_survivors=N official_evals=N official_clean=N official_dirty=N missing_official=N phase_dirty=N classical_dirty=N ancilla_dirty=N phase_gap=<true|false> decision=...

## Fleet Use

Place this gate after the qstate guard and before any handoff that uses clean,
winner, or FOR-AKASH language. It turns the fanout route into:

    qstate ok -> GPU survivor -> official phase-aware eval -> frontier recheck -> submit gate

If the gate returns nack with phase dirt, keep harvesting owner-led survivors
only when a fast official validator is attached. Otherwise redesign the
prefilter or park the fanout nonce lane.
