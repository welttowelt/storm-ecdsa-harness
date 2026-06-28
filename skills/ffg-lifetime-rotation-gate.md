# FFG Lifetime Rotation Gate

Use this before treating an FFG lifetime or `cy0_park` one-call rotation report
as residual, compute, pod, handoff, submit, or alert evidence.

## Command

    python3 scripts/storm-ffg-lifetime-rotation-gate.py \
      <redacted-ffg-lifetime-report.md> \
      --baseline-ops 10228095 \
      --baseline-ccx 1475525 \
      --baseline-ccz 6657 \
      --require-pass

Defaults assume source d44cad3, frontier score 1571592960, and 9024 route
compare shots. Override only after a fresh frontier lock.

## Pass Requirements

- route id, owner, next action, source base, source hash, candidate hash, and
  no_submit_ack=yes are present under no-submit discipline;
- the packet uses the current expected source base;
- FFG lifetime or `TLM_FFG` context is present;
- probe kind, call number, and candidate env are present;
- split-qcin and cy0-park toy checks are PASS;
- carry-floor decision is not the known `carry-floor-local-support-no-constant-wire` closure;
- BASE, CAND, and COMPARE summaries are present;
- baseline, candidate, and compare are all clean;
- route-compare shots meet the minimum;
- the rounded candidate score beats the supplied frontier score;
- optional baseline op/CCX/CCZ checks do not regress;
- evidence label is Prefilter or Partial, not Local full run or Promoted;
- no compute, submit, alert, WINNER, or Akash language appears.

## Decisions

- pass: `ffg-lifetime-rotation-review-no-compute`.
- hold: complete missing packet fields before handoff.
- fail: do not promote the FFG call rotation.

This gate keeps repeated one-call FFG toys from consuming residual, compute, or
submission attention unless they produce both correctness and score evidence.
