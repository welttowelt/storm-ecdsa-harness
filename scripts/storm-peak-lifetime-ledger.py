#!/usr/bin/env python3
"""Build a peak-lifetime ledger from raw ALLOC_NEAR trace rows."""

from __future__ import annotations

import argparse
import collections
import csv
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


CallerKey = tuple[str, str]
PhaseKey = tuple[str, str, str]


@dataclass
class AllocRow:
    active: int
    phase: str
    ops_idx: int
    caller_file: str
    caller_line: str


@dataclass
class LifetimeSummary:
    near_peak_allocs: int = 0
    peak_allocs: int = 0
    min_active: int = 10**9
    max_active: int = 0
    phases: collections.Counter[str] = field(default_factory=collections.Counter)
    peak_phases: collections.Counter[str] = field(default_factory=collections.Counter)
    peak_ops: set[int] = field(default_factory=set)

    def add(self, row: AllocRow, peak: int) -> None:
        self.near_peak_allocs += 1
        self.min_active = min(self.min_active, row.active)
        self.max_active = max(self.max_active, row.active)
        self.phases[row.phase] += 1
        if row.active >= peak:
            self.peak_allocs += 1
            self.peak_phases[row.phase] += 1
            self.peak_ops.add(row.ops_idx)

    @property
    def binds_peak(self) -> int:
        return 1 if self.peak_allocs else 0

    @property
    def peak_ops_min(self) -> str:
        return str(min(self.peak_ops)) if self.peak_ops else ""

    @property
    def peak_ops_max(self) -> str:
        return str(max(self.peak_ops)) if self.peak_ops else ""

    @property
    def peak_ops_span(self) -> str:
        if not self.peak_ops:
            return ""
        return str(max(self.peak_ops) - min(self.peak_ops))


def read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open() as f:
            yield from f
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def field_after(line: str, name: str) -> str | None:
    marker = f"{name}="
    start = line.find(marker)
    if start < 0:
        return None
    value_start = start + len(marker)
    if value_start < len(line) and line[value_start] == "'":
        value_end = line.find("'", value_start + 1)
        if value_end < 0:
            return None
        return line[value_start + 1 : value_end]
    value_end = line.find(" ", value_start)
    if value_end < 0:
        value_end = len(line)
    return line[value_start:value_end]


def caller_key(raw: str) -> CallerKey:
    file_name, sep, line = raw.rpartition(":")
    if sep and line.isdigit():
        return file_name, line
    return raw, ""


def parse_alloc_row(line: str) -> AllocRow | None:
    line = line.rstrip("\r\n")
    if not line.startswith("ALLOC_NEAR"):
        return None
    active = field_after(line, "active")
    phase = field_after(line, "phase")
    ops_idx = field_after(line, "ops_idx")
    caller = field_after(line, "caller")
    if not active or not phase or not ops_idx or not caller:
        return None
    try:
        active_int = int(active)
        ops_idx_int = int(ops_idx)
    except ValueError:
        return None
    caller_file, caller_line = caller_key(caller)
    return AllocRow(
        active=active_int,
        phase=phase,
        ops_idx=ops_idx_int,
        caller_file=caller_file,
        caller_line=caller_line,
    )


def top_counter_key(counter: collections.Counter[str]) -> str:
    if not counter:
        return ""
    return counter.most_common(1)[0][0]


def parse_alloc_rows(
    path: Path, peak: int
) -> tuple[
    int,
    collections.Counter[int],
    collections.Counter[int],
    dict[CallerKey, LifetimeSummary],
    dict[PhaseKey, LifetimeSummary],
]:
    input_rows = 0
    active_counts: collections.Counter[int] = collections.Counter()
    peak_ops_allocs: collections.Counter[int] = collections.Counter()
    caller_summaries: dict[CallerKey, LifetimeSummary] = collections.defaultdict(LifetimeSummary)
    phase_summaries: dict[PhaseKey, LifetimeSummary] = collections.defaultdict(LifetimeSummary)
    for line in read_lines(path):
        row = parse_alloc_row(line)
        if row is None:
            continue
        input_rows += 1
        active_counts[row.active] += 1
        caller_key_tuple = (row.caller_file, row.caller_line)
        phase_key_tuple = (row.caller_file, row.caller_line, row.phase)
        caller_summaries[caller_key_tuple].add(row, peak)
        phase_summaries[phase_key_tuple].add(row, peak)
        if row.active >= peak:
            peak_ops_allocs[row.ops_idx] += 1
    return input_rows, active_counts, peak_ops_allocs, caller_summaries, phase_summaries


def sort_lifetime_summary(item: tuple[CallerKey, LifetimeSummary]) -> tuple[int, int, str, int]:
    (file_name, line), summary = item
    try:
        line_int = int(line)
    except ValueError:
        line_int = 0
    return (-summary.peak_allocs, -summary.near_peak_allocs, file_name, line_int)


def sort_phase_summary(item: tuple[PhaseKey, LifetimeSummary]) -> tuple[int, int, str, int, str]:
    (file_name, line, phase), summary = item
    try:
        line_int = int(line)
    except ValueError:
        line_int = 0
    return (-summary.peak_allocs, -summary.near_peak_allocs, file_name, line_int, phase)


def write_caller_summary(path: Path, rows: list[tuple[CallerKey, LifetimeSummary]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "caller_file",
                "caller_line",
                "phase_top",
                "near_peak_allocs",
                "peak_allocs",
                "distinct_peak_ops",
                "peak_ops_min",
                "peak_ops_max",
                "peak_ops_span",
                "min_active",
                "max_active",
                "binds_peak",
                "peak_phase_top",
            ]
        )
        for (file_name, line), summary in selected:
            writer.writerow(
                [
                    file_name,
                    line,
                    top_counter_key(summary.phases),
                    summary.near_peak_allocs,
                    summary.peak_allocs,
                    len(summary.peak_ops),
                    summary.peak_ops_min,
                    summary.peak_ops_max,
                    summary.peak_ops_span,
                    summary.min_active,
                    summary.max_active,
                    summary.binds_peak,
                    top_counter_key(summary.peak_phases),
                ]
            )


def write_phase_summary(path: Path, rows: list[tuple[PhaseKey, LifetimeSummary]], limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = rows[:limit] if limit else rows
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "caller_file",
                "caller_line",
                "phase",
                "near_peak_allocs",
                "peak_allocs",
                "distinct_peak_ops",
                "min_active",
                "max_active",
                "binds_peak",
            ]
        )
        for (file_name, line, phase), summary in selected:
            writer.writerow(
                [
                    file_name,
                    line,
                    phase,
                    summary.near_peak_allocs,
                    summary.peak_allocs,
                    len(summary.peak_ops),
                    summary.min_active,
                    summary.max_active,
                    summary.binds_peak,
                ]
            )


def write_active_summary(path: Path, active_counts: collections.Counter[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["active", "allocs"])
        for active in sorted(active_counts, reverse=True):
            writer.writerow([active, active_counts[active]])


def format_number(value: float | int | str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if value.is_integer():
        return str(int(value))
    return f"{value:.1f}"


def peak_ops_metric(counter: collections.Counter[int], reducer: str) -> str:
    if not counter:
        return "0"
    values = list(counter.values())
    if reducer == "min":
        return str(min(values))
    if reducer == "max":
        return str(max(values))
    if reducer == "median":
        return format_number(statistics.median(values))
    raise ValueError(reducer)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="raw ALLOC_NEAR trace")
    parser.add_argument("--caller-out", type=Path, required=True, help="caller-level TSV ledger")
    parser.add_argument("--phase-out", type=Path, required=True, help="caller+phase TSV ledger")
    parser.add_argument("--active-out", type=Path, help="active-count TSV ledger")
    parser.add_argument("--peak", type=int, default=1152, help="active allocation threshold for binding wall")
    parser.add_argument("--limit", type=int, default=0, help="maximum emitted caller/phase rows")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_rows, active_counts, peak_ops_allocs, caller_summaries, phase_summaries = parse_alloc_rows(
        args.input, args.peak
    )
    caller_rows = sorted(caller_summaries.items(), key=sort_lifetime_summary)
    phase_rows = sorted(phase_summaries.items(), key=sort_phase_summary)
    write_caller_summary(args.caller_out, caller_rows, args.limit)
    write_phase_summary(args.phase_out, phase_rows, args.limit)
    if args.active_out:
        write_active_summary(args.active_out, active_counts)
    peak_allocs = sum(peak_ops_allocs.values())
    active_min = min(active_counts) if active_counts else 0
    active_max = max(active_counts) if active_counts else 0
    print(
        "peak_lifetime_ledger=pass "
        f"input_rows={input_rows} active_min={active_min} active_max={active_max} "
        f"peak={args.peak} peak_allocs={peak_allocs} peak_ops={len(peak_ops_allocs)} "
        f"peak_ops_allocs_min={peak_ops_metric(peak_ops_allocs, 'min')} "
        f"peak_ops_allocs_max={peak_ops_metric(peak_ops_allocs, 'max')} "
        f"peak_ops_allocs_median={peak_ops_metric(peak_ops_allocs, 'median')} "
        f"caller_rows={len(caller_rows)} phase_rows={len(phase_rows)} "
        f"caller_out={args.caller_out} phase_out={args.phase_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
