---
name: construction-intake-gate
description: Codex-discoverable bridge for Storm source-bound construction intake packets.
---

# Construction Intake Gate

Codex-discoverable bridge to the repo-local skill:

    skills/construction-intake-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-construction-intake-gate.py \
      <redacted-construction-packet.txt> \
      --require-pass

A pass only admits a source-bound construction intake for review. It does not
authorize pods, residuals, alerts, or submit.
