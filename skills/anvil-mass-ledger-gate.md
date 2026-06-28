# Anvil Mass Ledger Gate

Use this before accepting an Anvil conditional-Toffoli mass/economics ledger as
packet-ready evidence.

## Command

    python3 scripts/storm-anvil-mass-ledger-gate.py \
      <anvil_conditional_toffoli_mass_ledger.tsv> \
      --require-pass

Defaults assume source `d44cad3`.

## Pass Requirements

- TSV/CSV has rows and required columns: `route_id`, `source_base`,
  `source_location`, `source_hash`, `candidate_class`, `current_q`, `target_q`,
  `current_avg_tof`, `predicted_avg_tof`, `candidate_score`, `score_edge`,
  `required_support`, `known_counterexample`, and `next_gate`.
- `no_submit_ack=yes` appears either in a comment or as a column.
- source is current, source locations are public `src/point_add/*.rs` sites, and
  source hashes are hash-shaped.
- numeric q/T fields parse, `candidate_score` matches
  `target_q * predicted_avg_tof`, and optional `frontier_score` matches
  `score_edge`.
- positive rows route to a bounded gate; counterexample rows route only to NACK,
  close, or hold.
- no pod, GPU, CPU, scanner, residual, benchmark, alert, or submit request is
  present.

## Decisions

- `pass`: ledger is machine-readable and ready for the next packet gate; no compute.
- `hold`: columns, fields, numeric values, support labels, or next gate are
  incomplete.
- `fail`: stale source, bad source/hash shape, score mismatch, nonpositive row
  routed to a positive gate, counterexample routed to a positive gate, compute
  request, submit/alert language, local-heavy context, or missing no-submit ACK.
