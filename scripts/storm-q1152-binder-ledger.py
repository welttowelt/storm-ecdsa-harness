#!/usr/bin/env python3
"""Join q1152 ALLOC_NEAR wall rows to binder-specific reducibility facts."""

from __future__ import annotations

import argparse
import collections
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ALLOC_RE = re.compile(
    r"ALLOC_NEAR active=(\d+) .*?phase='([^']*)' ops_idx=(\d+) "
    r"free_pool=(\d+) caller=(\S+)"
)
THREAD_RE = re.compile(
    r"TLM_GIDNEY_THREAD call=(\d+) phase=([^ ]+) width=(\d+) "
    r"cin=(\d+) cout=(\d+) vents=(\d+) ops_start=(\d+) ops_end=(\d+)"
)
MCX_RE = re.compile(
    r"TLM_MCX_INC call=(\d+) phase=([^ ]+) n=(\d+) "
    r"skip_lsb_x=([^ ]+) anc=(\d+) ops_start=(\d+) ops_end=(\d+)"
)


@dataclass(frozen=True)
class AllocRow:
    active: int
    phase: str
    ops_idx: int
    free_pool: int
    caller: str


@dataclass(frozen=True)
class ThreadRow:
    call: int
    phase: str
    width: int
    cin: int
    cout: int
    vents: int
    ops_start: int
    ops_end: int


@dataclass(frozen=True)
class McxRow:
    call: int
    phase: str
    n: int
    skip_lsb_x: str
    anc: int
    ops_start: int
    ops_end: int


@dataclass(frozen=True)
class DeadRange:
    call: int
    lo: int
    hi: int

    @property
    def is_prefix(self) -> bool:
        return self.lo == 0

    @property
    def saved_allocs(self) -> int:
        return self.hi + 1 if self.is_prefix else 0


@dataclass
class BinderSummary:
    rows: int = 0
    peak_rows: int = 0
    ops: set[int] = field(default_factory=set)
    peak_ops: set[int] = field(default_factory=set)
    phases: collections.Counter[str] = field(default_factory=collections.Counter)
    peak_phases: collections.Counter[str] = field(default_factory=collections.Counter)
    min_active: int = 10**9
    max_active: int = 0

    def add(self, row: AllocRow, peak: int) -> None:
        self.rows += 1
        self.ops.add(row.ops_idx)
        self.phases[row.phase] += 1
        self.min_active = min(self.min_active, row.active)
        self.max_active = max(self.max_active, row.active)
        if row.active >= peak:
            self.peak_rows += 1
            self.peak_ops.add(row.ops_idx)
            self.peak_phases[row.phase] += 1


def read_lines(path: Path) -> Iterable[str]:
    try:
        with path.open() as f:
            yield from f
    except FileNotFoundError as exc:
        raise SystemExit(f"input_not_found path={path}") from exc


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError as exc:
        raise SystemExit(f"source_not_found path={path}") from exc


def parse_alloc(line: str) -> AllocRow | None:
    match = ALLOC_RE.search(line)
    if not match:
        return None
    return AllocRow(
        active=int(match.group(1)),
        phase=match.group(2),
        ops_idx=int(match.group(3)),
        free_pool=int(match.group(4)),
        caller=match.group(5),
    )


def parse_thread(line: str) -> ThreadRow | None:
    match = THREAD_RE.search(line)
    if not match:
        return None
    return ThreadRow(
        call=int(match.group(1)),
        phase=match.group(2),
        width=int(match.group(3)),
        cin=int(match.group(4)),
        cout=int(match.group(5)),
        vents=int(match.group(6)),
        ops_start=int(match.group(7)),
        ops_end=int(match.group(8)),
    )


def parse_mcx(line: str) -> McxRow | None:
    match = MCX_RE.search(line)
    if not match:
        return None
    return McxRow(
        call=int(match.group(1)),
        phase=match.group(2),
        n=int(match.group(3)),
        skip_lsb_x=match.group(4),
        anc=int(match.group(5)),
        ops_start=int(match.group(6)),
        ops_end=int(match.group(7)),
    )


def parse_dead_ranges(source: Path, name: str) -> list[DeadRange]:
    text = read_text(source)
    start = text.find(name)
    if start < 0:
        raise SystemExit(f"dead_range_table_not_found table={name}")
    end = text.find("];", start)
    if end < 0:
        raise SystemExit(f"dead_range_table_unclosed table={name}")
    ranges: list[DeadRange] = []
    for call, lo, hi in re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", text[start:end]):
        ranges.append(DeadRange(int(call), int(lo), int(hi)))
    return ranges


def prefix_by_call(ranges: Iterable[DeadRange]) -> dict[int, DeadRange]:
    prefixes: dict[int, DeadRange] = {}
    for dead_range in ranges:
        if not dead_range.is_prefix:
            continue
        current = prefixes.get(dead_range.call)
        if current is None or dead_range.hi > current.hi:
            prefixes[dead_range.call] = dead_range
    return prefixes


def parse_trace(
    path: Path, peak: int
) -> tuple[int, int, int, dict[int, ThreadRow], dict[int, McxRow], dict[str, BinderSummary], dict[int, list[AllocRow]]]:
    alloc_rows = 0
    thread_rows = 0
    mcx_rows = 0
    threads_by_start: dict[int, ThreadRow] = {}
    mcx_by_start: dict[int, McxRow] = {}
    summaries: dict[str, BinderSummary] = collections.defaultdict(BinderSummary)
    rows_by_ops: dict[int, list[AllocRow]] = collections.defaultdict(list)
    for raw_line in read_lines(path):
        line = raw_line.rstrip("\r\n")
        thread = parse_thread(line)
        if thread is not None:
            thread_rows += 1
            threads_by_start[thread.ops_start] = thread
            continue
        mcx = parse_mcx(line)
        if mcx is not None:
            mcx_rows += 1
            mcx_by_start[mcx.ops_start] = mcx
            continue
        alloc = parse_alloc(line)
        if alloc is None:
            continue
        alloc_rows += 1
        summaries[alloc.caller].add(alloc, peak)
        rows_by_ops[alloc.ops_idx].append(alloc)
    return alloc_rows, thread_rows, mcx_rows, threads_by_start, mcx_by_start, summaries, rows_by_ops


def phase_top(counter: collections.Counter[str]) -> str:
    if not counter:
        return ""
    return counter.most_common(1)[0][0]


def csv_join_ints(values: Iterable[int]) -> str:
    return ",".join(str(value) for value in sorted(values))


def csv_join_strs(values: Iterable[str]) -> str:
    return ",".join(sorted(values))


def write_summary(
    path: Path,
    summaries: dict[str, BinderSummary],
    gidney_threads: dict[int, ThreadRow],
    mcx_rows: dict[int, McxRow],
    gidney_prefixes: dict[int, DeadRange],
    peak: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "caller",
                "rows",
                "peak_rows",
                "ops",
                "peak_ops",
                "min_active",
                "max_active",
                "phase_top",
                "peak_phase_top",
                "binding_calls",
                "prefix_dead_binding_calls",
                "prefix_saved_allocs",
                "mcx_n_values",
                "mcx_anc_values",
                "mcx_skip_lsb_x_values",
                "dead_mechanism",
            ]
        )
        for caller, summary in sorted(summaries.items(), key=lambda item: (-item[1].peak_rows, item[0])):
            binding_calls: set[int] = set()
            prefix_calls: set[int] = set()
            saved_allocs = 0
            mcx_n_values: set[int] = set()
            mcx_anc_values: set[int] = set()
            mcx_skip_lsb_x_values: set[str] = set()
            dead_mechanism = ""
            if caller.endswith("gidney.rs:1217"):
                dead_mechanism = "gidney_thread_forward_prefix"
                for ops_idx in summary.peak_ops:
                    thread = gidney_threads.get(ops_idx)
                    if thread is None:
                        continue
                    binding_calls.add(thread.call)
                    prefix = gidney_prefixes.get(thread.call)
                    if prefix is not None:
                        prefix_calls.add(thread.call)
                        saved_allocs += prefix.saved_allocs
            elif caller.endswith("mcx.rs:318"):
                dead_mechanism = "none_kg_prefix_ancilla"
                for ops_idx in summary.peak_ops:
                    mcx = mcx_rows.get(ops_idx)
                    if mcx is None:
                        continue
                    binding_calls.add(mcx.call)
                    mcx_n_values.add(mcx.n)
                    mcx_anc_values.add(mcx.anc)
                    mcx_skip_lsb_x_values.add(mcx.skip_lsb_x)
            writer.writerow(
                [
                    caller,
                    summary.rows,
                    summary.peak_rows,
                    len(summary.ops),
                    len(summary.peak_ops),
                    "" if summary.rows == 0 else summary.min_active,
                    summary.max_active,
                    phase_top(summary.phases),
                    phase_top(summary.peak_phases),
                    csv_join_ints(binding_calls),
                    csv_join_ints(prefix_calls),
                    saved_allocs,
                    csv_join_ints(mcx_n_values),
                    csv_join_ints(mcx_anc_values),
                    csv_join_strs(mcx_skip_lsb_x_values),
                    dead_mechanism,
                ]
            )


def decide(
    gidney_peak_ops: set[int],
    gidney_unmatched: int,
    gidney_prefix_calls: set[int],
    mcx_peak_ops: set[int],
) -> str:
    if gidney_peak_ops and gidney_unmatched:
        return "need-gidney-call-trace"
    if gidney_prefix_calls and mcx_peak_ops:
        return "coordinated-cut-requires-mcx-replacement"
    if gidney_prefix_calls:
        return "gidney-prefix-binding-coordinated-gate"
    if mcx_peak_ops:
        return "nack-gidney-not-prefix-or-mcx-floor"
    return "no-q1152-gidney-mcx-binding"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True, help="stderr trace with ALLOC_NEAR and optional TLM_GIDNEY_THREAD rows")
    parser.add_argument("--gidney-source", type=Path, required=True, help="trailmix_ludicrous/gidney.rs source")
    parser.add_argument("--peak", type=int, default=1152, help="active-qubit wall threshold")
    parser.add_argument("--summary-out", type=Path, help="optional caller-level TSV output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ranges = parse_dead_ranges(args.gidney_source, "GIDNEY_THREAD_FWD_DEAD_RANGES")
    prefixes = prefix_by_call(ranges)
    alloc_rows, thread_rows, mcx_trace_rows, threads_by_start, mcx_by_start, summaries, _rows_by_ops = parse_trace(
        args.trace, args.peak
    )

    gidney = summaries.get("src/point_add/trailmix_ludicrous/gidney.rs:1217", BinderSummary())
    mcx_summary = summaries.get("src/point_add/trailmix_ludicrous/mcx.rs:318", BinderSummary())
    gidney_binding_calls: set[int] = set()
    gidney_prefix_calls: set[int] = set()
    gidney_unmatched = 0
    gidney_saved_allocs = 0
    mcx_binding_calls: set[int] = set()
    mcx_unmatched = 0
    mcx_n_values: set[int] = set()
    mcx_anc_values: set[int] = set()
    for ops_idx in gidney.peak_ops:
        thread = threads_by_start.get(ops_idx)
        if thread is None:
            gidney_unmatched += 1
            continue
        gidney_binding_calls.add(thread.call)
        prefix = prefixes.get(thread.call)
        if prefix is not None:
            gidney_prefix_calls.add(thread.call)
            gidney_saved_allocs += prefix.saved_allocs
    for ops_idx in mcx_summary.peak_ops:
        mcx_row = mcx_by_start.get(ops_idx)
        if mcx_row is None:
            mcx_unmatched += 1
            continue
        mcx_binding_calls.add(mcx_row.call)
        mcx_n_values.add(mcx_row.n)
        mcx_anc_values.add(mcx_row.anc)

    if args.summary_out:
        write_summary(args.summary_out, summaries, threads_by_start, mcx_by_start, prefixes, args.peak)

    decision = decide(gidney.peak_ops, gidney_unmatched, gidney_prefix_calls, mcx_summary.peak_ops)
    print(
        "q1152_binder_ledger=pass "
        f"alloc_rows={alloc_rows} thread_rows={thread_rows} mcx_trace_rows={mcx_trace_rows} peak={args.peak} "
        f"gidney_peak_ops={len(gidney.peak_ops)} gidney_peak_rows={gidney.peak_rows} "
        f"gidney_binding_calls={len(gidney_binding_calls)} gidney_unmatched_peak_ops={gidney_unmatched} "
        f"gidney_prefix_dead_binding_calls={len(gidney_prefix_calls)} gidney_prefix_saved_allocs={gidney_saved_allocs} "
        f"mcx_peak_ops={len(mcx_summary.peak_ops)} mcx_peak_rows={mcx_summary.peak_rows} "
        f"mcx_binding_calls={len(mcx_binding_calls)} mcx_unmatched_peak_ops={mcx_unmatched} "
        f"mcx_n_values={csv_join_ints(mcx_n_values) or 'none'} mcx_anc_values={csv_join_ints(mcx_anc_values) or 'none'} "
        "mcx_dead_mechanism=0 "
        f"decision={decision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
