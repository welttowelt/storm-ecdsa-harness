# Bluesky/Redsky Source Packet Novelty Gate - 2026-06-28

## Frontier Context

Latest mailbox state closed the current q1152 source-line UNKNOWN backlog:
current_unknown_scored=21, closed_by_existing_jsonl=21, and NEXT_UNCLOSED
empty. The useful route is no longer "scan the same source-line rows harder."
The useful route is to admit only a genuinely new packet outside the closed
counterexample ledger, or a remote official 0/0/0 score-below-frontier candidate
from an owned route.

## Loop 1

Bluesky audit:
- Route or idea: Treat closed counterexample ledgers as an admission-control
  layer for new source packets.
- Best case: Workers stop reopening q1152 rows that the ledger already killed.
- Missing measurement: Whether a packet is source-bound and outside the closed
  ledger.
- Smallest useful experiment: Parse a redacted packet and fail ledger hits,
  NEXT_UNCLOSED empty, or all-unknowns-closed summaries unless novelty is
  explicit.
- Bounded alternative: Keep the packet but send it to proof backlog only.
- Hidden assumption: The closed ledger keys are specific enough to avoid
  over-closing a future source hash.
- Stop condition: Any packet missing source hash, source location, owner, next,
  or no-submit ACK stays on hold.
- Decision: Implement a public-safe novelty gate.

Redsky audit:
- Problem: Current-source UNKNOWN rows can be described as fresh leads after
  Storm has already closed them.
- Evidence: Mailbox says current_unknown_scored and closed_by_existing_jsonl are
  equal, with NEXT_UNCLOSED empty.
- Effect: Compute and reviewer attention can drift onto already falsified rows.
- Implementation check: Gate must parse summaries only and avoid private logs.
- Smallest useful fix: storm-source-packet-novelty-gate.py.
- Gate: Pass only to one bounded source proof, never to compute or submit.

## Loop 2

Bluesky audit:
- Route or idea: Allow support_status=UNKNOWN only when the packet is new and
  routed to a proof step.
- Best case: UNKNOWN becomes a backlog item, not a compute trigger.
- Missing measurement: outside_closed_ledger=yes or equivalent ledger_hit=no.
- Smallest useful experiment: A pass fixture with UNKNOWN support and explicit
  novelty.
- Bounded alternative: A hold state for missing source hash or novelty status.
- Hidden assumption: Workers will read pass as proof-admission, not validation.
- Stop condition: Decision string includes no-compute.
- Decision: Pass decision is admit-one-bounded-source-proof-no-compute.

Redsky audit:
- Problem: Evidence labels can be over-promoted.
- Evidence: Existing gates block Local full run and Promoted on support packets.
- Effect: A source packet can imply validation it does not possess.
- Implementation check: Evidence label must be Prefilter or Partial.
- Smallest useful fix: Fail full-run/promoted labels.
- Gate: Any full-run/Promoted source packet fails before handoff.

## Loop 3

Bluesky audit:
- Route or idea: Treat NEXT_UNCLOSED empty as a kill signal unless the packet
  names a new outside-ledger source hash.
- Best case: The gate blocks the exact latest fleet weakness.
- Missing measurement: current_unknown_scored and closed_by_existing_jsonl
  counts.
- Smallest useful experiment: Fail a fixture with 21/21 closed and no outside
  ledger override.
- Bounded alternative: If a later source hash changes, require explicit novelty
  rather than inheriting closure.
- Hidden assumption: The summary belongs to the same packet.
- Stop condition: The gate does not fail NEXT_UNCLOSED empty when the packet
  explicitly says it is outside the closed ledger.
- Decision: Implement the equal-count and empty-next checks.

Redsky audit:
- Problem: Closed-ledger summaries can be stale relative to a new source hash.
- Evidence: Frontier source is the current lock; stale bases are common in
  handoffs.
- Effect: A stale packet can look new by omitting the current base.
- Implementation check: Compare source_base to expected source.
- Smallest useful fix: Default expected source d44cad3.
- Gate: Stale source fails; missing source holds.

## Loop 4

Bluesky audit:
- Route or idea: Make the gate reusable by accepting freeform redacted packets,
  not a private schema.
- Best case: Any worker can paste a mailbox packet into the gate.
- Missing measurement: Stable output fields for scanner automation.
- Smallest useful experiment: Text output plus JSON mode.
- Bounded alternative: Keep examples plain text.
- Hidden assumption: Regex parsing is enough for intake.
- Stop condition: Public harness fixtures cover pass, hold, fail, and stale.
- Decision: Add examples and harness tests.

Redsky audit:
- Problem: Public repo must not leak private mailbox paths, endpoints, or raw
  nonce assignments.
- Evidence: Existing redaction gate scans the tree.
- Effect: A good process gate can become unsafe if examples include live paths.
- Implementation check: Fixtures use public-style source paths only.
- Smallest useful fix: Run scripts/redaction-check.sh.
- Gate: No raw SSH commands, private home paths, endpoints, or nonces.

## Loop 5

Bluesky audit:
- Route or idea: Chain novelty gate before source proof and candidate validation
  gates.
- Best case: The fleet has a durable funnel: novel packet -> bounded proof ->
  candidate validation -> Storm submit decision.
- Missing measurement: Which gate owns each transition.
- Smallest useful experiment: Add a skill bridge naming the exact command.
- Bounded alternative: Keep the novelty gate independent; no imports from the
  miner.
- Hidden assumption: Workers can distinguish proof-admission from compute
  admission.
- Stop condition: The docs and output state no compute, alert, or submit.
- Decision: Add skills/source-packet-novelty-gate.md and Codex bridge.

Redsky audit:
- Problem: Without a narrow decision string, a pass can be misrouted.
- Evidence: Prior mailbox language repeatedly needed no-submit/no-sentinel
  corrections.
- Effect: Passing an intake packet could be overread as candidate evidence.
- Implementation check: Decision string is explicit:
  admit-one-bounded-source-proof-no-compute.
- Smallest useful fix: Self-test the decision text.
- Gate: A pass still requires later source-proof and candidate-validation gates;
  no submit authority is granted.

## Result

Implemented:

- scripts/storm-source-packet-novelty-gate.py
- examples/source-packet-novelty-*.example.txt
- skills/source-packet-novelty-gate.md
- .agents/skills/source-packet-novelty-gate/SKILL.md

This is process-control alpha only. It creates no candidate, no official clean
run, no alert, and no submit authority.
