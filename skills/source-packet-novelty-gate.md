# Source Packet Novelty Gate

Use this before a worker opens a new source-line packet after an UNKNOWN bucket
was closed by existing counterexample ledgers.

## Command

    python3 scripts/storm-source-packet-novelty-gate.py <redacted-packet-or-summary>

Add --require-pass when the caller needs a hard shell gate.

## Pass Requirements

- packet has route_id, owner, next, frontier_score, and the expected q-tier;
- source is bound to the current frontier and includes a source hash;
- packet includes a candidate index/diff hash so the proposed row can be
  reproduced and compared against later proof output;
- source location is a public `src/point_add/*.rs:<line>` site, including
  non-`trailmix_ludicrous` support code such as `arith.rs`;
- packet names scored kind `CCX` or `CCZ`, evidence label, and expected
  negative delta;
- novelty is explicit: novelty_status=NEW, outside_closed_ledger=yes, or
  ledger_hit=no;
- packet is aimed at one bounded source proof, certificate, or counterexample;
- no_submit_ack=yes is present.

## Decisions

- pass: admit one bounded source-proof step; no compute, alert, or submit.
- hold: novelty or source-binding evidence is incomplete.
- fail: existing counterexample ledger hit, exhausted source-family summary,
  all current unknowns already closed, non-scored op kind such as `CX`, `CZ`,
  `X`, or `SWAP`, stale source, wrong q-tier, local-heavy context, compute
  request, premature Akash/submit language, overclaimed evidence label, missing
  no-submit ACK, or nonnegative expected delta.

This gate only parses redacted packets and ledger summaries. It does not run
miners, build/eval, SSH job control, alerts, or submit.
