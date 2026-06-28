---
name: pod-inventory-ack-gate
description: Codex-discoverable bridge for the Storm pod inventory ACK gate.
---

# Pod Inventory ACK Gate

Codex-discoverable bridge to the repo-local skill:

    skills/pod-inventory-ack-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-pod-inventory-ack-gate.py \
      <redacted-pod-inventory-ack.txt> \
      --require-pass

Require provider, pod id, owner, status, job, stop condition, no-start/no-compute
ACK, and no-submit discipline before a pod inventory ACK is accepted. Fail
ownerless running pods and compute-start language.
