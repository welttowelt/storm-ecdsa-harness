---
name: fanout-burst-triage-gate
description: "Storm repo-local skill for parsing FANOUT_NONCE_LIST burst triage logs and routing possible 0/0/0 rows to full validation without promoting prefilter hits."
license: MIT
---

# Fanout Burst Triage Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/fanout-burst-triage-gate.md.

Before treating a FANOUT_NONCE_LIST burst as exhausted or candidate-bearing,
read that card and run scripts/storm-fanout-burst-triage-gate.py on the log.

This bridge is local-only. It does not load private endpoints, credentials,
live candidate diffs, telemetry, or always-on behavior.
