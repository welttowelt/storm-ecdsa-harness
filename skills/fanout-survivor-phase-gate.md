# Fanout Survivor Phase Gate

Use this when a q1152 SINGLE_CCX_FANOUT GPU worker prints a survivor or CLEAN
row.

## Gate

Run the mixed GPU/eval logs through:

    python3 scripts/storm-fanout-survivor-phase-gate.py GPU_OR_EVAL_LOG [...]

For raw eval_circuit stdout that does not include the nonce, attach it
explicitly:

    python3 scripts/storm-fanout-survivor-phase-gate.py eval.out --nonce N --mark-survivor

If the validation checkout does not already expose ISLAND_FAST_EXIT, use
skills/official-fast-exit-eval.md and patches/eval-fast-exit-dirty-triage.patch
to add the local dirty-triage helper first.

The gate reports one of:

- ready: at least one survivor has official counts 0/0/0 and must enter the
  validation-submit gate. It is not a submit authorization.
- hold: a GPU survivor exists but no phase-aware official eval count exists.
- nack: all official-evaluated survivors are dirty.
- fail: no usable survivor/eval evidence was found.

Only ready can move to the validation-submit gate and fresh frontier recheck.
It is still not a submit authorization.

## Discipline

- Treat GPU CLEAN as stage-1 survivor, not as clean circuit evidence.
- Trusted eval must check classical mismatch, phase garbage, and ancilla
  garbage.
- Raw fast-exit eval stdout is valid for dirty triage when the nonce is attached
  out-of-band and the route is still labelled survivor-only.
- A survivor with phase garbage is a prefilter false positive, even if the GPU
  predicate passed.
- If phase_dirty is greater than zero, steer future compute toward official
  fast-exit verification or a phase-aware predicate before widening GPU spend.
- Do not write winner sentinels, alert, or submit from this gate.

## Output Contract

    fanout_survivor_phase_gate=<ready|hold|nack|fail> gpu_survivors=N official_evals=N official_clean=N official_dirty=N missing_official=N phase_dirty=N classical_dirty=N ancilla_dirty=N phase_gap=<true|false> submit_authorized=false decision=...

## Fleet Use

Place this gate after the qstate guard and before any handoff that uses clean,
winner, or FOR-AKASH language. It turns the fanout route into:

    qstate ok -> GPU survivor -> official phase-aware eval -> frontier recheck -> submit gate

If the gate returns nack with phase dirt, keep harvesting owner-led survivors
only when a fast official validator is attached. Otherwise redesign the
prefilter or park the fanout nonce lane.
