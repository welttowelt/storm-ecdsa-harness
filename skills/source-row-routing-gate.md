# Source Row Routing Gate

Use this after a q1152 source scout row is assigned. The worker must return
either a packet-ready row for one bounded source proof, or a counterexample
closure that advances to the next row.

## Command

    python3 scripts/storm-source-row-routing-gate.py \
      <redacted-source-row-routing-packet.txt> \
      --require-pass

## Pass Requirements

Common fields:

- route_id, owner, next, rank, count, source_base, frontier_score, q;
- source_hash and source_location;
- kind and evidence_label=Prefilter;
- studio or remote context;
- no_submit_ack=yes;
- no compute, pod, residual, benchmark, alert, or submit language.

Packet-ready rows also need scored kind `CCX` or `CCZ`,
candidate_index_hash, primitive_family,
expected_avgT_delta<0, novelty_status=NEW or outside_closed_ledger=yes,
support_status=UNKNOWN, proof_status=UNPROVEN, and proof_backlog for one bounded
source proof.

Closure rows instead need support_status=COUNTEREXAMPLE,
proof_status=COUNTEREXAMPLE, closure_reason or counterexample_artifact, and
next_source_row or next=next-CCX-source-row. Closure rows must not claim a
negative expected delta.

## Decisions

- pass: source-row-packet-ready-no-compute.
- pass: source-row-closed-advance-next-no-compute.
- hold: incomplete packet or closure metadata.
- fail: stale source, wrong q-tier, packet-ready non-scored op kind such as
  `CX`, `CZ`, `X`, or `SWAP`, local-heavy context, compute request,
  submit/alert language, missing no-submit ACK, overclaimed result label, or
  counterexample closure that still claims a negative delta.
