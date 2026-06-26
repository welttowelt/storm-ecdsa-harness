# Skill: Value-Exact Skip Certification (reversible-classical dead-op elimination)

Use when porting/designing value-exact "skip" optimizations (structural-dead-call, exact-remainder,
top-carry, dead-CSWAP/dead-shift) on a REVERSIBLE-CLASSICAL circuit (CNOT/Toffoli/X/arith, no H/T on
data qubits) — e.g. the ecdsa.fail secp256k1 point-add. Tells you how to CERTIFY a skip is dead on ALL
inputs (not just sampled/reachable), so it's value-exact and won't dirty the island.

## The license theorem (the single load-bearing fact)

For a **reversible-classical** subcircuit, dead-on-all-computational-basis-states ⟺ dead-on-all-
superposition-states, because reversible classical gates act permutationally on the basis. So a skip you
prove dead classically (on all basis states) is dead on every superposition input → value-exact. Source:
Yu & Palsberg, *Quantum Abstract Interpretation*, PLDI 2021 (the abstract domain is EXACT, not an
over-approximation, for reversible-classical circuits).

## ⚠ The audit (do this FIRST, before certifying any skip)

The classical license holds ONLY if the skip does not cross a qubit that is ever in GENUINE SUPERPOSITION
(e.g. a QFT/phase register in a modular-inversion routine). Audit: for every qubit a skip reads/writes,
confirm it stays computational-basis throughout (or prove so via abstract stabilizer sim — Quantum
Abstract Interpretation companion, Quantum 2023). If a skip crosses a superposition qubit, the classical
certificate is INSUFFICIENT → fall back to a full denotational-semantics rewrite proof (VOQC/Coq, Quartz/SMT).

## Per-skip-type certification recipe

| Skip type | Certificate | Discharge |
|---|---|---|
| **Structural dead-call** (call output unused / on known-zero operand) | output liveness = ⊥ on symbolic state; denotation unchanged | symbolic exec (Giallar) or Coq (VOQC) |
| **Exact-remainder** (mod-reduce is no-op: val already < p) | range domain proves val ∈ [0,p); query sat(val − p ≥ 0) → expect **UNSAT** | **z3/cvc5 bit-vector** |
| **Top-carry** (bit-31/30 carry structurally can't fire) | operand-width bounds; query sat(carry_N ∧ operand_ranges) → **UNSAT** | **z3/cvc5 bit-vector range** |
| **Dead-CSWAP / dead-shift** (control structurally false on reachable input manifold) | symbolic-exec + abduction (QUESO): "skip sound iff condition C"; sat(¬C) → **UNSAT**; OR AQCEL initial-state proof (record the input invariant, e.g. operand ∈ [0,p), as a precondition) | symbolic exec + SMT |

Use **bit-vector theory** (word-level, fully decidable) rather than integer arithmetic for the SMT queries —
nonlinear modular integer reasoning is undecidable in general (Programming Z3). Each skip = one
discharge obligation; UNSAT ⇒ value-exact on all inputs.

## Sources (ranked)

1. **Giallar** — Tao et al., PLDI 2022 (symbolic-exec verification; the structural-dead-call template). arXiv:2205.00661.
2. **Quantum Abstract Interpretation** — Yu & Palsberg, PLDI 2021 (the license theorem + dead-code detection). DOI 10.1145/3453483.3454061. Companion: Abstract Stabilizer Simulation, Quantum 2023 (superposition audit engine).
3. **AQCEL** — Quantum 2022 q-2022-09-08-798 (initial-state-dependent controlled-op removal = dead-CSWAP/dead-shift precedent). arXiv:2209.02322. Record input invariants as preconditions.
4. **Quartz + QUESO** — Xu et al., PLDI 2022/2023 (SMT-based peephole verification; QUESO abduction = the discharge-obligation pattern). Quartz arXiv:2204.09033; QUESO arXiv:2211.09691.
5. **VOQC + ReVerC** — Hietala et al. POPL 2021 / Amy et al. (Coq/F* machine-checked rewrites — gold-standard if a proof object is needed). VOQC arXiv:1912.02250; ReVerC arXiv:1603.01635.
6. **Sound Symbolic Execution via Abstract Interpretation** — VMCAI 2023 (the composition principle for symbolic-exec + SMT + range domains).
7. Maslov/Soeken template matching (structural identity removal via SAT).
8. SMT over modular/bit-vector arithmetic: Programming Z3 (theory.stanford.edu/~nikolaj/programmingz3.html); Integer Reasoning Modulo Different Constants; Difference Constraints over Modular Arithmetic.

## Companion tool

`scripts/skip-value-exact-checker.py` — encodes each skip type as a z3 bit-vector SMT query and returns
CERTIFIED (UNSAT) or NOT-VALUE-EXACT (SAT counterexample). Run it on each skip before trusting the port.
