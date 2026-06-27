# Skill: Paper - Remaud Ancilla-Free Adder

Use when a peak is blocked by carry workspace and a zero-ancilla adder suffix
could trade extra Toffolis for a lower qubit tier.

## Source

- Maxime Remaud and Vivien Vandaele, "Ancilla-free Quantum Adder with
  Sublinear Depth", arXiv:2501.16802.

## Why We Keep It

The paper gives exact quantum adders using only Toffoli, CNOT, and X gates with
no ancilla qubits. It also includes increment and constant-add constructions.
For ecdsa.fail, this is not a default replacement; it is a pressure-release
tool for very short suffixes where one resident carry lane creates the peak.

## Apply To

- max-peak add suffixes;
- carry ladders where a small no-ancilla section can remove a clean carry lane;
- emergency q-tier cuts that have explicit Toffoli headroom.

## Required Invariant

The no-ancilla replacement must preserve the same carry-in, carry-out, target
value, and phase as the clean-ladder segment it replaces.

## Procedure

1. Identify the shortest suffix that overlaps the peak.
2. Estimate Toffoli growth before writing code.
3. Reject full-width replacements unless the lower q tier has score headroom.
4. Run `scripts/qcut-candidate-prefilter.sh`; any final `KILL (gate N)` verdict
   blocks a source hook.
5. Build a reduced-width suffix toy with the same carry boundary.
6. Port one callsite and run count/residual before widening.

## Output

```text
Remaud ancilla-free adder:
- Suffix width:
- Carry boundary:
- Q saved:
- Toffoli delta estimate:
- Toy evidence:
- Count/residual:
- Decision: port / shrink / park
```

## Kill Gate

If the Toffoli delta cannot fit the target q tier, do not port it just to make
a count-only peak line smaller.

For current d44/q1152 work, treat full-width or factor-2 replacements as parked
unless a fresh product calculation proves otherwise. This paper is a suffix
pressure-release tool, not a broad carry-ladder replacement.
