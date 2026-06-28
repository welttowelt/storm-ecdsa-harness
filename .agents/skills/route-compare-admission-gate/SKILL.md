---
name: route-compare-admission-gate
description: Codex-discoverable bridge for the Storm route-compare admission gate.
---

# Route Compare Admission Gate

Codex-discoverable bridge to the repo-local skill:

    skills/route-compare-admission-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-route-compare-admission.py \
      --route-compare <route-compare-summary.out> \
      --frontier-score 1571592960 \
      --require-admission

Require clean baseline, clean candidate, clean compare summary, and a strict
score edge before residual, compute, pod, handoff, submit, or alert language.
The gate also requires present/parseable numeric fields, matching shot counts,
at least 9024 shots by default, and benchmark-style rounded average-Toffoli
score arithmetic.
