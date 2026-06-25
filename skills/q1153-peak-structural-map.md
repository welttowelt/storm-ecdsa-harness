# Skill: q1153 Peak Structural Map + Ancilla-Garbage Kill-Test (ecdsa.fail secp256k1)

Use when attempting ANY qubit-width (peak) cut on the ecdsa.fail secp256k1 reversible EC point-add
circuit (peak 1153), or when diagnosing nonce-independent full-circuit dirt after a fold-suffix edit.
This is the durable structural map + kill-test from 2 cycles of adversarial paper-mining — it tells you
in advance which cuts CAN'T work and why, so you stop re-walking dead space.

## ⚠️ CORRECTION (live TRACE_ALLOC_NEAR_PEAK, 2026-06-25, cascade pilot — trumps the anatomy below on the peak SITE)

The marginal +1 (1152→1153) is **NOT** the graduated-suffix boundary `cout` stack (arith.rs:826-838)
claimed in the anatomy below. It is the **INTERNAL carry `int` of `const_chunk_add_clean`** (arith.rs:646,
~:810), ops_idx=2682127, phase `tlm_apply_inverse_mod_sub_fold` — the ONLY `free_pool=0` alloc in the
fold (all 1153 ids live quantum data; no donor to borrow — force-borrow trips `Op::validate`'s aliasing
guard). Peak 1153 is therefore a **HARD RIPPLE-CARRY FLOOR**: all s-1 carries of a chunk are
simultaneously live; there is no transient borrow slot inside a stage. The conditionally-clean cascade
(Rank-1 below) is **CLOSED**: a synthesized-`|0>` donor costs +13,319 CCX (Toffoli penalty eats the
1-qubit win → score worse) AND force-borrow hits 9024/141/141 (garbage wall). Only a NON-RIPPLE adder
(Gidney Fig-2 vented-streaming) or an algebraic re-factor (pair-complete / Schrottenloher modmul width)
can break the floor. The kill-test / MBU-baked-in / toffoli-vs-width / dead-bit-borrow sections below
remain valid; only the peak SITE (internal carry, not boundary cout) is corrected.

## DEFINITIVE (Fig-2 pilot, 2026-06-26): ALL adder-substitution routes CLOSED. Peak = width-1 (s=2) single-carry floor.

The graduated staircase chunks are s=2..6; their max-active is **s=2 → 1153 (THE PEAK)**, s=3 → 1152,
s=4 → 1151, s=5 → 1150, s=6 → 1149. The peak instance is a **single internal carry `int[0]` on a 1152
resident floor** — a WIDTH-1 ripple. This closes every adder trick:
- **Fig-2 vented-streaming** (arXiv:2507.23079 Fig 2): value-exact in isolation (5456/5456 selftest) but
  keeps `cur+nxt = 2 carries` live for s=2 → peak 1154 (WORSE). Its non-ripple property is irrelevant when
  the ripple is already width-1 (any adder needs ≥2 carries for s=2: c_1 feeds c_2=cout). It only wins for
  s≥4 chunks, which sit BELOW the global peak → no score change. ROUTE CLOSED.
- **Fig-5 3-clean** (arXiv:2507.23079 Fig 5): peak 1152 achieved + adder value-exact (anc=0, stale-index
  confirmed), but Q×T-NEGATIVE raw (4n Toffoli > graduated clean-MBU → avgT ~1,407,928 → loses #1 by
  ~44M). PATH B (approximation fix) is STRUCTURALLY BLOCKED: Gidney ≡ graduated bit-identical on SUMS,
  but diverges on PHASE PROFILE — different MBU mechanisms (graduated = comparator-based
  `controlled_erase_carry_gated_const` phase deposit cancelled across ~40 folds; Gidney = X-basis vent +
  Z-discharge). The fold's correctness DEPENDS ON the graduated's phase-compounding; matching it inside
  the Gidney suffix would replicate the comparator = defeats the 3-clean win. So landing q1152 needs
  PATH C (deep island hunt ~3e-7, fleet — find a nonce where the phase compounding cancels → 0 pha) +
  PATH A (per-nonce value-exact drop regen, DEAD_SCAN_REAL_SEAD=1 → avgT ~1,368,349, Q×T-positive). NOT a
  cheap win; a real cut gated on fleet island-hunt + value-exact drops.
- **Conditionally-clean cascade**: CLOSED (no donor at the peak; ripple floor).

**THE PEAK +1 IS LOAD-BEARING**: int[0] of the s=2 chunk + the boundary `cout` (deferred-erase into the
next chunk's carry-in). No adder substitution removes it.

**ONLY REMAINING STRUCTURAL LEVERS** (all hard/unproven): (1) **pair-complete simplification**; (2)
**Schrottenloher modmul/modadd width** (algebraic re-factor of the resident base, not the carry); (3)
**staircase-reshape** — restructure the graduated staircase so the peak chunk is WIDE (s≥4), where the
banked value-exact Fig-2/Fig-5 adders WOULD help (Fig-2 selftest banked in worktree for this). Until one
of these lands, the q1153 peak cut is EXHAUSTED and the nonce-variance island hunt (Akash) is the only
live #1 path.

## The peak anatomy (the one fact every candidate must pass)

Peak 1153 is NOT a single adder's ripple carries. It is **4 INTER-CHUNK boundary `cout` ancillae**
(`carries` Vec, arith.rs:834) of a graduated staircase [4,3,2,1] that must COEXIST because
`controlled_add_const_chunked_graduated_off` runs ALL forward chunks first, then reverse-erases
(arith.rs:836-846), and each reverse-erase reads `carries[j-1]` as a LIVE quantum carry-in (`cin_ref`,
arith.rs:842). entry_active 1149 + 4 carries = 1153. Nine other phases sit at a 1152 floor; ONLY
`tlm_apply_inverse_mod_sub_fold` is +1.

CONSEQUENCE: per-adder single-ancilla tricks (CDKM, Cuccaro) and ripple-carry-elimination papers
(Remaud-Vandaele arXiv:2402.18594) DO NOT HELP — our carries are a **deferred-erase boundary
structure**, not a ripple. Reject any candidate that assumes a ripple.

## The ancilla-garbage kill-test (nonce-independent 9024/141/141)

After a fold-suffix edit, full-circuit eval of `9024 cls / 141 pha / 141 anc`, identical across ALL
Fiat-Shamir nonces incl. random, is the signature of an **INEXACT wide-suffix dirty-borrow restore**
(phase-ordering / wrong borrow axis) — i.e. a **palindrome violation**. It is reproduced by:
`TLM_FORCE_DIRTY_SUFFIX=1`, the Gidney-2507.23079 Fig-5 dirty-borrow port, per-call g-reduction,
spooky-pebbling mid-circuit Hadamard, HRS17 on a branching suffix, Zhang-Cho-Lee-Seo forced on nested
carries. Any candidate whose restore is NOT a literal unitary inverse over a flat linear adder trips it.
**THE DIFFERENTIATOR:** is the restore unitary-invertible BY CONSTRUCTION (conditionally-clean
[Khattar-Gidney], Bennett compute-copy-uncompute) → safe; or inexact (dirty-borrow, MBU on entangled
wires, ghosting) → this wall. (See also `circuit-edit-integration-safety.md` for the cheap
stale-index/free-pool falsifier ladder before declaring it this wall.)

## MBU is ALREADY baked in; the peak carries are NON-MBU-able

The repo already measurement-uncomputes (hmr + cz_if_bit/cz/ccz deferred-phase) every INTERNAL carry of
the +f fold (const_chunk_add_clean arith.rs:666-685; clean_add_threaded_opt arith.rs:196-230;
controlled_erase_carry_gated_const arith.rs:793-810). The boundary `cout` carries at the PEAK are
structurally **NON-MBU-able**: each is the coherent quantum carry-in of the NEXT forward chunk
(arith.rs:649-659: `cx(cin_ref,a[i]); ccx(a[i],cin_ref,cout_ref)`). Measuring it destroys the downstream
carry-in superposition — a **forward data-dependency wall MORE fundamental than the reverse-erase
liveness**. Candidates re-proposing Gidney-2018 MBU / Luongo-Miti on these carries duplicate
already-shipped optimizations targeting the wrong (non-MBU-able) carries. (The Gidney-2507.23079 Fig-5
port hits this: isolation-clean, full-circuit 9024/141/141.)

## Toffoli-axis vs width-axis confusion = the #1 finding-bug source

Gidney-2018 (temporary logical-AND), Luongo-Miti MBU, and Remaud-Vandaele ancilla-free adder reduce
**TOFFOLI COUNT / DEPTH, NOT peak qubit width**. The score is `avg_Toffoli × peak_qubits`. On a graduated
suffix of width n≤4, these asymptotic constructions blow up the Toffoli factor (O(n log n) vs ~8
CCX/chunk) → score-NEUTRAL or score-NEGATIVE. **Only conditionally-clean (Khattar-Gidney) and the
terminal-carry drop (already wired as TLM_GRAD_FINAL_NO_COUT) touch the WIDTH axis on the peak carries.**

## The dead-bit-borrow precondition (universal gate for resident-bit reuse)

Any technique that borrows/reuses a RESIDENT bit during the fold (conditionally-clean cascade, dirty
borrow, recompute-later) needs ≥1 RESIDENT bit that is DEAD across the entire fold plateau. The plateau
(`tlm_apply_inverse_mod_sub_fold` inside `apply_step_reverse` inside `reverse_gcd_jump`) sits in the
apply pipeline where codec-tape(406) / divstep-flags(4) / shrunk-GCD-u(91) are ALL LIVE. The divstep
SYMBOL bits are deliberately DROPPED before the apply (gcd.rs ~760) so they are NOT resident at the peak
and CANNOT be borrowed. **MANDATORY first step for any borrowed-bit technique:** a per-op active-timeline
liveness scan during the fold to find/confirm a verified-dead resident bit. Without one, every
resident-bit-reuse route dies for lack of a target.

## The one surviving value-safe candidate (cycle 2) — CLOSED by cascade pilot (2026-06-25)

Conditionally-clean borrowed ancilla for ONLY the j=0 (first) carry — Khattar & Gidney, "Rise of
conditionally clean ancillae," Quantum 9:1752 (2025) / arXiv:2407.17966. Replace the j=0 `alloc_qubit()`
(arith.rs:834) with a conditionally-clean handle to a verified-dead resident bit (Khattar-Gidney
AND-accumulator). Ceiling = **1152 (one carry only)** — cascaded cuts blocked by the live cout_{j-1}
carry-in read. value-exact BY CONSTRUCTION (unitary-invertible). TWO blockers: (i) the dead-resident-bit
precondition is unverified (run the liveness scan first); (ii) the builder only exposes
`loan_zero_qubit` (assumes |0>) — needs a NEW unknown-state-borrow op, or the port silently falls back
to dirty-borrow and dies. Caveat: per the findability-wall memory, q1152 value-exact beats are
UNFINDABLE on the live frontier (cls floor >18 → islands too rare) — a correctness win that may not yield
a submittable #1 this window.

## Credit

Synthesized from qcut-paper-mining workflow cycles 1-2 (2026-06-25): 58 papers screened, 55 closed.
Key sources: Khattar & Gidney arXiv:2407.17966 (Quantum 9:1752); Gidney arXiv:2507.23079;
Nie-Zi-Sun arXiv:2402.05053; Remaud-Vandaele arXiv:2402.18594; Schrottenloher space-optimized mod-arith.
Companion skills: `conditionally-clean-cascade-cut.md`, `circuit-edit-integration-safety.md`. Do not
imply copied code.
