---
name: anvil-mass-ledger-gate
description: Codex-discoverable bridge for Storm Anvil mass/economics ledgers.
---

# Anvil Mass Ledger Gate

Codex-discoverable bridge to the repo-local skill:

    skills/anvil-mass-ledger-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-anvil-mass-ledger-gate.py \
      <anvil_conditional_toffoli_mass_ledger.tsv> \
      --require-pass

A pass only admits a machine-readable mass/economics ledger for the next packet
gate. It does not authorize pods, residuals, alerts, or submit.
