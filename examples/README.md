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
