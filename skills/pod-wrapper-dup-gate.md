# Pod Wrapper Duplicate Gate

Use this before a pod guard keeps a paid GPU or CPU eval lane running after a
process audit. It catches the live failure class where multiple gpu_forever or
ev.sh wrappers cover the same route or nonce.

## Gate

Run a redacted process snapshot, mailbox packet, or pod status tail through:

    python3 scripts/storm-pod-wrapper-dup-gate.py pod-snapshot.txt --require-pass

The snapshot should include:

- pod or instance identity,
- active GPU wrapper line and route/range,
- active eval wrapper line and nonce when eval is running,
- queued marker, lock, or isolated workspace evidence for eval work,
- no_submit_ack=yes in the surrounding owner packet.

## Discipline

- Duplicate GPU wrappers for the same route fail the gate. Collapse to one
  route controller before keeping the pod guarded.
- Duplicate eval wrappers for the same nonce fail the gate. Use an eval-N.queued
  marker plus a lock or isolated workspace.
- Missing route/nonce or missing queue/lock evidence is a hold, not a clean
  pass. Treat results as triage-only until the wrapper state is clear.
- This gate does not certify candidate correctness. Run survivor, isolation,
  official full validation, frontier, and submit gates separately.

## Output

    pod_wrapper_dup_gate=<pass|hold|fail> gpu_wrapper_keys=... eval_wrapper_keys=... queued_marker=... lock=... decision=...
