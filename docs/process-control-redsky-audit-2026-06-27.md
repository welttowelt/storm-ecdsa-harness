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
- `gcd.rs:1510`
- `gcd.rs:1558`
- `fused.rs:1943`
- `fused.rs:2008`
- `arith.rs:1322`
- `arith.rs:1090`
- `gidney.rs:1253`
- `arith.rs:1860`
- `gidney.rs:1357`
- `gidney.rs:1416`
- `arith.rs:524`
- `arith.rs:537`

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

## Passes 6-10 - Cycle48 Source Alias Sweep

Problem:
After the first sync, full cycle48 still had source-site rows with `context=none`
that duplicated trace-context families already covered by the miner.

Evidence:
The current rerun on `wall-owner-site-audit.tsv` reported `certified=0`,
`unknown=14`, `counterexample=43` at support-check. The top five remaining
ranked UNKNOWN rows were `gidney.rs:1253`, `arith.rs:1860`, `gidney.rs:1357`,
`arith.rs:524`, and `arith.rs:537`.

Effect:
Leaving those aliases open keeps the fleet on known-live carry and phase rows
instead of moving to the next proof family.

Fix:
Added explicit source aliases for the Gidney boundary carry, bounded-add carry
span, Gidney HMR erase CCZ and capped erase CCZ, and Cuccaro forward/reverse
carry rows. These are all NACK-only counterexamples; none supply a value-exact
skip.

Gate:
Rerun the cycle48 fixture and full cycle48 miner pipeline. Keep pod dispatch,
alerts, WINNER, and submit closed unless a later packet becomes `CERTIFIED` and
then passes trusted validation.

## Measurement - Process Impact

Evidence source:

- Original cycle48 artifact:
  `state/autonomous-research/structural-alpha-20260627/artifacts/cycle48-wall-owner-certificate-backlog/ranked.jsonl`
- Current rerun command: the full cycle48 classifier pipeline in the
  verification section below, using the same `wall-owner-site-audit.tsv`.

Measured output:

| State | Support UNKNOWN | Support COUNTEREXAMPLE | Ranked UNKNOWN | Ranked COUNTEREXAMPLE | NACK ledger rows | Ranked UNKNOWN weight | Ranked COUNTEREXAMPLE weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original cycle48 artifact | 25 | 32 | 23 | 31 | 31 | 709580 | 124882 |
| Before passes 6-10 | 14 | 43 | 12 | 42 | 42 | 17818 | 816644 |
| After passes 6-10 | 8 | 49 | 6 | 48 | 48 | 2056 | 832406 |

Result:

- Ranked UNKNOWN rows fell from `23` to `6`, a `73.9%` reduction.
- Ranked UNKNOWN weight fell from `709580` to `2056`, a `99.7%` reduction.
- Durable NACK ledger rows rose from `31` to `48`.
- Certified rows stayed at `0`, so the audit improved proof routing but did not
  create a submission candidate.

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

Full cycle48 measurement rerun:

```bash
src=../state/autonomous-research/structural-alpha-20260627/artifacts/cycle48-wall-owner-certificate-backlog/wall-owner-site-audit.tsv
tmp=/tmp/storm-cycle48-after-audit
rm -rf "$tmp"
mkdir -p "$tmp"
python3 scripts/storm-exact-miner.py trace-facts --input "$src" --frontier 1571592960/d44cad3 --source-base d44cad3 --stream-hash cycle48-wall-owner-context-f30d8365 --out "$tmp/facts.jsonl"
python3 scripts/storm-exact-miner.py support-check --facts "$tmp/facts.jsonl" --out "$tmp/supported.jsonl"
python3 scripts/storm-exact-miner.py mine --facts "$tmp/supported.jsonl" --include-unknown-sites --max-unknown-sites 80 --out "$tmp/candidates.jsonl"
python3 scripts/storm-exact-miner.py prove --candidates "$tmp/candidates.jsonl" --out "$tmp/proofs.jsonl"
python3 scripts/storm-exact-miner.py falsify --packets "$tmp/proofs.jsonl" --out "$tmp/falsified.jsonl"
python3 scripts/storm-exact-miner.py ledger --packets "$tmp/falsified.jsonl" --out "$tmp/nack-ledger.jsonl"
python3 scripts/storm-exact-miner.py rank --proofs "$tmp/falsified.jsonl" --out "$tmp/ranked.jsonl"
```
