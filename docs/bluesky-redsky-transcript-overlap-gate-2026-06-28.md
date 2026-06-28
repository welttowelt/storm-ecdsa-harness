# Bluesky/Redsky Transcript Overlap Gate - 2026-06-28

## Context

The latest q1147 fresh-drop lane split into two bad outcomes: one refinement
kept a paper count edge but failed a bounded correctness probe, while the next
refinement removed observed dirt but lost score edge. Storm's next useful work
was a new source theorem or a transcript peak-overlap inventory with exact
support before implementation.

## Loop 1

Bluesky audit:
- Route or idea: Treat transcript peak-overlap as a gate before any drop patch.
- Best case: Drop packets can advance only when the peak-binding calls and
  overlap rows are source-bound and complete.
- Missing measurement: covered peak calls versus required peak calls.
- Smallest useful experiment: Parse a redacted packet with required_calls and
  covered_calls.
- Bounded alternative: Hold incomplete packets for source-theorem review.
- Hidden assumption: The inventory belongs to the current source hash.
- Stop condition: Stale source or missing source hash blocks the packet.
- Decision: Add transcript-overlap gate.

Redsky audit:
- Problem: Active-only origin maps can produce attractive drop counts without
  source-bound semantics.
- Evidence: The q1147 fresh-drop NACK cited active-only origin limits and stale
  index warnings.
- Effect: Count deltas can be detached from the actual circuit source.
- Implementation check: Fail active-only origin and stale indices.
- Smallest useful fix: Parser fail reasons for active_only_origin_map and
  stale_index_warnings.
- Gate: No implementation from active-only inventory.

## Loop 2

Bluesky audit:
- Route or idea: Let score economics kill clean-but-too-small drops.
- Best case: Refined clean packets that lose score edge stop before residual
  or benchmark work.
- Missing measurement: candidate score or avgT at the target q-tier.
- Smallest useful experiment: Compute score edge from frontier, q, and avgT.
- Bounded alternative: Require explicit score_edge when avgT is missing.
- Hidden assumption: q and avgT belong to the same candidate stream.
- Stop condition: score_edge <= 0 fails.
- Decision: Add score-edge computation.

Redsky audit:
- Problem: A clean-looking refinement can still be below break-even.
- Evidence: The refine2 packet removed observed dirt but lost the q1147 avgT
  edge.
- Effect: Further validation would spend work on a non-winning route.
- Implementation check: score_no_edge is a hard failure.
- Smallest useful fix: Fail non-positive edge.
- Gate: No residual/9024/benchmark from score-no-edge packets.

## Loop 3

Bluesky audit:
- Route or idea: Distinguish bounded probe dirt from proof incompleteness.
- Best case: Dirty packets fail immediately, unknown support holds.
- Missing measurement: dirty_classical, dirty_phase_shots, dirty_any_fail, c/p/a.
- Smallest useful experiment: Fail a fixture with dirty bounded probe counters.
- Bounded alternative: Hold only when support is unknown and dirt is absent.
- Hidden assumption: Any nonzero bounded dirt is enough to block the route.
- Stop condition: Nonzero dirt counters fail.
- Decision: Add dirty evidence detection.

Redsky audit:
- Problem: Count edge can be over-promoted despite classical/phase failures.
- Evidence: Refine1 had count edge and dirty_classical/phase evidence.
- Effect: Residual or compute can chase a correctness-broken packet.
- Implementation check: dirty_bounded_probe is a hard failure.
- Smallest useful fix: Parse dirty counters and rc=1 text.
- Gate: Dirty bounded probe blocks implementation.

## Loop 4

Bluesky audit:
- Route or idea: The gate should pass only to source-theorem review.
- Best case: A good inventory gets human/theorem review without becoming a
  compute request.
- Missing measurement: exact support is certified.
- Smallest useful experiment: Pass fixture with exact_support=CERTIFIED.
- Bounded alternative: Missing exact support holds.
- Hidden assumption: Certified support is source-bound.
- Stop condition: support counterexample fails.
- Decision: Pass decision is source-theorem-review-no-compute.

Redsky audit:
- Problem: A pass can be misread as submit or compute authorization.
- Evidence: Recent mailbox entries repeatedly needed no-submit and no-pod
  wording.
- Effect: Process-control pass can leak into scanner work.
- Implementation check: Fail compute/residual/benchmark requests and
  submit/Akash/winner language.
- Smallest useful fix: Explicit decision string and regex blockers.
- Gate: No compute or submit authority.

## Loop 5

Bluesky audit:
- Route or idea: Keep the gate public-safe and easy to paste into.
- Best case: Workers can test redacted mailbox packets directly.
- Missing measurement: harness regression coverage.
- Smallest useful experiment: pass/hold/fail/stale fixtures.
- Bounded alternative: JSON output for dashboards.
- Hidden assumption: Regex parsing is enough for intake.
- Stop condition: redaction and public harness checks must pass.
- Decision: Add fixtures, skill, bridge, and docs.

Redsky audit:
- Problem: Public process artifacts can leak private paths or overstate wins.
- Evidence: Existing redaction check caught prior path mistakes.
- Effect: A useful gate can become unsafe to publish.
- Implementation check: Examples use public-style paths and no raw private
  endpoints.
- Smallest useful fix: Run redaction and diff checks.
- Gate: No candidate, no official clean run, no alert, no submit.

## Result

Implemented:

- scripts/storm-transcript-overlap-gate.py
- examples/transcript-overlap-*.example.txt
- skills/transcript-overlap-gate.md
- .agents/skills/transcript-overlap-gate/SKILL.md

This is process-control alpha only. It creates no candidate, no official clean
run, no alert, and no submit authority.
