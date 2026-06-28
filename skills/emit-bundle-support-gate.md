# Emit Bundle Support Gate

Use this before promoting a combined real-emit support packet from the q1152
fallback lane where no single emitted row clears the 2,439-shot same-q bar.

## Command

    python3 scripts/storm-emit-bundle-support-gate.py \
      <redacted-emit-bundle-packet.txt> \
      --require-pass

Defaults assume source `d44cad3`, q1152, total Toffoli `12,310,809,446`, and
9,024 shots. Override only after a fresh frontier lock changes those public
facts.

## Pass Requirements

- route id, owner, next action, `source_base=d44cad3`, `q=1152`,
  frontier score, candidate hash, at least two source locations, source hashes,
  row count, total bundle shot mass, max single-row shot mass, and
  `no_submit_ack=yes`.
- Certified packets need a true shared invariant across the bundle, total shot
  mass at or above the strict same-q rounding bar, max single-row mass below the
  bar, `expected_avgT_delta<0`, `support_status=CERTIFIED`,
  `proof_status=CERTIFIED`, `restore_proof=1`, and `phase_proof=1`.
- Counterexample closures need support/proof COUNTEREXAMPLE, restore and phase
  proof flags, and an explicit closure reason or artifact.
- No live witness, differing witness, closed-ledger hit, default-on table row,
  pod, GPU, CPU, scanner, residual, benchmark, alert, or submit request.

## Decisions

- `pass`: certified bundle packet or explicit counterexample closure, both
  no-compute.
- `hold`: source, candidate, bundle, invariant, or proof fields are missing.
- `fail`: below-bar mass, single-row packet, non-shared invariant, live/different
  witness, UNKNOWN/UNPROVEN proof, closed/default-on rows, compute request,
  submit/alert language, stale source, wrong q-tier, or missing no-submit ACK.
