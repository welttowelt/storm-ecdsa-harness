---
name: candidate-validation-packet-gate
description: "Storm repo-local skill for checking official ECDSA.fail validation handoff packets before FOR-AKASH or candidate language."
license: MIT
---

# Candidate Validation Packet Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/candidate-validation-packet-gate.md.

Before calling a survivor a candidate, FOR-AKASH, or submit-gate-ready, read
that card and run scripts/storm-candidate-validation-packet-gate.py on the
redacted packet.

This bridge is local-only. It does not run validation, inspect live processes,
submit, alert, load private endpoints, credentials, telemetry, or always-on
behavior.
