# Skill: Paper - Score Condition Discount

Use when a paper-mining hit promises lower T-count, T-depth, relative-phase
Toffoli, or conditional replay, and a worker wants to convert it into an
ecdsa.fail q1152 average-Toffoli route.

## Source

- Any paper route that changes T-count/T-depth without deleting benchmark IR
  `CCX`/`CCZ` operations.
- Any paper route that claims an average-executed gate discount from
  conditioning.

## Why We Keep It

The ecdsa.fail score counts average executed `CCX`/`CCZ` through the trusted
simulator. Quantum-control sparsity does not discount a Toffoli in the scorer:
only a classical `c_condition` or active `push_condition` mask reduces the
charged shots.

This means T-depth and relative-phase papers are useful only after a source
translation step:

- delete scored `CCX`/`CCZ`;
- move scored `CCX`/`CCZ` under a measured classical condition;
- or prove a trusted eval `avg_tof` change.

## Required Invariant

For a q1152 avgT route, state the exact source mechanism:

```text
source_file/function:
paper_mechanism:
scored_IR_effect: delete_CCX_CCZ / classically_discount_CCX_CCZ / no_score_effect
condition_source: measured_bit / condition_stack / none
phase_proof:
ancilla_proof:
expected_avgT_delta:
count_gate:
```

If `scored_IR_effect=no_score_effect`, do not run residuals, pods, nonce search,
or benchmark submission from the paper hit.

## Software Gate

Use the source theorem packet:

```bash
scripts/storm-q1152-avgt-theorem.py \
  --sim-rs <challenge>/src/sim.rs \
  --eval-circuit-rs <challenge>/src/bin/eval_circuit.rs \
  --circuit-rs <challenge>/src/circuit.rs \
  --point-add-mod-rs <challenge>/src/point_add/mod.rs \
  --ops-bin <challenge>/ops.bin \
  --paper-summary <paper-mining-summary.md>
```

The toy falsifier inside the script records the core scoring fact:

```text
quantum-sparse-control CCX charged shots == unconditioned CCX charged shots
classical-conditioned CCX charged shots < unconditioned CCX charged shots
```

## Output

```text
q1152 avgT source theorem:
- Source scorer:
- Candidate paper:
- Source file/function:
- Exact local invariant:
- Toy or trace falsifier:
- Expected avgT delta:
- Correctness risk channel:
- Count gate:
- Decision: source-theorem / needs-hook / no-score-effect / NACK
```

## Kill Gate

Do not treat a T-count, T-depth, or relative-phase improvement as a benchmark
route unless the current source or op-stream evidence shows a scored `CCX`/`CCZ`
deletion, a measured classical condition discount, or a trusted eval avgT cut.
Quantum data controls alone are not an average-Toffoli discount in this scorer.
