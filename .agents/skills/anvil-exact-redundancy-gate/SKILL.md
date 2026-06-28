---
name: anvil-exact-redundancy-gate
description: Codex-discoverable bridge for Storm Anvil single-op exact-redundancy proof packets.
---

# Anvil Exact Redundancy Gate

Codex-discoverable bridge to the repo-local skill:

    skills/anvil-exact-redundancy-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-anvil-exact-redundancy-gate.py \
      <redacted-anvil-exact-redundancy-packet.txt> \
      --require-pass

A pass only admits a certified single-op exact-redundancy proof or closure for
Storm review. It does not authorize pods, residuals, alerts, or submit.
