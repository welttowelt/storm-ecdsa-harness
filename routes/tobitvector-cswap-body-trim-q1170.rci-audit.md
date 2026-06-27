# RCI Audit: `tobitvector-cswap-body-trim-q1170` route packet

## Issue 1: Filename does not match route ID

**Problem:**
The file is named `shift-band-trims.md` but the route ID inside is
`tobitvector-cswap-body-trim-q1170`. The old name refers to the abandoned
`DIALOG_GCD_SHIFT_BAND_TRIMS` target.

**Evidence:**
- Filename: `storm-ecdsa-harness/routes/shift-band-trims.md`
- Route ID field: `tobitvector-cswap-body-trim-q1170`

**Why it affects the route:**
A future operator opening `shift-band-trims.md` expects the old route. Misrouting
wastes time and can cause the wrong experiment to be run.

**Source check:**
The correction paragraph inside the file acknowledges the name mismatch but does
not fix the filename itself.

**Smallest useful fix:**
Rename the file to `tobitvector-cswap-body-trim-q1170.md` and delete or archive
the `shift-band-trims.md` name.

---

## Issue 2: Memory-note citation is wrong

**Problem:**
The route claims memory note section **B2** estimates the savings. The actual
section is **C1** — "tobitvector cswap band-trim".

**Evidence:**
- Route says: "Memory note `src/point_add/memory/2026-06-07-measured-frontier-leads.md` (B2)"
- Source says: section header is `## C. Partial cswap reduction` and the entry is
  labeled `C1 — tobitvector cswap band-trim` (line 133).

**Why it affects the route:**
Wrong section label makes the citation unverifiable and weakens the evidence
label. Another reader will search for B2 and find something else.

**Source check:**
Section B2 in the memory note is actually "freeing `composite_scratch.owned`"
(line 126), a different (and rejected) idea.

**Smallest useful fix:**
Change `(B2)` to `(C1)` throughout the route packet.

---

## Issue 3: The memory note says the cut is "untested"

**Problem:**
The route presents the ~1,600 CCX savings as a measured estimate, but the source
note marks the cut as **untested** and value-exact by reasoning.

**Evidence:**
- Route says: "Memory note B2 estimates clamping the cswap loop bound ... saves ~1,600 CCX."
- Source note C1 says: "Correctness: **untested** but value-exact by the body trim's own premise."

**Why it affects the route:**
The evidence label should be `Inference` or `Historical clue`, not `Source fact plus Inference`.
Overclaiming the evidence level could lead to spending compute on a route whose
savings are purely theoretical.

**Source check:**
The note itself is clear that this is an unvalidated optimization idea.

**Smallest useful fix:**
Downgrade the evidence label to `Historical clue` or `Source fact plus Inference
(untested)`. Add the word "untested" before the savings estimate.

---

## Issue 4: Experiment commands rebuild unnecessarily

**Problem:**
The first experiment tells the operator to run `./setup.sh && ./benchmark.sh` for
both baseline and toggle runs. `./setup.sh` rebuilds the Rust binaries, which is
slow and uses disk. The toggle is a runtime env-var; only the benchmark stage
needs to re-run.

**Evidence:**
- Route says: `DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=1 ./setup.sh && ./benchmark.sh`
- `configure_ecdsafail_submission_route()` reads the env var at runtime via
  `set_default_env`, so the compiled binary is unchanged.

**Why it affects the route:**
On a 5 GB pod, unnecessary rebuilds waste disk and time. The correct workflow is
build once, then run benchmark with different env vars.

**Source check:**
`set_default_env` in `src/point_add/mod.rs:1001-1005` only sets the var if it is
not already present; the env lever is read at circuit-build time inside
`configure_ecdsafail_submission_route()`.

**Smallest useful fix:**
Change the experiment steps to:
```bash
./setup.sh                    # build once
./benchmark.sh                # baseline
DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM=1 ./benchmark.sh   # toggle
```

---

## Issue 5: Submit diff claim is misleading

**Problem:**
The route says the diff is "one env-var toggle + measured note". To actually
submit a score improvement, the default in the source must change from `"0"` to
`"1"` in `src/point_add/mod.rs:1418`.

**Evidence:**
- Route says: "Diff is legal and narrow (one env-var toggle + measured note)."
- Source shows: `set_default_env("DIALOG_GCD_TOBITVECTOR_CSWAP_BODY_TRIM", "0");`

**Why it affects the route:**
The grader runs the repo with the source defaults. Just exporting the env var
locally does not change the submitted diff. The route must explicitly include
editing `mod.rs` as the submission change.

**Source check:**
`benchmark.json` lists `editablePaths: ["src/point_add"]`, confirming the
submission must modify source files under that path.

**Smallest useful fix:**
Add a step: "If the toggle works, change `src/point_add/mod.rs:1418` from `"0"`
to `"1"` before submitting."

---

## Issue 6: Re-hunt instruction is probably unnecessary

**Problem:**
The route says to re-hunt `DIALOG_TAIL_NONCE` if the toggle works. The memory
note explicitly calls this cut **island-free** and says the existing frontier
tail value survives. Keep the raw value out of the public route packet.

**Evidence:**
- Route says: "If lower Toffoli and qubits stay at 1170, re-hunt `DIALOG_TAIL_NONCE`..."
- Source note C1 says the accepted body-trim premise is island-free and the
  existing frontier tail value survives.

**Why it affects the route:**
Re-hunting nonces costs compute. If the premise is island-free, the existing
frontier nonce should survive; re-hunt only becomes necessary if validation
fails.

**Source check:**
The note's island assessment is part of its evidence; the route should not
override it without reason.

**Smallest useful fix:**
Change the instruction to: "If correctness tests pass with the existing
`DIALOG_TAIL_NONCE`, no re-hunt is needed. Re-hunt only if 9024-shot validation
reports phase-garbage or classical mismatches."

---

## Fixes applied

All issues above were fixed in the revised route packet:

- File renamed to `tobitvector-cswap-body-trim-q1170.md`.
- Old `shift-band-trims.md` removed.
- Memory-note citation corrected from B2 to C1.
- Evidence label downgraded to `Historical clue (untested source idea)`.
- Savings described as "untested" estimate.
- Experiment commands changed to build once, run benchmark twice.
- Submit diff explicitly includes editing `src/point_add/mod.rs:1418`.
- Re-hunt instruction corrected to run only if validation fails.

## Summary verdict

The route is now actionable. Proceed with the cheap toggle experiment.
