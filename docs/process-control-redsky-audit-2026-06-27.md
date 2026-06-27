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
- `gcd.rs:784`
- `gcd.rs:812`
- `arith.rs:1865`
- `arith.rs:1880`
- `arith.rs:1375`
- `gcd.rs:800`

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
- Machine-readable fixture: `examples/cycle48-audit-impact.example.json`
- Snapshot emitter: `scripts/storm-audit-impact.py`

Measured output:

| State | Support UNKNOWN | Support COUNTEREXAMPLE | Ranked UNKNOWN | Ranked COUNTEREXAMPLE | NACK ledger rows | Ranked UNKNOWN weight | Ranked COUNTEREXAMPLE weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original cycle48 artifact | 25 | 32 | 23 | 31 | 31 | 709580 | 124882 |
| Before passes 6-10 | 14 | 43 | 12 | 42 | 42 | 17818 | 816644 |
| After passes 6-10 | 8 | 49 | 6 | 48 | 48 | 2056 | 832406 |
| After pass 11 | 6 | 51 | 4 | 50 | 50 | 1032 | 833430 |
| After pass 12 | 4 | 53 | 2 | 52 | 52 | 42 | 834420 |
| After pass 13 | 3 | 54 | 1 | 53 | 53 | 2 | 834460 |
| After pass 14 | 2 | 55 | 0 | 54 | 54 | 0 | 834462 |

Result:

- Ranked UNKNOWN rows fell from `23` to `0`, a `100%` reduction.
- Ranked UNKNOWN weight fell from `709580` to `0`, a `100%` reduction.
- Durable NACK ledger rows rose from `31` to `54`.
- Certified rows stayed at `0`, so the audit improved proof routing but did not
  create a submission candidate.

## Pass 11 - GCD Mod-Double Shift Alias Sync

Problem:
After the cycle48 audit-impact sync, the next public top UNKNOWN rows were
`gcd.rs:784` and `gcd.rs:812`.

Evidence:
Both rows are source-site aggregates produced by the `#[track_caller]` CSWAP
expansion in the controlled modular double pair. They map to the forward
`controlled_mod_double` and reverse `controlled_mod_double_reverse` shift over
the `a ++ ovf` view.

Effect:
With `ctrl=1` and adjacent shift-view bits unequal, the CSWAP changes register
order. Omitting the forward row leaves the value unshifted; omitting the reverse
row leaves the inverse schedule unrestored.

Fix:
Added explicit NACK-only source aliases for `gcd.rs:784` and `gcd.rs:812`, then
advanced the fixture to leave `arith.rs:1865` as the next visible UNKNOWN.

Gate:
No source hook, count claim, residual/eval, pod dispatch, alert, WINNER, or
submit follows from these rows. The next worker must prove or falsify
`arith.rs:1865` before touching compute.

## Pass 12 - Vented Plain Carry Alias Sync

Problem:
After pass 11, the next public fixture UNKNOWN was `arith.rs:1865`, with
`arith.rs:1880` still open in the full cycle48 ranked backlog.

Evidence:
Both rows sit in `add_cout_vented_skip_dead`. Row `1865` is the non-vented
carry creation branch when `dead(i)=false` and vent budget is exhausted. Row
`1880` is the mirrored reverse CCX needed after the sum bit is written.

Effect:
With `a[i]=1` and `b[i]=1`, row `1865` toggles `b[i+1]` and feeds the following
sum path. Row `1880` is the restoration mirror; skipping it leaves the carry
lane dirty.

Fix:
Added explicit NACK-only source aliases for `arith.rs:1865` and `arith.rs:1880`,
then advanced the fixture to leave `arith.rs:1375` as the next visible UNKNOWN.

Gate:
No source hook, count claim, residual/eval, pod dispatch, alert, WINNER, or
submit follows from these rows. The next worker must prove or falsify
`arith.rs:1375` before touching compute.

## Pass 13 - FFG Cy0 Restore Alias Sync

Problem:
After pass 12, the next public fixture UNKNOWN was `arith.rs:1375`.

Evidence:
Row `1375` is the optional `cy0` reclaim/restore CCX in the `+f` path. After
`cy0` is reclaimed from the zero-loan, the code flips `a[0]`, restores
`cy0 = ctrl & !final_a0`, then flips `a[0]` back before prefix reverse.

Effect:
With `ctrl=1` and `final_a0=0`, the restore CCX must fire. Skipping it leaves
the prefix carry unavailable for reverse cleanup.

Fix:
Added an explicit NACK-only source alias for `arith.rs:1375`, then advanced the
fixture to leave `gcd.rs:800` as the next visible UNKNOWN.

Gate:
No source hook, count claim, residual/eval, pod dispatch, alert, WINNER, or
submit follows from this row. The next worker must prove or falsify `gcd.rs:800`
before touching compute.

## Pass 14 - GCD Reverse Overflow Alias Sync

Problem:
After pass 13, `gcd.rs:800` was the only ranked UNKNOWN packet left.

Evidence:
Trace-attributed row `800` maps to the inverse overflow rebuild in
`controlled_mod_double_reverse`: `ovf = ctrl & a[0]`. The following subtract-`f`
fold is gated on `ovf`, then the inverse shift returns the `a ++ ovf` view to
zero overflow.

Effect:
With `ctrl=1` and `a[0]=1`, the rebuild CCX must fire. Skipping it loses the
inverse subtract-`f` control and breaks inverse controlled modular doubling.

Fix:
Added an explicit NACK-only source alias for `gcd.rs:800`. The full cycle48
ranked proof backlog now has zero UNKNOWN packets and zero CERTIFIED packets.

Gate:
The cycle48 wall-owner proof queue is exhausted as reusable NACK evidence. It
does not authorize source hooks, count claims, residual/eval, pod dispatch,
alerts, WINNER, or submit. The next route must be a new wall-wide
source-hash-bound certificate or a separate structural discovery pass.

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
