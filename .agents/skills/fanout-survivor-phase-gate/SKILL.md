---
name: fanout-survivor-phase-gate
description: "Storm repo-local skill for gating q1152 fanout GPU survivors against phase-aware official eval evidence."
license: MIT
---

# Fanout Survivor Phase Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/fanout-survivor-phase-gate.md.

Before promoting any fanout GPU survivor, read that card and run
scripts/storm-fanout-survivor-phase-gate.py on the mixed GPU and official eval
logs.

This bridge is local-only. It does not load private logs, endpoints, raw
nonces, telemetry, or always-on behavior.
