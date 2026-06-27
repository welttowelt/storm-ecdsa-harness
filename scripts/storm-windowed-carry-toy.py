#!/usr/bin/env python3
"""Toy/count gate for windowed Gidney threaded carries.

This is a public verifier for the next gate, not a circuit edit. It compares
the current full stored-carry threaded-add schedule against a reduced-storage
schedule that keeps only a top carry window and reverses the bottom prefix with
a coherent in-place UMA.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Case:
    width: int
    cin_present: bool
    cout_present: bool
    vents: int
    ctrl: int
    cin: int
    cout: int
    a: tuple[int, ...]
    b: tuple[int, ...]


@dataclass(frozen=True)
class EvalResult:
    a: tuple[int, ...]
    b: tuple[int, ...]
    cout: int
    clean: bool
    phase_closed: bool
    toffoli: int
    carried_peak: int


def produces(index: int, width: int, cout_present: bool) -> bool:
    return cout_present or index + 1 < width


def n_inner(width: int, cout_present: bool) -> int:
    return width if cout_present else max(0, width - 1)


def current_full(case: Case) -> EvalResult:
    width = case.width
    a = list(case.a)
    b = list(case.b)
    cout = case.cout
    inner: list[int | None] = [None] * n_inner(width, case.cout_present)
    toffoli = 0
    phase_closed = True

    for i in range(width):
        if not produces(i, width, case.cout_present):
            continue
        ci = case.cin if i == 0 and case.cin_present else (inner[i - 1] if i > 0 else None)
        if ci is None:
            co = a[i] & b[i]
        else:
            a[i] ^= ci
            b[i] ^= ci
            co = (a[i] & b[i]) ^ ci
        inner[i] = co
        toffoli += 1

    if case.cout_present:
        cout ^= case.ctrl & int(inner[width - 1])
        toffoli += 1

    clean = True
    for i in range(width - 1, -1, -1):
        ci = case.cin if i == 0 and case.cin_present else (inner[i - 1] if i > 0 else None)
        if not produces(i, width, case.cout_present):
            if ci is not None:
                b[i] ^= ci
            a[i] ^= case.ctrl & b[i]
            if ci is not None:
                b[i] ^= ci
            toffoli += 1
            continue

        co = int(inner[i])
        if ci is not None:
            co ^= ci
        if co != (a[i] & b[i]):
            clean = False
        if i < case.vents:
            # HMR + CZ(a,b) correction: no Toffoli, but the phase receipt must be closed.
            phase_closed = phase_closed and (co == (a[i] & b[i]))
        else:
            toffoli += 1
        co ^= a[i] & b[i]
        if co != 0:
            clean = False
        inner[i] = None

        if ci is not None:
            a[i] ^= ci
        a[i] ^= case.ctrl & b[i]
        if ci is not None:
            b[i] ^= ci
        toffoli += 1

    return EvalResult(
        a=tuple(a),
        b=tuple(b),
        cout=cout,
        clean=clean and all(v is None for v in inner),
        phase_closed=phase_closed,
        toffoli=toffoli,
        carried_peak=n_inner(width, case.cout_present),
    )


def windowed(case: Case, window: int) -> EvalResult:
    width = case.width
    inner_count = n_inner(width, case.cout_present)
    stored_top = min(window, inner_count)
    split = inner_count - stored_top
    a = list(case.a)
    b = list(case.b)
    cout = case.cout
    toffoli = 0
    phase_closed = True
    clean = True

    carry = case.cin if case.cin_present else 0
    for i in range(split):
        a[i] ^= carry
        b[i] ^= carry
        carry = (a[i] & b[i]) ^ carry
        toffoli += 1

    held: dict[int, int] = {}
    for i in range(split, width):
        if not produces(i, width, case.cout_present):
            continue
        ci = carry if i == split else held[i - 1]
        a[i] ^= ci
        b[i] ^= ci
        held[i] = (a[i] & b[i]) ^ ci
        toffoli += 1

    if case.cout_present:
        cout ^= case.ctrl & held[width - 1]
        toffoli += 1

    for i in range(width - 1, split - 1, -1):
        ci = carry if i == split else held[i - 1]
        if not produces(i, width, case.cout_present):
            b[i] ^= ci
            a[i] ^= case.ctrl & b[i]
            b[i] ^= ci
            toffoli += 1
            continue

        co = held.pop(i)
        co ^= ci
        if co != (a[i] & b[i]):
            clean = False
        phase_closed = phase_closed and (co == (a[i] & b[i]))
        co ^= a[i] & b[i]
        if co != 0:
            clean = False
        a[i] ^= ci
        a[i] ^= case.ctrl & b[i]
        b[i] ^= ci
        toffoli += 1

    for i in range(split - 1, -1, -1):
        carry ^= a[i] & b[i]
        a[i] ^= carry
        a[i] ^= case.ctrl & b[i]
        b[i] ^= carry
        toffoli += 2

    expected_carry = case.cin if case.cin_present else 0
    if carry != expected_carry or held:
        clean = False

    return EvalResult(
        a=tuple(a),
        b=tuple(b),
        cout=cout,
        clean=clean,
        phase_closed=phase_closed,
        toffoli=toffoli,
        carried_peak=stored_top,
    )


def bit_tuple(mask: int, width: int) -> tuple[int, ...]:
    return tuple((mask >> i) & 1 for i in range(width))


def iter_cases(max_width: int) -> list[Case]:
    cases: list[Case] = []
    for width in range(1, max_width + 1):
        for cin_present, cout_present in product((False, True), repeat=2):
            for vents in range(0, width + 1):
                for ctrl in (0, 1):
                    for cin in ((0, 1) if cin_present else (0,)):
                        for cout in ((0, 1) if cout_present else (0,)):
                            for a_mask in range(1 << width):
                                a = bit_tuple(a_mask, width)
                                for b_mask in range(1 << width):
                                    cases.append(
                                        Case(
                                            width=width,
                                            cin_present=cin_present,
                                            cout_present=cout_present,
                                            vents=vents,
                                            ctrl=ctrl,
                                            cin=cin,
                                            cout=cout,
                                            a=a,
                                            b=bit_tuple(b_mask, width),
                                        )
                                    )
    return cases


def count_model(width: int, window: int, cout_present: bool, vents: int) -> dict[str, float | int]:
    case = Case(
        width=width,
        cin_present=True,
        cout_present=cout_present,
        vents=vents,
        ctrl=1,
        cin=1,
        cout=0,
        a=tuple(1 for _ in range(width)),
        b=tuple(1 for _ in range(width)),
    )
    full = current_full(case)
    reduced = windowed(case, window)
    return {
        "width": width,
        "window": window,
        "cout": int(cout_present),
        "vents": vents,
        "full_carries": full.carried_peak,
        "windowed_carries": reduced.carried_peak,
        "saved_carries": full.carried_peak - reduced.carried_peak,
        "current_toffoli": full.toffoli,
        "windowed_toffoli": reduced.toffoli,
        "delta_toffoli": reduced.toffoli - full.toffoli,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a reduced-storage threaded-add carry schedule against the current full schedule."
    )
    parser.add_argument("--max-width", type=int, default=5)
    parser.add_argument("--window", type=int, default=3)
    parser.add_argument("--count-width", type=int, default=16)
    parser.add_argument("--count-window", type=int, default=15)
    parser.add_argument("--frontier-qubits", type=int, default=1152)
    parser.add_argument("--frontier-toffoli", type=float, default=1364230.0)
    parser.add_argument("--binding-sites", type=int, default=2617)
    parser.add_argument("--count-table", action="store_true")
    args = parser.parse_args()

    if args.max_width < 1 or args.window < 0 or args.count_width < 1 or args.count_window < 0:
        parser.error("widths and windows must be non-negative, with positive widths")
    if args.frontier_qubits <= 1 or args.binding_sites <= 0:
        parser.error("--frontier-qubits must be >1 and --binding-sites must be positive")

    value_mismatches = 0
    restore_mismatches = 0
    phase_mismatches = 0
    ancilla_mismatches = 0
    toffoli_delta_min: int | None = None
    toffoli_delta_max: int | None = None

    cases = iter_cases(args.max_width)
    for case in cases:
        full = current_full(case)
        reduced = windowed(case, args.window)
        if (full.a, full.b, full.cout) != (reduced.a, reduced.b, reduced.cout):
            value_mismatches += 1
        if full.b != case.b or reduced.b != case.b:
            restore_mismatches += 1
        if not full.phase_closed or not reduced.phase_closed:
            phase_mismatches += 1
        if not full.clean or not reduced.clean:
            ancilla_mismatches += 1
        delta = reduced.toffoli - full.toffoli
        toffoli_delta_min = delta if toffoli_delta_min is None else min(toffoli_delta_min, delta)
        toffoli_delta_max = delta if toffoli_delta_max is None else max(toffoli_delta_max, delta)

    cout_count = count_model(args.count_width, args.count_window, True, args.count_width)
    no_cout_count = count_model(args.count_width, args.count_window, False, args.count_width)
    per_site_delta = int(cout_count["delta_toffoli"])
    total_delta = per_site_delta * args.binding_sites
    break_even_delta = args.frontier_toffoli / (args.frontier_qubits - 1)
    score_positive = int(total_delta <= break_even_delta)

    status = (
        "pass"
        if not value_mismatches
        and not restore_mismatches
        and not phase_mismatches
        and not ancilla_mismatches
        else "fail"
    )
    print(
        "windowed_carry_toy="
        f"{status} evidence_label=Partial max_width={args.max_width} window={args.window} "
        f"cases={len(cases)} value_mismatches={value_mismatches} "
        f"restore_mismatches={restore_mismatches} phase_mismatches={phase_mismatches} "
        f"ancilla_mismatches={ancilla_mismatches} "
        f"toffoli_delta_min={toffoli_delta_min} toffoli_delta_max={toffoli_delta_max} "
        "source_edit_ready=0"
    )
    print(
        "windowed_carry_count "
        f"width={args.count_width} window={args.count_window} cout=1 vents={args.count_width} "
        f"full_carries={cout_count['full_carries']} "
        f"windowed_carries={cout_count['windowed_carries']} "
        f"saved_carries={cout_count['saved_carries']} "
        f"current_toffoli={cout_count['current_toffoli']} "
        f"windowed_toffoli={cout_count['windowed_toffoli']} "
        f"delta_toffoli={cout_count['delta_toffoli']} "
        f"binding_sites={args.binding_sites} total_delta_toffoli={total_delta} "
        f"break_even_delta_toffoli={break_even_delta:.3f} score_positive={score_positive}"
    )
    print(
        "windowed_carry_count "
        f"width={args.count_width} window={args.count_window} cout=0 vents={args.count_width} "
        f"full_carries={no_cout_count['full_carries']} "
        f"windowed_carries={no_cout_count['windowed_carries']} "
        f"saved_carries={no_cout_count['saved_carries']} "
        f"current_toffoli={no_cout_count['current_toffoli']} "
        f"windowed_toffoli={no_cout_count['windowed_toffoli']} "
        f"delta_toffoli={no_cout_count['delta_toffoli']}"
    )
    print(
        "decision=toy-value-restore-phase-ancilla-clean; "
        "naive-window15-cout-count-is-score-negative-at-current-2617-site-bound; "
        "needs-co-residency-reduced-site-count-or-zero-extra-top-carry-vent-before-source-edit"
    )

    if args.count_table:
        print("count_table\twidth\twindow\tcout\tvents\tfull_carries\twindowed_carries\tsaved\tdelta_toffoli")
        for cout_present in (False, True):
            for vents in range(0, args.count_width + 1):
                row = count_model(args.count_width, args.count_window, cout_present, vents)
                print(
                    "count_table"
                    f"\t{row['width']}\t{row['window']}\t{row['cout']}\t{row['vents']}"
                    f"\t{row['full_carries']}\t{row['windowed_carries']}"
                    f"\t{row['saved_carries']}\t{row['delta_toffoli']}"
                )

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
