# Anvil Namespace Gate

Use this before promoting one high-mass Anvil row from raw `op_index` mass
inventory into source-bound proof work.

## Command

    python3 scripts/storm-anvil-namespace-gate.py \
      <redacted-anvil-namespace-packet.txt> \
      --require-pass

Defaults assume source `d44cad3`, `q=1152`, frontier score `1,571,592,960`,
and the same-q mass bar of `2,439` executed Toffoli-shots.

## Pass Requirements

Common fields:

- `route_id`, owner/ACK, `next`, `source_base`, `frontier_score`, `q`, and
  `no_submit_ack=yes`;
- raw Anvil row fields: `op_index`, `kind`, `q_target`, `q_c1`, `q_c2`, and
  `expected_shot_mass`;
- `index_namespace`, `namespace_status=MATCHED` or `BOUND`, and
  `source_binding_status=BOUND`;
- support index, support op id, or trace-context hash;
- no pod, residual, benchmark, scanner, alert, submit, or win language.

Packet-ready rows also need source location/hash, candidate index hash,
source-bound context, trace-context family, `evidence_label=Prefilter`, and open
support/proof status. They route to exact-support or source-packet proof review,
with no compute.

Closure rows instead need `support_status=COUNTEREXAMPLE`,
`proof_status=COUNTEREXAMPLE`, closure reason or witness, and a next row. They
must not claim a negative expected delta.

## Decisions

- `pass`: row is source-bound for proof review, or closed by counterexample; no
  compute.
- `hold`: namespace/source binding is missing, mismatched, ambiguous, or
  incomplete.
- `fail`: stale source, wrong q-tier, below-bar positive mass, result overclaim,
  local-heavy context, compute/submit language, or missing no-submit ACK.
