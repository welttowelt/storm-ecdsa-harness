# Anvil Exact Redundancy Gate

Use this before promoting one high-mass Anvil conditional op from mass inventory
into exact-redundancy review.

## Command

    python3 scripts/storm-anvil-exact-redundancy-gate.py \
      <redacted-anvil-exact-redundancy-packet.txt> \
      --require-pass

Defaults assume source `d44cad3`, `q=1152`, `shots=9024`, frontier avg-Toffoli
`1,364,230`, frontier score `1,571,592,960`, and current total Toffoli
`12,310,809,446`.

## Pass Requirements

- Packet names `route_id`, owner/ACK, next gate, `source_base`, public
  `src/point_add/*.rs:<line>` location, source hash, candidate/proof hash, and
  exact-redundancy candidate class.
- Packet binds one raw Anvil op with `op_index`, `kind`, `q_target`, `q_c1`,
  `q_c2`, `c_condition`, and `expected_shot_mass`.
- Same-q redundancy only: `target_q` cannot claim a q-cut.
- `expected_shot_mass` clears the same-q rounding bar, and
  `expected_avgT_delta`, `candidate_score`, and `score_edge` must not overclaim
  what that mass can buy.
- Positive packets need `support_status=CERTIFIED`, `proof_status=CERTIFIED`,
  `exact_support=CERTIFIED`, restore/phase/ancilla proof flags, allocator-order
  evidence, and `no_submit_ack=yes`.
- Counterexample closures need an explicit closure reason, witness, falsifier, or
  counterexample artifact.
- No pod, GPU, CPU, scanner, residual, benchmark, alert, submit, or win language
  is present.

## Decisions

- `pass`: exact-redundancy proof or counterexample closure is ready for Storm
  review; no compute.
- `hold`: source/op/economics fields or proof flags are incomplete.
- `fail`: stale source, q-cut overclaim, below-bar mass, score/delta overclaim,
  result overclaim, compute/submit language, local-heavy context, or missing
  no-submit ACK.
