# Redsky Process-Control Audit - 2026-06-27

Scope: improve the Storm process around proof routing and pod dispatch. This is
public harness work only. It does not change challenge circuit code, validation
logic, cloud credentials, alert delivery, or submit behavior.

## Pass 1 - Evidence Boundary

Problem:
Mailbox text is readable by humans but hard to audit mechanically. A row can
sound decisive while still being `Prefilter` or `Partial`.

Evidence:
Recent wall-owner cycles used strict language manually: frontier lock, evidence
label, proof status, artifact path, and `no_submit_ack=yes`.

Effect:
Workers can reopen stale claims or promote a weak result in chat.

Fix:
Added `scripts/storm-claim-ledger.py`, a JSONL claim ledger that prints the
matching mailbox ACK/NACK line and validates evidence labels, proof status, TTL,
and `no_submit_ack=yes`.

Gate:
Score-relevant claims should appear in the ledger and mailbox; anything below
`Local full run` remains non-submit evidence.

## Pass 2 - Proof Backlog Ownership

Problem:
`UNKNOWN` proof rows can drift between agents without a single owner or expiry.

Evidence:
Cycle48 produced a ranked backlog where `comparator.rs:864`, `gcd.rs:745`, and
`gcd.rs:730` needed one-row source proof, not pods.

Effect:
Agents duplicate manual proof work and idle pods stay open waiting for a route.

Fix:
Added `scripts/storm-proof-backlog.py` to import exact-miner ranked packets,
claim one row with a TTL, and resolve it as `NACK`, `CERTIFIED`, `PARKED`, or
`STALE`.

Gate:
One proof owner per row. A row must be resolved before it can unlock count,
residual, validation, or compute.

## Pass 3 - Pod Admission

Problem:
Cheap pods make it tempting to run count or search work before a proof packet
exists.

Evidence:
The current CPU fleet had reachable idle pods while the queue lacked a
certificate-backed job.

Effect:
Spending compute without a source proof mostly creates more `Partial` rows.

Fix:
Added `scripts/pod-admission-gate.py`. It allows only `canary`,
`certified_count`, and `trusted_eval` job classes. Certified count work requires
`proof_status=CERTIFIED`; trusted eval also requires a count edge and clean
candidate flag.

Gate:
No pod dispatch from `UNKNOWN`, `COUNTEREXAMPLE`, stale frontier, missing owner,
missing validator, or missing stop condition.

## Pass 4 - Miner Regression

Problem:
Once a generic-live source row is manually falsified, the miner should not keep
emitting it as `UNKNOWN`.

Evidence:
Cycle49 manually closed `comparator.rs:864`; source inspection also closed
cycle48 aggregate rows `gcd.rs:745` and `gcd.rs:730` as live shift/cswap rows.

Effect:
Without classifier aliases, future wall-owner reports spend proof bandwidth on
already closed live rows.

Fix:
Updated `scripts/storm-exact-miner.py` with classifier aliases for:

- `comparator.rs:864`
- `gcd.rs:745`
- `gcd.rs:730`
- `gcd.rs:935`
- `gcd.rs:1296`

Added `examples/cycle48-wall-owner-sites.example.tsv` as a regression fixture.

Gate:
Classifier rows become source counterexamples only. They do not certify a
skip, open count work, or authorize pods.

## Pass 5 - Control Packet

Problem:
The control loop combines frontier, sentinels, proof backlog, pod queue, and
alert status, but the compact status packet was assembled manually.

Evidence:
Current live loops require the same checks every cycle: frontier lock, hard
sentinels, queue state, proof backlog, and alert/submit closure.

Effect:
Manual status summaries can omit the one field that blocks action.

Fix:
Added `scripts/storm-state-packet.py`, which prints a short public-safe state
packet from a frontier string, optional claim ledger, optional proof backlog,
queue status, and sentinel paths.

Gate:
The script prints `alert_decision=ready_candidate` only when explicitly supplied
with both `--local-full-run-clean` and `--score-below-frontier`; default output
keeps alert and submit closed.

## Verification Commands

```bash
python3 -m py_compile scripts/storm-exact-miner.py scripts/storm-claim-ledger.py scripts/storm-proof-backlog.py scripts/pod-admission-gate.py scripts/storm-state-packet.py
scripts/redaction-check.sh
scripts/check-public-harness.sh
```

Cycle48 classifier regression:

```bash
tmp=/tmp/storm-cycle48-fixture
rm -rf "$tmp"
mkdir -p "$tmp"
python3 scripts/storm-exact-miner.py trace-facts --input examples/cycle48-wall-owner-sites.example.tsv --frontier 1571592960/d44cad3 --source-base d44cad3 --stream-hash cycle48-fixture --out "$tmp/facts.jsonl"
python3 scripts/storm-exact-miner.py support-check --facts "$tmp/facts.jsonl" --out "$tmp/supported.jsonl"
python3 scripts/storm-exact-miner.py mine --facts "$tmp/supported.jsonl" --include-unknown-sites --out "$tmp/candidates.jsonl"
python3 scripts/storm-exact-miner.py prove --candidates "$tmp/candidates.jsonl" --out "$tmp/proofs.jsonl"
python3 scripts/storm-exact-miner.py falsify --packets "$tmp/proofs.jsonl" --out "$tmp/falsified.jsonl"
```
