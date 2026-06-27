#!/usr/bin/env python3
"""Toy checker for the Gidney threaded-add boundary carry question."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    width: int
    cin_present: bool
    ctrl: int
    cin: int
    a: int
    b: int
    cout: int


@dataclass(frozen=True)
class Result:
    ctrl: int
    cin: int
    a: int
    b: int
    cout: int


def standard_top_segment(case: Case, *, boundary_dead: bool) -> Result:
    ctrl = case.ctrl
    ci = case.cin
    a = case.a
    b = case.b
    cout = case.cout
    co = 0

    if case.cin_present:
        a ^= ci
        b ^= ci
        co ^= a & b
        co ^= ci
    else:
        co ^= a & b

    if not boundary_dead:
        cout ^= ctrl & co

    if case.cin_present:
        co ^= ci
    co ^= a & b
    if co != 0:
        raise AssertionError(f"top carry did not clean for {case}: co={co}")

    if case.cin_present:
        a ^= ci
    a ^= ctrl & b
    if case.cin_present:
        b ^= ci

    return Result(ctrl=ctrl, cin=ci, a=a, b=b, cout=cout)


def elided_dead_boundary(case: Case) -> Result:
    ctrl = case.ctrl
    ci = case.cin
    a = case.a
    b = case.b
    cout = case.cout

    if case.cin_present:
        a ^= ci
        b ^= ci

    if case.cin_present:
        a ^= ci
    a ^= ctrl & b
    if case.cin_present:
        b ^= ci

    return Result(ctrl=ctrl, cin=ci, a=a, b=b, cout=cout)


def elided_with_boundary_formula(case: Case) -> Result:
    ctrl = case.ctrl
    ci = case.cin
    a = case.a
    b = case.b
    cout = case.cout

    if case.cin_present:
        a ^= ci
        b ^= ci
        cout ^= ctrl & (ci ^ (a & b))
    else:
        cout ^= ctrl & (a & b)

    if case.cin_present:
        a ^= ci
    a ^= ctrl & b
    if case.cin_present:
        b ^= ci

    return Result(ctrl=ctrl, cin=ci, a=a, b=b, cout=cout)


def elided_without_boundary_formula(case: Case) -> Result:
    return elided_dead_boundary(case)


def iter_cases(max_width: int) -> list[Case]:
    cases: list[Case] = []
    for width in range(1, max_width + 1):
        cin_modes = (False, True) if width == 1 else (True,)
        for cin_present in cin_modes:
            for ctrl in (0, 1):
                for cin in (0, 1):
                    if not cin_present and cin != 0:
                        continue
                    for a in (0, 1):
                        for b in (0, 1):
                            for cout in (0, 1):
                                cases.append(
                                    Case(
                                        width=width,
                                        cin_present=cin_present,
                                        ctrl=ctrl,
                                        cin=cin,
                                        a=a,
                                        b=b,
                                        cout=cout,
                                    )
                                )
    return cases


def anf_degree(values: list[int], variable_count: int) -> int:
    coeffs = values[:]
    for bit in range(variable_count):
        step = 1 << bit
        for mask in range(1 << variable_count):
            if mask & step:
                coeffs[mask] ^= coeffs[mask ^ step]
    degree = 0
    for mask, coeff in enumerate(coeffs):
        if coeff:
            degree = max(degree, bin(mask).count("1"))
    return degree


def boundary_formula_anf_degree(cin_present: bool) -> int:
    # Variables are ctrl, ci, a, b. For no-cin mode ci is pinned to 0.
    values: list[int] = []
    for mask in range(16):
        ctrl = (mask >> 0) & 1
        ci = (mask >> 1) & 1
        a = (mask >> 2) & 1
        b = (mask >> 3) & 1
        if not cin_present:
            ci = 0
        folded_a = a ^ ci if cin_present else a
        folded_b = b ^ ci if cin_present else b
        if cin_present:
            values.append(ctrl & (ci ^ (folded_a & folded_b)))
        else:
            values.append(ctrl & (folded_a & folded_b))
    return anf_degree(values, 4)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check toy Boolean obligations for Gidney top boundary carry elision."
    )
    parser.add_argument("--max-width", type=int, default=6)
    parser.add_argument("--truth-table", action="store_true")
    args = parser.parse_args()

    if args.max_width < 1:
        parser.error("--max-width must be positive")

    cases = iter_cases(args.max_width)
    dead_mismatches = []
    formula_mismatches = []
    naive_mismatches = []

    for case in cases:
        standard_dead = standard_top_segment(case, boundary_dead=True)
        dead_elided = elided_dead_boundary(case)
        if standard_dead != dead_elided:
            dead_mismatches.append((case, standard_dead, dead_elided))

        standard_live = standard_top_segment(case, boundary_dead=False)
        formula_elided = elided_with_boundary_formula(case)
        if standard_live != formula_elided:
            formula_mismatches.append((case, standard_live, formula_elided))

        naive_elided = elided_without_boundary_formula(case)
        if standard_live != naive_elided:
            naive_mismatches.append((case, standard_live, naive_elided))

    if args.truth_table:
        print("width\tcin_present\tctrl\tcin\ta\tb\tcout_in\tboundary_formula")
        for case in cases:
            folded_a = case.a ^ case.cin if case.cin_present else case.a
            folded_b = case.b ^ case.cin if case.cin_present else case.b
            if case.cin_present:
                formula = case.ctrl & (case.cin ^ (folded_a & folded_b))
            else:
                formula = case.ctrl & (folded_a & folded_b)
            print(
                f"{case.width}\t{int(case.cin_present)}\t{case.ctrl}\t{case.cin}"
                f"\t{case.a}\t{case.b}\t{case.cout}\t{formula}"
            )

    nondead_degree_with_cin = boundary_formula_anf_degree(cin_present=True)
    nondead_degree_without_cin = boundary_formula_anf_degree(cin_present=False)
    native_ccx_target_degree = 2
    status = "pass" if not dead_mismatches and not formula_mismatches else "fail"
    print(
        "gidney_boundary_toy="
        f"{status} evidence_label=Partial max_width={args.max_width} cases={len(cases)} "
        f"dead_boundary_mismatches={len(dead_mismatches)} "
        f"nondead_formula_mismatches={len(formula_mismatches)} "
        f"naive_nondead_mismatches={len(naive_mismatches)} "
        f"nondead_degree_with_cin={nondead_degree_with_cin} "
        f"nondead_degree_without_cin={nondead_degree_without_cin} "
        f"native_ccx_target_degree={native_ccx_target_degree} "
        f"needs_degree3_or_product_scratch={int(nondead_degree_with_cin > native_ccx_target_degree)} "
        "phase_proof=0 ancilla_proof=0"
    )
    print(
        "decision=dead-boundary-top-carry-elision-is-classically-exact; "
        "nondead-boundary-needs-ctrl-and-majority-formula-before-source-edit"
    )

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
