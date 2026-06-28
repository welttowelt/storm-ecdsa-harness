# Fanout Burst Triage Gate

Use this when a worker runs FANOUT_NONCE_LIST to triage many fanout survivor
nonces from one op-stream build.

## Gate

Run the burst log through:

    python3 scripts/storm-fanout-burst-triage-gate.py burst.log

Use --require-no-candidate when the expected control-plane result is a NACK:

    python3 scripts/storm-fanout-burst-triage-gate.py burst.log --require-no-candidate

## Discipline

- fanout_burst_triage_gate=nack means this burst produced no 0/0/0 triage row.
- fanout_burst_triage_gate=candidate means full local official validation is
  required. It is not a submit claim.
- Missing clean summary or count rows is a hold.
- Keep this after qstate and wrapper gates, and before any FOR-AKASH language.

## Output

    fanout_burst_triage_gate=<candidate|nack|hold|fail> burst_nonces=... triage_rows=... clean_summary=... zero_rows=... decision=...
