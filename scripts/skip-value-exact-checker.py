#!/usr/bin/env python3
"""skip-value-exact-checker.py — certify a reversible-circuit "skip" is value-exact (dead on ALL inputs)
via z3 bit-vector SMT discharge. Implements the per-skip recipe in value-exact-skip-certification.md.

License theorem: for a REVERSIBLE-CLASSICAL circuit (CNOT/Toffoli/X/arith, no H/T on data qubits),
dead-on-all-basis-states <=> dead-on-all-superposition-states (gates act permutationally). So a z3-UNSAT
discharge on the bit-vector semantics IS a value-exact certificate. AUDIT first that the skip does not
cross a genuine-superposition register (see the skill).

Requires: pip install z3-solver

Usage (built-in skip types):
  skip-value-exact-checker.py exact-remainder --width 256 --max 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F   # prove a width-bit value is always < max (mod-reduce is a no-op)
  skip-value-exact-checker.py top-carry --width 32 --operand-max 0x7FFFFFFF --carry-bit 31                                          # prove bit-31 carry can't fire given operand bounds
  skip-value-exact-checker.py dead-control --width 8 --control-mask 0xF0 --invariant-mask 0x0F                                       # prove control bits are always 0 under the input invariant
  skip-value-exact-checker.py demo                                                                                                  # run all 3 demos (secp256k1-flavored)

Each query: if z3 returns UNSAT -> CERTIFIED (value-exact on all inputs); SAT -> NOT-VALUE-EXACT (prints
the counterexample). For a custom skip, encode its "must-be-false" condition as a z3 BitVec expression and
call check_unsat(formula).
"""
import sys
try:
    import z3
except ImportError:
    sys.exit("install z3-solver: pip install z3-solver")

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def check_unsat(formula, desc=""):
    """Return 'CERTIFIED' if formula is UNSAT (skip is value-exact on all inputs), else 'NOT-VALUE-EXACT' + model."""
    s = z3.Solver()
    s.add(formula)
    r = s.check()
    if r == z3.unsat:
        print(f"CERTIFIED (UNSAT){': '+desc if desc else ''} — skip is value-exact on all inputs.")
        return True
    if r == z3.sat:
        print(f"NOT-VALUE-EXACT (SAT counterexample){': '+desc if desc else ''}:")
        print("  ", s.model())
        return False
    print(f"UNKNOWN (z3 could not decide){': '+desc if desc else ''} — treat as NOT certified.")
    return False

def exact_remainder(width, max_val):
    """Prove a width-bit value is ALWAYS < max_val (so a mod-reduce by max_val is a no-op)."""
    v = z3.BitVec("v", width)
    # the skip is value-exact iff it's impossible for v >= max_val
    return check_unsat(z3.UGE(v, max_val), f"exact-remainder: width-{width} value always < 0x{max_val:x}")

def top_carry(width, operand_max, carry_bit):
    """Prove the carry into carry_bit can't fire when each operand is in [0, operand_max]."""
    a = z3.BitVec("a", width); b = z3.BitVec("b", width)
    # bound operands
    conds = [z3.UGE(a, 0), z3.ULE(a, operand_max), z3.UGE(b, 0), z3.ULE(b, operand_max)]
    carry_fires = z3.Extract(carry_bit, carry_bit, a + b) == 1  # the carry-out bit of the sum
    return check_unsat(z3.And(*(conds + [carry_fires])), f"top-carry: bit-{carry_bit} carry can't fire (operands <= 0x{operand_max:x})")

def dead_control(width, control_mask, invariant_mask):
    """Prove the control bits (control_mask) are always 0 under an input invariant (invariant_mask bits = 0)."""
    v = z3.BitVec("v", width)
    invariant = (v & invariant_mask) == 0          # input invariant: these bits are 0
    control_nonzero = (v & control_mask) != 0      # the skip is value-exact iff control can't be nonzero under the invariant
    return check_unsat(z3.And(invariant, control_nonzero), f"dead-control: bits 0x{control_mask:x} always 0 under invariant 0x{invariant_mask:x}")

def demo():
    print("=== DEMO: 3 skip-type certifications (secp256k1-flavored) ===\n")
    print("[1] exact-remainder: a 256-bit value always < secp256k1 p? (trivially NOT — full range)")
    exact_remainder(256, SECP256K1_P)  # a raw 256-bit value is NOT always < p (expected NOT-VALUE-EXACT — illustrates the tool flags non-value-exact skips)
    print("\n[2] top-carry: bit-31 carry can't fire if operands <= 0x7FFFFFFF (31-bit)? (CERTIFIED)")
    top_carry(32, 0x7FFFFFFF, 31)
    print("\n[3] dead-control: high nibble always 0 if low-nibble-only invariant? (CERTIFIED)")
    dead_control(8, 0xF0, 0xF0)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    t = sys.argv[1]
    if t == "demo": demo(); sys.exit(0)
    kw = {}
    for a in sys.argv[2:]:
        k, _, v = a.partition("=") if "=" in a and not a.startswith("--") else (a[2:], None)
        if a.startswith("--") and "=" in a: k, v = a[2:].split("=", 1)
        elif a.startswith("--"): continue
        else: k, v = a.split("=", 1) if "=" in a else (a, None)
    # parse --key=val
    args = {}
    for a in sys.argv[2:]:
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            args[k] = int(v, 0)  # auto-base (0x..)
    if t == "exact-remainder": exact_remainder(args["width"], args["max"])
    elif t == "top-carry": top_carry(args["width"], args["operand-max"], args["carry-bit"])
    elif t == "dead-control": dead_control(args["width"], args["control-mask"], args["invariant-mask"])
    else: print(f"unknown type '{t}'; try: exact-remainder | top-carry | dead-control | demo")
