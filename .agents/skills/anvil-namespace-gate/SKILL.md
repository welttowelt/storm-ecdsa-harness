---
name: anvil-namespace-gate
description: Codex-discoverable bridge for Storm Anvil op-index namespace/source-binding packets.
---

# Anvil Namespace Gate

Codex-discoverable bridge to the repo-local skill:

    skills/anvil-namespace-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-anvil-namespace-gate.py \
      <redacted-anvil-namespace-packet.txt> \
      --require-pass

A pass only admits a high-mass Anvil row as source-bound for proof review, or
closes it by counterexample. It does not authorize pods, residuals, alerts, or
submit.
