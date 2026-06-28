---
name: gidney-ccz-residual-gate
description: Codex-discoverable bridge for the Storm Gidney erase-CCZ residual gate.
---

# Gidney CCZ Residual Gate

Codex-discoverable bridge to the repo-local skill:

    skills/gidney-ccz-residual-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-gidney-ccz-residual-gate.py \
      --gidney-rs <ecdsafail source>/src/point_add/trailmix_ludicrous/gidney.rs \
      --point-add-mod-rs <ecdsafail source>/src/point_add/mod.rs \
      --packet <redacted-ccz-residual-packet.txt> \
      --require-pass

A pass only makes a packet eligible for Storm compute-unlock review. It does not
authorize pods, residuals, alerts, or submit.
