# Compute Restart Gate

Use this before a worker restarts GPU/CPU scanner work after the fleet has
closed compute or when the pod queue has no eligible job.

## Command

    python3 scripts/storm-compute-restart-gate.py <redacted-packet-or-pod-snapshot> --require-pass

## Pass Requirements

- scanner packet has owner, validation owner, pod identity, route/range, next
  action, budget, stop condition, source base, frontier score, q-tier, expected
  negative edge, and no_submit_ack=yes;
- compute gate is explicitly open through a Storm route ACK or route_ack=yes;
- evidence is source-hash-bound CERTIFIED support/proof or a trusted full-clean
  validation packet;
- packet avoids submit, winner, Akash, or mobile-alert language.

## Decisions

- pass: scanner restart gate cleared; still no submit authority.
- hold: owner/route/pod/next metadata is incomplete.
- fail: scanner restart under closed compute, stale/manual scanner route, no
  route ACK plus certified evidence, overclaimed validation label, or premature
  alert/submit wording.

Official eval/build packets without scanner restart language can pass this gate
as `no-scanner-restart`, but they still need validation-submit and eval
isolation gates before any candidate claim.
