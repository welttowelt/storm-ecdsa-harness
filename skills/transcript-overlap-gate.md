# Transcript Overlap Gate

Use this before implementing or scaling a q1147/q1152 drop packet that depends
on transcript peak-overlap, origin-map, or active-drop inventory evidence.

## Command

    python3 scripts/storm-transcript-overlap-gate.py <redacted-transcript-packet>

Add --require-pass when the caller needs a hard shell gate.

## Pass Requirements

- route_id, owner, next, current source/base, frontier_score, and q-tier;
- source hash and source-bound context;
- transcript peak-overlap inventory with peak_rows and overlap_rows;
- all required peak calls are covered, when required_calls is present;
- exact support is CERTIFIED;
- score edge is positive, either explicit or computed from q and avgT;
- stale_index_warnings=0;
- origin map is source-bound, not active-only;
- bounded dirt counters are clean;
- evidence label is Prefilter or Partial;
- no_submit_ack=yes.

## Decisions

- pass: source-theorem-review-no-compute.
- hold: inventory is incomplete.
- fail: active-only origin map, stale indices, missing required calls, dirty
  bounded probe, support counterexample, stale source, no score edge, premature
  compute/residual/benchmark request, or submit/Akash/winner language.

This gate only parses redacted summaries. It does not run miners, build/eval,
SSH job control, alerts, or submit.
