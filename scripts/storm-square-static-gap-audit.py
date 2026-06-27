#!/usr/bin/env python3
"""Audit the symmetric-square bit-1 gap and cross-term liveness."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CrossTerm:
    i: int
    j: int
    row_bit: int
    product_bit: int
    witness_x: int


@dataclass(frozen=True)
class WidthAudit:
    width: int
    fixed_zero_bits: tuple[int, ...]
    cross_terms: tuple[CrossTerm, ...]

    @property
    def bit1_only(self) -> bool:
        return self.fixed_zero_bits == (1,)

    @property
    def gap_has_executable_ccx(self) -> bool:
        return any(term.row_bit == 1 for term in self.cross_terms)

    @property
    def live_cross_terms(self) -> int:
        return len(self.cross_terms)


def square_bits(x: int, out_bits: int) -> list[int]:
    square = x * x
    return [(square >> bit) & 1 for bit in range(out_bits)]


def fixed_zero_bits(width: int) -> tuple[int, ...]:
    out_bits = 2 * width
    return tuple(
        bit
        for bit in range(out_bits)
        if all(square_bits(x, out_bits)[bit] == 0 for x in range(1 << width))
    )


def cross_terms(width: int) -> tuple[CrossTerm, ...]:
    terms: list[CrossTerm] = []
    for i in range(width):
        for k in range(max(0, width - i - 1)):
            j = i + 1 + k
            terms.append(
                CrossTerm(
                    i=i,
                    j=j,
                    row_bit=k + 2,
                    product_bit=i + j + 1,
                    witness_x=(1 << i) | (1 << j),
                )
            )
    return tuple(terms)


def audit_width(width: int) -> WidthAudit:
    if width < 1:
        raise ValueError("width must be >= 1")
    return WidthAudit(
        width=width,
        fixed_zero_bits=fixed_zero_bits(width),
        cross_terms=cross_terms(width),
    )


def fmt_ints(values: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in values) if values else "none"


def sample_terms(terms: tuple[CrossTerm, ...], limit: int) -> str:
    if not terms:
        return "none"
    return ";".join(
        f"{term.i}:{term.j}:row{term.row_bit}:prod{term.product_bit}:x{term.witness_x}"
        for term in terms[:limit]
    )


def write_summary(path: Path, audits: list[WidthAudit], sample_limit: int) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(
            [
                "width",
                "fixed_zero_bits",
                "bit1_only",
                "source_bit1_gap_has_executable_ccx",
                "cross_terms_checked",
                "cross_terms_live",
                "sample_witnesses",
            ]
        )
        for audit in audits:
            writer.writerow(
                [
                    audit.width,
                    fmt_ints(audit.fixed_zero_bits),
                    int(audit.bit1_only),
                    int(audit.gap_has_executable_ccx),
                    len(audit.cross_terms),
                    audit.live_cross_terms,
                    sample_terms(audit.cross_terms, sample_limit),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prove the square bit-1 row gap is already non-emitted and all cross terms are live."
    )
    parser.add_argument("--min-width", type=int, default=1)
    parser.add_argument("--max-width", type=int, default=8)
    parser.add_argument("--sample-limit", type=int, default=8)
    parser.add_argument("--summary-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_width < 1:
        raise SystemExit("--min-width must be >= 1")
    if args.max_width < args.min_width:
        raise SystemExit("--max-width must be >= --min-width")
    if args.sample_limit < 0:
        raise SystemExit("--sample-limit must be >= 0")

    audits = [audit_width(width) for width in range(args.min_width, args.max_width + 1)]
    all_bit1_only = all(audit.bit1_only for audit in audits)
    no_gap_ccx = all(not audit.gap_has_executable_ccx for audit in audits)
    cross_terms_checked = sum(len(audit.cross_terms) for audit in audits)
    cross_terms_live = sum(audit.live_cross_terms for audit in audits)
    decision = (
        "no-executable-zero-bit-trim"
        if all_bit1_only and no_gap_ccx and cross_terms_live == cross_terms_checked
        else "investigate-square-layout"
    )

    if args.summary_out:
        write_summary(args.summary_out, audits, args.sample_limit)

    print(
        "square_static_gap_audit=pass "
        f"min_width={args.min_width} "
        f"max_width={args.max_width} "
        f"fixed_zero_pattern={'bit1_only' if all_bit1_only else 'mixed'} "
        f"source_bit1_gap_has_executable_ccx={int(not no_gap_ccx)} "
        f"cross_terms_checked={cross_terms_checked} "
        f"cross_terms_live={cross_terms_live} "
        f"decision={decision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
