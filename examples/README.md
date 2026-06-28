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
  subdirectory and reject non-scored `CX/CZ/X/SWAP` rows as q1152 avg-Toffoli
  routes,
- source-row routing fixtures separate packet-ready rows from counterexample
  closures, unsafe compute asks, and non-scored row promotions,
- Gidney CCZ residual fixtures separate non-default residual packets from
  default-on remainder rows and missing-proof holds,
- qoffset host-accounting fixtures separate certified source-integrated packets,
  counterexample closures, incomplete packets, and proof-unknown NACKs,
- emit-bundle fixtures separate certified shared-invariant bundles from
  counterexample closures, incomplete packets, and unsafe single-row claims,
- construction-intake fixtures separate source-bound paper construction packets
  from incomplete handoffs and paper-only compute asks,
- anvil-mass-ledger fixtures separate complete conditional-Toffoli economics
  and raw mass ledgers from incomplete rows and stale/score-inconsistent
  promotions,
- anvil-namespace fixtures separate source-bound high-mass rows from unresolved
  namespace ambiguity and unsafe compute asks,
- anvil-exact-redundancy fixtures separate exact-support proof packets from
  incomplete proof flags and stale/compute overclaims,
- pebbling-theorem fixtures separate certified recompute/pebbling DAG packets
  from incomplete handoffs and stale/dirty compute asks,
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
