---
name: apply-overlap-ledger
description: "Storm repo-local skill for gating apply/codec/fold overlap claims before lower-Q ecdsa.fail solver edits."
license: MIT
---

# Apply Overlap Ledger

This is a Codex-discoverable bridge to the Storm prompt card at
`../../../skills/apply-overlap-ledger.md`.

Before treating pending-symbol or last-window streaming across
`tlm_apply_inverse_mod_sub_fold` as a lower-Q route, read that card and run the
apply overlap ledger against a public trace.

This bridge is local-only. It does not load private chat logs, private
endpoints, raw logs, nonces, telemetry, or always-on behavior.
