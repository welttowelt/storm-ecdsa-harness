# Bluesky/Redsky Route Compare Admission - 2026-06-28

## Context

The latest FFG lane produced a diagnostic one-call packet: toy checks passed,
but route-compare and count evidence did not justify residual, scanner, pod, or
handoff work. The existing route-compare helper detected dirty/no-edge outcomes
in its decision field, but its headline always printed
route_compare_admission=pass. That was too easy to misread in mailbox and
script output.

## Loop 1

Bluesky audit:
- Route or idea: Make route-compare output headline match the admission result.
- Best case: Workers can glance at the first field and avoid promoting a dirty
  diagnostic packet.
- Missing measurement: explicit admitted flag.
- Smallest useful experiment: dirty FFG-style fixture with baseline, candidate,
  and compare failures.
- Stop condition: dirty packet must say fail and admitted=0.

Redsky audit:
- Strongest objection: A decision string buried later in the row can be missed.
- Fastest falsifier: old output said pass for dirty candidate data.
- Decision: Add route_compare_admission=fail/hold/pass and admitted=0/1.

## Loop 2

Bluesky audit:
- Route or idea: Require BASE_SUMMARY, not only CAND and COMPARE.
- Best case: Baseline dirt cannot be hidden while candidate dirt is debated.
- Missing measurement: baseline channel cleanliness.
- Smallest useful experiment: baseline classical/phase dirt in the fixture.
- Stop condition: dirty baseline blocks admission.

Redsky audit:
- Strongest objection: If baseline is dirty, compare agreement is not enough.
- Fastest falsifier: baseline_classical or baseline_phase nonzero.
- Decision: Add baseline_clean and dirty-baseline-no-admission.

## Loop 3

Bluesky audit:
- Route or idea: Separate classifier mode from hard shell gating.
- Best case: Dashboards can keep parsing all rows, while launch scripts can
  require a hard pass.
- Missing measurement: exit status under strict mode.
- Smallest useful experiment: --require-admission exits nonzero for dirty,
  missing, and no-edge rows.
- Stop condition: only route-clean-score-edge exits zero with strict mode.

Redsky audit:
- Strongest objection: Existing callers may rely on classifier exit zero.
- Fastest falsifier: default mode still returns a row for every packet.
- Decision: Add --require-admission without breaking classifier mode.

## Loop 4

Bluesky audit:
- Route or idea: Treat clean but non-winning route-compare as fail for admission.
- Best case: Clean q1147 or q1133 diagnostics do not reopen compute when score
  arithmetic cannot beat the frontier.
- Missing measurement: strict score edge against supplied frontier score.
- Smallest useful experiment: clean no-edge fixture.
- Stop condition: score-no-edge fails strict admission.

Redsky audit:
- Strongest objection: Clean is not the same as useful.
- Fastest falsifier: q * avg_tof >= frontier score.
- Decision: No residual/pod/handoff from no-edge route-compare rows.

## Loop 5

Bluesky audit:
- Route or idea: Make the rule discoverable as a fleet skill.
- Best case: Workers use the same gate before residual, compute, pod, handoff,
  submit, or alert language.
- Missing measurement: public harness and skill bridge coverage.
- Smallest useful experiment: route-compare skill card plus harness assertions.
- Stop condition: public harness and redaction checks pass.

Redsky audit:
- Strongest objection: Hidden parser behavior drifts without skill docs.
- Fastest falsifier: missing public harness manifest entry.
- Decision: Add skill card, Codex bridge, and README entries.

## Result

Implemented process-control hardening only:

- scripts/storm-route-compare-admission.py now reports pass/hold/fail and
  admitted=0/1.
- --require-admission exits nonzero unless the packet is clean and has score
  edge.
- Dirty baseline, dirty candidate, dirty compare, missing summaries, and
  score-no-edge rows cannot be mistaken for admitted routes.

No candidate, no official clean run, no pod, no alert, and no submit authority.

## Follow-up 5-loop audit

### Loop 1

Bluesky audit:
- Route or idea: Treat required summary fields as evidence, not optional text.
- Best case: malformed or missing channel counts cannot default to clean.
- Smallest useful experiment: remove candidate classical from a clean packet.

Redsky audit:
- Strongest objection: parser defaults turned missing integers into zero.
- Fastest falsifier: CAND_SUMMARY without classical looked clean.
- Decision: missing or malformed required fields now hold with
  incomplete-summary-no-admission.

### Loop 2

Bluesky audit:
- Route or idea: Require BASE/CAND/COMPARE to describe the same sample depth.
- Best case: mismatched rows cannot be stitched into a fake route-clean packet.
- Smallest useful experiment: compare summaries with different shots.

Redsky audit:
- Strongest objection: compare agreement is meaningless if summaries are from
  different shot sets.
- Fastest falsifier: distinct shot counts in the three rows.
- Decision: shot-mismatch-no-admission blocks admission.

### Loop 3

Bluesky audit:
- Route or idea: Do not admit short clean route-compare probes.
- Best case: 256-shot diagnostics remain useful for routing but cannot unlock
  residual, pod, handoff, submit, or alert language.
- Smallest useful experiment: clean score-edge packet with shots=256.

Redsky audit:
- Strongest objection: partial route-compare is not a 9024 residual.
- Fastest falsifier: clean 256-shot edge.
- Decision: default --min-shots=9024; short rows hold as
  insufficient-shots-no-admission.

### Loop 4

Bluesky audit:
- Route or idea: Match benchmark score arithmetic.
- Best case: raw float edges cannot pass when rounded average Toffoli ties the
  frontier.
- Smallest useful experiment: avg_tof=1364229.999 at q=1152.

Redsky audit:
- Strongest objection: official q1152 score uses rounded Toffoli, so raw score
  can claim a false one-Toffoli edge.
- Fastest falsifier: raw score below frontier but rounded score equal.
- Decision: admission score is qubits * floor(avg_tof + 0.5), and output now
  exposes raw_score plus avg_tof_rounded.

### Loop 5

Bluesky audit:
- Route or idea: Assert the hard shell mode in the public harness.
- Best case: launch scripts can safely use --require-admission.
- Smallest useful experiment: dirty row exits nonzero; admitted row exits zero.

Redsky audit:
- Strongest objection: docs can claim strict mode while shell behavior drifts.
- Fastest falsifier: dirty strict run returns 0.
- Decision: check-public-harness.sh now tests strict fail/pass behavior.
