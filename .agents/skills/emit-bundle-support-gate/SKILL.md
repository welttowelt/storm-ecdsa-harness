---
name: emit-bundle-support-gate
description: Codex-discoverable bridge for the Storm combined real-emit bundle support gate.
---

# Emit Bundle Support Gate

Codex-discoverable bridge to the repo-local skill:

    skills/emit-bundle-support-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-emit-bundle-support-gate.py \
      <redacted-emit-bundle-packet.txt> \
      --require-pass

A pass only admits a certified shared-invariant emit bundle or counterexample
closure. It does not authorize pods, residuals, alerts, or submit.
