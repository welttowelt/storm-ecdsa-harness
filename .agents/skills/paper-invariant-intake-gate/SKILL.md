---
name: paper-invariant-intake-gate
description: Codex-discoverable bridge for the Storm paper invariant intake gate.
---

# Paper Invariant Intake Gate

Codex-discoverable bridge to the repo-local skill:

    skills/paper-invariant-intake-gate.md

Use the repo-local instructions and run:

    python3 scripts/storm-paper-invariant-intake-gate.py \
      <redacted-paper-model-pass.txt> \
      --require-pass

Require source and candidate hashes, a local source invariant, score-visible IR
effect, certified support/proof status, negative score edge, and no-submit
discipline before a paper-mining hit can become a skill card or route handoff.
Pass is review-only and does not unlock compute.
