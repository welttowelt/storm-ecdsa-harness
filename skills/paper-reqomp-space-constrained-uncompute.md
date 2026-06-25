# Skill: Paper - Reqomp Space-Constrained Uncompute

Use when a lower-Q route proposes to trade resident qubits for extra
uncompute/recompute work under a hard peak-qubit cap.

## Source

- Benoit Valiron, Simon Martiel, and colleagues, "Reqomp: Space-constrained
  Uncomputation for Quantum Circuits", Quantum 8, 1258 (2024).

## Why We Keep It

Reqomp is useful because it treats uncomputation as a constrained synthesis
problem instead of an informal "clean this qubit earlier" idea. For the
ecdsa.fail lower-Q campaign, that is the right discipline: a q1146 or q1152 cut
is live only if the removed resident value can be recomputed or replayed without
creating an equal hidden scratch peak inside the same plateau.

The paper is not a drop-in circuit replacement. Its value is the gate it gives
us: prove the uncompute/replay window and hidden-scratch budget before touching
the full circuit.

## Apply To

- codec or transcript timing rewrites that delay a tape/code bit;
- inverse-fold plateau cuts that recompute a carry, compare bit, or borrowed
  high bit after the peak;
- label-stable allocator experiments where changing physical lanes must not
  change the logical op stream;
- q1152-or-lower paths that need a non-local resident-footprint cut.

## Required Invariant

Every candidate must name the value, the above-target call window it covers,
all consumers, the exact replay path, and the hidden scratch created during
decode/recompute.

Required shape:

```text
candidate=<name>
value=<logical bit/register>
producer=<source callsite or codec window>
covered_calls=<comma-separated FFG call ids>
all_consumers_accounted=<yes/no>
cut_bits=<N>
hidden_scratch_bits=<N>
extra_toffoli_estimate=<N>
replay_window=<before|inside|after plateau, with source labels>
```

## Procedure

1. Refresh the current frontier and q-tier thresholds.
2. Build or reuse a peak trace with `TLM_FFG` rows.
3. Run `scripts/uncompute-window-ledger.sh` for the candidate.
4. If the ledger says `prototype-required`, build a small reversible toy before
   editing the full circuit.
5. Promote only after count, residual probes, trusted eval, and benchmark gates.

Example:

```bash
scripts/uncompute-window-ledger.sh \
  --trace /tmp/codex_alloc_near_1145.err \
  --frontier 1577850522 \
  --q 1147 \
  --target-q 1146 \
  --route q1147-clean \
  --candidate codec-one-bit-before-ffg-plateau \
  --covered-calls 178,180,181,182,183,185,190,192,194 \
  --all-consumers yes \
  --cut-bits 1 \
  --hidden-scratch 0 \
  --extra-toffoli 0
```

## Current Campaign Gate

For the current q1147 clean route, local comparator/carry swaps are exhausted.
The useful Reqomp target is a one-bit resident-footprint cut across all
above-target inverse-mod-sub plateau calls. A codec idea that saves one tape bit
but needs one decompression bit inside those same calls is rejected; it gives
back the whole q1146 cut.

## Output

```text
Reqomp uncompute window gate:
- Route:
- Frontier/q/max avgT:
- Target q/max avgT:
- Candidate:
- Above-target calls:
- Covered calls:
- Missing calls:
- Cut bits:
- Hidden scratch bits:
- Extra Toffoli estimate:
- All consumers accounted:
- Decision: prototype-required / incomplete-window / scratch-erases-cut / park
```

## Kill Gate

Park the route if any above-target call is uncovered, if any consumer is
unaccounted, if hidden scratch inside the peak is greater than or equal to the
cut, or if the extra Toffoli cannot beat the q-tier score gate.
