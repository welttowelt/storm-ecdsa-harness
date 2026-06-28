---
name: pod-wrapper-dup-gate
description: "Storm repo-local skill for detecting duplicate gpu_forever or ev.sh wrappers in redacted ECDSA.fail pod snapshots before keeping paid compute guarded."
license: MIT
---

# Pod Wrapper Duplicate Gate

This is a Codex-discoverable bridge to the Storm prompt card at
../../../skills/pod-wrapper-dup-gate.md.

Before maintaining a paid ECDSA.fail pod after a process audit, read that card
and run scripts/storm-pod-wrapper-dup-gate.py on the redacted snapshot.

This bridge is local-only. It does not load private endpoints, credentials,
raw nonces from live pods, telemetry, or always-on behavior.
