# Skill: Paper - SQUARE Active Volume

Use when a lower-Q route has several possible reuse, uncompute, or codec-timing
targets and you need to choose the one that actually reduces peak pressure.

## Source

- Yongshan Ding, Xin-Chuan Wu, Adam Holmes, Ash Wiseth, Diana Franklin,
  Margaret Martonosi, and Frederic T. Chong, "SQUARE: Strategic Quantum Ancilla
  Reuse for Modular Quantum Programs via Cost-Effective Uncomputation",
  arXiv:2004.08539.

## Why We Keep It

SQUARE is useful because it makes qubit reuse a costed scheduling problem. The
paper's active-quantum-volume idea is the right pressure metric for ecdsa.fail:
a local one-bit saving is irrelevant if it misses the above-target plateau, and
an uncompute/recompute idea is bad if its hidden scratch appears inside the same
peak rows it claims to fix.

For the current lower-Q campaign, this skill turns "find a qubit" into:

1. rank the rows that actually exceed the target q tier;
2. map each candidate value to those rows;
3. reject candidates that cover only cheap rows or give the bit back as hidden
   scratch inside the same window.

## Apply To

- transcript/tape codec timing changes;
- carry, cout, comparator, or FFG host-lifetime cuts;
- Gidney/conditionally-clean adder ports that trade extra uncompute for lower
  resident scratch;
- q1147/q1144 plateau analysis before a larger code edit or paid compute.

## Required Ledger

Before editing, run an active-volume ledger on the exact trace that defines the
candidate:

```bash
scripts/active-volume-ledger.sh \
  --trace /tmp/trace.err \
  --frontier 1577850522 \
  --q 1147 \
  --target-q 1146 \
  --route q1147-local \
  --candidate codec-or-carry-cut
```

The ledger must report:

- q tier and max average Toffoli for that tier;
- all above-target FFG rows and the worst rows by pressure;
- whether tape/transcript rows overlap the same target;
- a decision to continue only if the candidate covers the high-pressure rows.

## Procedure

1. Refresh `ecdsafail benchmark` and compute q-tier thresholds.
2. Build the route with `TRACE_TLM_FFG=1` and, for transcript routes,
   `TRACE_TLM_TAPE_ALL=1`.
3. Run `scripts/active-volume-ledger.sh`.
4. State the candidate's coverage in terms of the ledger's top pressure rows.
5. Combine with `paper-reqomp-space-constrained-uncompute`:
   hidden scratch inside a high-pressure row subtracts from the cut.
6. Only then edit the circuit and run count/residual/eval/benchmark gates.

## Output

```text
SQUARE active-volume gate:
- Route:
- Frontier/q/max avgT:
- Target q/max avgT:
- Candidate:
- Max FFG peak:
- FFG rows above target:
- Weighted pressure:
- Tape rows above target:
- Top pressure rows:
- Decision: rank-first / candidate-covers-plateau / incomplete-window / park
```

## Kill Gate

Park the route before compute if the candidate does not cover the highest
pressure rows, if it reintroduces equal scratch inside those rows, or if it
only improves total active volume while leaving the target peak unchanged.
