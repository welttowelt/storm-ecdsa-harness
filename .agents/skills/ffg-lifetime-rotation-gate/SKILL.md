---
name: ffg-lifetime-rotation-gate
description: Codex-discoverable bridge for the Storm FFG lifetime rotation gate.
---

# FFG Lifetime Rotation Gate

Codex-discoverable bridge to the repo-local skill:

    skills/ffg-lifetime-rotation-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-ffg-lifetime-rotation-gate.py \
      <redacted-ffg-lifetime-report.md> \
      --baseline-ops 10228095 \
      --baseline-ccx 1475525 \
      --baseline-ccz 6657 \
      --require-pass

Require clean BASE/CAND/COMPARE summaries, sufficient shots, positive frontier
score edge, source/candidate hashes, FFG lifetime context, toy PASS evidence,
and no-submit discipline before any residual, compute, pod, handoff, submit, or
alert language.
