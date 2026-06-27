# Route Packet: Enable `DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM` on q1170

## Identity

- Route ID: tobitvector-cswap-body-trim-q1170
- Source/base: ecdsa.fail public benchmark `gpsanaut/ecdsafail-challenge` @ `7bab51f`
- Current frontier: score 1677861900, qubits 1170, avg Toffoli 1434070
- Expected edge: ~−1,600 emitted CCX (~−0.11 %) while holding 1170 qubits
- Evidence label: Historical clue (untested source idea)

## Correction from prior draft

The prior draft targeted `DIALOG_GCD_SHIFT_BAND_TRIMS`. That env-var is referenced
in memory notes but is **not implemented** in the current `7bab51f` code (no
reader function exists). This route instead targets a wired, currently-off flag
in the same optimization family.

## Claim

- What should improve: average executed Toffoli count of the q1170 circuit.
- Why it might work:
  - `src/point_add/mod.rs:1418` sets `DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=0`.
  - The tobitvector cswap loops run at the full `active_width` while the body
    sub/add beside them already trims to `aw − body_trim`.
  - Memory note `src/point_add/memory/2026-06-07-measured-frontier-leads.md`
    section **C1** estimates clamping the cswap loop bound to the body's own
    `dialog_gcd_body_carry_trunc_width` saves ~1,600 emitted CCX.
  - The code path is already wired in `dialog_gcd_classical_filter.rs`
    (`cswap_width`) and `src/point_add/rounds/dialog/mod.rs`
    (`dialog_gcd_tobitvector_cswap_width`).
- What would make it false:
  - Enabling the trim breaks correctness (9024-shot validation fails).
  - The gain is relocated into the GCD-walk peak and raises qubit count above 1170.
  - The memory note's island-free reasoning is wrong and a fresh
    `DIALOG_TAIL_NONCE` is needed.

## Validation

- Cheap check:
  - Confirm `dialog_gcd_tobitvector_cswap_width()` is read in the cswap emitters.
  - Confirm the current `DIALOG_GCD_BODY_CARRY_BAND_TRIMS` schedule is active.
- Full validator:
  - `./benchmark.sh` from the cloned benchmark working tree.
- Official validation:
  - Required before any public submit claim.
- Dirty classes to track:
  - `local-only improvement`
  - `relocated peak`
  - `failed cleanup`

## Compute

- Compute needed: local CPU benchmark runs only.
- Predicate: setting `DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=1` lowers avg Toffoli
  without raising qubits.
- Owner: Kimi Storm
- Budget: ≤ 5 full local benchmark iterations (single boolean toggle).
- Stop condition:
  - Stop if qubit count rises above 1170.
  - Stop if correctness tests fail.
  - Stop if improvement is < 50 avg Toffoli.

## Safety

- Public-credit policy:
  - Route inspired by memory notes in `src/point_add/memory/` (section C1) and
    the explicit TODO/commentary around controlled-body band trimming. Credit
    nasqret / prior promoted submissions for the q1170 baseline.
- Redaction concerns:
  - No live `DIALOG_TAIL_NONCE` value in public notes.
  - No private compute endpoints or local home paths.
- Submit gate:
  - Fresh frontier recheck.
  - Official local validation passes with `0/0/0`.
  - Score beats 1677861900.
  - Diff is legal and narrow: change the default in
    `src/point_add/mod.rs:1418` from `"0"` to `"1"` plus a measured public note.
  - Public note ready with evidence label and credits.
  - Explicit user submit flag.

## Result

**Status: parked / falsified on 2026-06-14.**

Local experiment at commit `7bab51f`:

| Metric | Baseline | Toggle (`DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=1`) |
|--------|----------|-----------------------------------------------------|
| emitted ops | 10,301,716 | 10,296,700 (−5,016) |
| qubits | 1170 | 1170 |
| classical mismatches | 0 | **72** |
| phase-garbage batches | 0 | **35** |
| correctness | pass | **fail** |

The toggle reduced emitted ops as predicted but broke correctness. The memory
note's "island-free" reasoning does not hold for the current q1170 configuration.
Do not pursue further unless combined with a different body-carry schedule, tail
nonce, or other co-tuning that restores `0/0/0`.

## First experiment

1. Build once in the benchmark working tree:
   ```bash
   ./setup.sh
   ```
2. Run the baseline:
   ```bash
   ./benchmark.sh
   cp score.json score.baseline.json
   ```
3. Re-run with the toggle enabled:
   ```bash
   DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=1 ./benchmark.sh
   cp score.json score.trim.json
   ```
4. Compare `score.baseline.json` and `score.trim.json`.
5. If lower Toffoli, qubits stay at 1170, and 9024-shot validation passes with
   the existing `DIALOG_TAIL_NONCE`, no nonce re-hunt is needed. Re-hunt only if
   validation reports classical mismatches or phase-garbage batches.
6. If the experiment succeeds, edit `src/point_add/mod.rs:1418` to change the
   default from `"0"` to `"1"` before submitting.
