# Local Heavy Compute Gate

Use this after a HOT STOP or before keeping any ECDSA.fail process running on a
developer laptop. It blocks Mac-local heavy compute and recurring wrappers from
process snapshots or mailbox packets.

## Gate

Run a redacted process snapshot through:

    python3 scripts/storm-local-heavy-compute-gate.py process-snapshot.txt --require-pass

If the snapshot is known to be from the local Mac and does not include host
metadata, use:

    python3 scripts/storm-local-heavy-compute-gate.py process-snapshot.txt --assume-local --require-pass

## Discipline

- Mac-local build_circuit, eval_circuit, fanout_nonce_eval, route_compare,
  search_driver, storm-exact-miner, lower-q/proof/scanner loops,
  ccx_site_histogram, target/release programs, cargo release builds,
  validation wrappers, or local fleet loops fail the gate.
- Mac-local recurring SSH/watch wrappers fail the gate even when they are only
  watching remote work.
- Unknown-host heavy commands hold until the worker records host, owner, route,
  and pid/log evidence.
- Remote-owned studio, RunPod, or Vast work can pass this gate, but still needs
  owner, wrapper, survivor, eval-isolation, full-validation, and submit gates.
- Lightweight harness checks on this Mac are allowed.
- This gate never kills processes and never authorizes submit.

## Output

    local_heavy_compute_gate=<pass|hold|fail> heavy_lines=... local_heavy=... remote_heavy=... unknown_heavy=... local_recurring=... decision=...
