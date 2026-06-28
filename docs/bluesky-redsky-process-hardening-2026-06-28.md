# Bluesky/Redsky Process Hardening - 2026-06-28

Scope: public-safe harness gates only. No solver worktree edits, no compute,
no alert, and no submit authority.

## Loop 1: Transcript Peak-Overlap Packets

Bluesky audit:
- Route or idea: Admit transcript peak-overlap packets only when they are
  source-bound and complete enough for theorem review.
- Best case: Workers can turn q1147/q1152 overlap inventory into a bounded
  source theorem without jumping to residuals or pods.
- Missing measurement: required peak calls covered by the inventory.
- Smallest useful experiment: Parse pass/hold/fail/stale redacted packets.
- Stop condition: active-only origin, stale index warnings, dirt, missing calls,
  no score edge, compute language, or submit language.

Redsky audit:
- Strongest objection: Active-only maps and dirty bounded probes can produce
  attractive paper deltas detached from source truth.
- Fastest falsifier: fail packets with `active_only_origin_map`,
  `stale_index_warnings`, `dirty_bounded_probe`, or `score_no_edge`.
- Decision: Implemented `storm-transcript-overlap-gate.py`.

## Loop 2: Source Packet Location Breadth

Bluesky audit:
- Route or idea: Let source novelty packets cover all public `src/point_add`
  support sites, not only one subdirectory.
- Best case: FFG/arith proof packets can enter one bounded source proof without
  a false parser hold.
- Missing measurement: a non-`trailmix_ludicrous` fixture.
- Smallest useful experiment: `source_location=src/point_add/arith.rs:1322`.
- Stop condition: still require source hash, current base, q-tier, negative
  delta, novelty, and `no_submit_ack=yes`.

Redsky audit:
- Strongest objection: Broader paths could admit unrelated files.
- Fastest falsifier: keep the regex pinned to `src/point_add/*.rs:<line>`.
- Decision: Broadened `storm-source-packet-novelty-gate.py` and added the
  arith pass fixture.

## Loop 3: Scanner Restart Discipline

Bluesky audit:
- Route or idea: A scanner restart should carry the same route packet facts as
  a compute request.
- Best case: Certified source evidence can unlock one bounded owned range while
  blocking stale or ownerless loops.
- Missing measurement: validator, budget, stop condition, current source,
  frontier score, q-tier, and negative edge.
- Smallest useful experiment: require those fields in the restart pass fixture.
- Stop condition: missing metadata holds; stale source or wrong q-tier fails.

Redsky audit:
- Strongest objection: A bare `route_ack=yes support_status=CERTIFIED` line can
  restart paid scanners without budget or kill gate.
- Fastest falsifier: fail/hold any scanner packet missing budget or stop.
- Decision: Tightened `storm-compute-restart-gate.py`.

## Loop 4: Candidate Validation Freshness

Bluesky audit:
- Route or idea: Candidate packets should be able to pass only with fresh source
  base and no alert/submit wording.
- Best case: Clean remote validation can be handed to Storm for fresh frontier
  review without becoming automatic submit or mobile-alert authority.
- Missing measurement: stale-source candidate fixture.
- Smallest useful experiment: `source_base=58866a2` with otherwise clean
  c/p/a should fail.
- Stop condition: stale source, local host, dirty c/p/a, score no edge, missing
  no-submit ACK, or premature alert language.

Redsky audit:
- Strongest objection: Missing source base was only a warning even though the
  skill says it is required.
- Fastest falsifier: make missing source a hold and stale source a fail.
- Decision: Tightened `storm-candidate-validation-packet-gate.py`.

## Loop 5: Regression Evidence

Bluesky audit:
- Route or idea: Every process improvement should become a fixture-backed check.
- Best case: Future workers can rerun one public command and see the same gate
  behavior.
- Missing measurement: public harness coverage for each new behavior.
- Smallest useful experiment: wire new fixtures into `check-public-harness.sh`.
- Stop condition: no merge until public harness, redaction, Python compile, and
  diff checks pass.

Redsky audit:
- Strongest objection: Parser changes can silently drift without examples.
- Fastest falsifier: run pass/hold/fail/stale fixtures under `--require-pass`.
- Decision: Added regression assertions for transcript overlap, arith source
  novelty, stale validation packets, and scanner restart metadata.

## Implemented Changes

- Added transcript-overlap gate, skill card, bridge, and four fixtures.
- Broadened source-packet novelty parsing from one subdirectory to
  `src/point_add/*.rs:<line>`.
- Required scanner restart packets to include source, frontier, q-tier,
  negative edge, validation owner, budget, and stop condition.
- Required candidate validation packets to include fresh source base.
- Added stale-source and arith-source fixtures.

## Verification Evidence

- `scripts/check-public-harness.sh` -> pass
- `scripts/redaction-check.sh` -> pass
- `find scripts -name '*.py' -print0 | xargs -0 python3 -m py_compile` -> pass
- `git diff --check` -> pass

Measured gate behavior:

- Arith source novelty packet now passes:
  `source_location=src/point_add/arith.rs:1322`,
  `decision=admit-one-bounded-source-proof-no-compute`.
- Restart hold packet now reports missing budget and stop condition in addition
  to owner/range gaps.
- Stale candidate packet fails with `stale_source_base`.

Result: process-control improvement only. No candidate, no official clean run,
no alert, and no submit authority.
