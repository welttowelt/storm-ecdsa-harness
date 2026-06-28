# Examples

These examples are safe, public-demo packets. They show shape and discipline,
not a live `ecdsa.fail` route.

Use them to teach agents the workflow:

- every directed message requests a read receipt,
- two-worker and file-backed handoffs keep ACKs explicit,
- every route has a falsifier,
- every route can receive a Bluesky and Redsky audit pass,
- every compute request has a validator and kill gate,
- every public note separates evidence from claims,
- apply-overlap fixtures separate certified facts from restore-proof failures,
- wall-owner summaries are regenerated before source-certificate scouting,
- source-certificate scouts filter already-closed context rows before mining,
- source-packet novelty checks accept public `src/point_add` sites beyond one
  subdirectory,
- FFG pair-complete fixtures distinguish no-recompute NACKs from recompute
  proof holds,
- FFG pair-proof fixtures gate full source-bound packets before handoff or
  compute language,
- paper-invariant fixtures block scout-only hits before skill-card or compute
  language,
- pod-inventory ACK fixtures accept complete no-compute inventory, hold
  unreachable provider state, accept verified zero-pod account inventory, and
  fail ownerless running pods or nonzero empty-account spend,
- candidate validation packets fail stale source bases before handoff language,
- scanner output stays `Prefilter` until official validation passes.

The examples intentionally avoid:

- endpoints,
- provider names,
- raw logs,
- raw nonces,
- private paths,
- active diffs,
- unreleased route data.

Run before sharing modified examples:

```bash
scripts/check-public-harness.sh
scripts/redaction-check.sh
scripts/redaction-check.sh --history
```
