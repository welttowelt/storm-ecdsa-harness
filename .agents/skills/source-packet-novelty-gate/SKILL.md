---
name: source-packet-novelty-gate
description: Codex-discoverable bridge for the Storm source packet novelty gate.
---

# Source Packet Novelty Gate

Codex-discoverable bridge to the repo-local skill:

    skills/source-packet-novelty-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-source-packet-novelty-gate.py <redacted-packet-or-summary>

Require a machine-readable packet with route_id, owner, next, frontier_score,
q-tier, source hash, source location, explicit outside closed ledger novelty
evidence, a bounded source-proof next step, and no_submit_ack=yes.
