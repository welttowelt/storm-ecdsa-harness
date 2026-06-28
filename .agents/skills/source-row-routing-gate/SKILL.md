---
name: source-row-routing-gate
description: Codex-discoverable bridge for the Storm q1152 source row routing gate.
---

# Source Row Routing Gate

Codex-discoverable bridge to the repo-local skill:

    skills/source-row-routing-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-source-row-routing-gate.py \
      <redacted-source-row-routing-packet.txt> \
      --require-pass

Accept either one packet-ready q1152 source row for bounded proof, or one
counterexample closure that advances to the next source row. A pass has no
compute, pod, alert, or submit authority.
