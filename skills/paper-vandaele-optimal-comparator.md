# Skill: Paper - Vandaele Optimal Comparator

Use when a lower-Q route is blocked by comparator or incrementer carry pressure
and needs a source-backed way to distinguish "replace the comparator" from
"the comparator is only one half of the peak."

## Source

- Vivien Vandaele, "Asymptotically Optimal Quantum Circuits for Comparators
  and Incrementers", arXiv:2603.12917.

## Why We Keep It

The paper gives Clifford+Toffoli comparator and incrementer constructions with
linear gate count, logarithmic depth, and minimal qubit use. The most useful
local hook is the classical-quantum comparator using one dirty ancilla, because
ecdsa.fail lower-Q traces repeatedly hit comparator carry ladders while erasing
overflow or phase flags.

This is not a blanket adder replacement. It is a comparator-pressure diagnostic
and one-callsite port discipline.

## Apply To

- `compare_geq_const_cin_middle` or other const-comparator carry ladders;
- truncated overflow cleanup comparators;
- incrementer sections whose carry ladder is the only peak allocation source;
- routes where a dirty host is available and can be proven restored.

## Required Invariant

The replacement must preserve the same predicate, middle-callback value, phase
deposit, carry-in convention, and dirty-host restoration for every reachable
input. If the existing comparator is inside an HMR/phase-recovery callback, the
phase callback contract is part of the invariant, not an implementation detail.

## Procedure

1. Run a near-peak allocation trace and classify whether the comparator is the
   sole peak source or only co-peaking with an adder carry floor.
2. If a const-add chunk and comparator ladder peak together, require a paired
   cut or an entry-active reduction. If other callsites remain at the same q
   after excluding that pair, widen the proof to the whole plateau before
   porting code.
   If `scripts/vandaele-comparator-ledger.sh` reports
   `max_without_comparator == peak_qubits`, a comparator-only port is blocked:
   the paper hook is real, but it cannot lower the current wall by itself.
3. Build a reduced-width toy that exposes the same carry-in, const bits, dirty
   host, and middle callback.
4. Count the one-callsite port before widening.
5. Run residual and benchmark gates before any compute or submit claim.

## Software Gate

Use `scripts/vandaele-comparator-ledger.sh` to normalize a trace:

```bash
scripts/vandaele-comparator-ledger.sh \
  --trace /tmp/codex_alloc_near_1145.err \
  --frontier 1577850522 \
  --q 1147 \
  --route q1147-clean
```

## Output

```text
Vandaele comparator gate:
- Route:
- Frontier/q/max avgT:
- Peak evidence:
- Comparator peak hits:
- Co-peak add/carry hits:
- Dirty host:
- Middle callback preserved:
- Toy/count/residual:
- Decision: toy-port / paired-cut-required / plateau-cut-required / park
```

## Kill Gate

Park the route if the comparator is not the sole peak source and no paired or
plateau-wide cut is specified. Also park on any phase-only residual: a
comparator that preserves the classical predicate but changes the HMR phase
callback is not clean.
